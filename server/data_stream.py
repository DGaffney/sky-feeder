from collections import defaultdict

from rq import Queue
from redis import Redis
from atproto import AtUri, CAR, firehose_models, FirehoseSubscribeReposClient, models, parse_subscribe_repos_message
from atproto.exceptions import FirehoseError

from server.database import SessionLocal, SubscriptionState

from server.logger import logger
from algo_matcher import match_algo, delete_record
# Connect to Redis
redis_conn = Redis.from_url("redis://redis:6379/0")
queue = Queue("algo_matcher", connection=redis_conn)
db = SessionLocal()
STOPGAP_QUEUE_DEPTH_THRESHOLD = 50000

_INTERESTED_RECORDS = {
    # models.AppBskyFeedLike: modelsx.ids.AppBskyFeedLike,
    models.AppBskyFeedPost: models.ids.AppBskyFeedPost,
    # models.AppBskyGraphFollow: models.ids.AppBskyGraphFollow,
}


def _get_ops_by_type(commit: models.ComAtprotoSyncSubscribeRepos.Commit) -> defaultdict:
    operation_by_type = defaultdict(lambda: {'created': [], 'deleted': []})

    car = CAR.from_bytes(commit.blocks)
    for op in commit.ops:
        if op.action == 'update':
            # we are not interested in updates
            continue

        uri = AtUri.from_str(f'at://{commit.repo}/{op.path}')

        if op.action == 'create':
            if not op.cid:
                continue

            create_info = {'uri': str(uri), 'cid': str(op.cid), 'author': commit.repo}
            # try:
            #     redis_conn.sadd("bluesky_user_dids", create_info["author"])
            # except:
            #     logger.info("SADD Fails for momentary read-only issue")
            record_raw_data = car.blocks.get(op.cid)
            if not record_raw_data:
                continue
            record = models.get_or_create(record_raw_data, strict=False)
            for record_type, record_nsid in _INTERESTED_RECORDS.items():
                if uri.collection == record_nsid and models.is_record_type(record, record_type):
                    operation_by_type[record_nsid]['created'].append({'record': record, **create_info})
                    if queue.count < STOPGAP_QUEUE_DEPTH_THRESHOLD:
                        job = queue.enqueue(match_algo, {'record': record_raw_data, 'create_info': create_info})
                    break

        if op.action == 'delete':
            operation_by_type[uri.collection]['deleted'].append({'uri': str(uri)})
            job = queue.enqueue(delete_record, {'uri': str(uri)})

    return operation_by_type


def run(name, operations_callback, stream_stop_event=None):
    while stream_stop_event is None or not stream_stop_event.is_set():
        try:
            _run(name, operations_callback, stream_stop_event)
        except FirehoseError as e:
            # here we can handle different errors to reconnect to firehose
            raise e


def _run(name, operations_callback, stream_stop_event=None):
    db = SessionLocal()
    state = db.query(SubscriptionState).filter(SubscriptionState.service == name).first()

    params = None
    if state:
        params = models.ComAtprotoSyncSubscribeRepos.Params(cursor=state.cursor)

    client = FirehoseSubscribeReposClient(params)

    if not state:
        sub_state = SubscriptionState(service=name, cursor=0)
        db.add(sub_state)
        db.commit()

    def on_message_handler(message: firehose_models.MessageFrame) -> None:
        # stop on next message if requested
        if stream_stop_event and stream_stop_event.is_set():
            client.stop()
            db.close()
            return

        commit = parse_subscribe_repos_message(message)
        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        # update stored state every ~20 events
        if commit.seq % 20 == 0:
            # logger.info(f'Updated cursor for {name} to {commit.seq}')
            client.update_params(models.ComAtprotoSyncSubscribeRepos.Params(cursor=commit.seq))
            sub_state = db.query(SubscriptionState).filter(SubscriptionState.service == name).first()
            sub_state.cursor = commit.seq
            db.commit()
        if not commit.blocks:
            return

        operations_callback(_get_ops_by_type(commit))

    client.start(on_message_handler)
