import json
from collections import defaultdict

from atproto import models

from server.logger import logger

def operations_callback(ops: defaultdict) -> None:
    # Here we can filter, process, run ML classification, etc.
    # After our feed alg we can save posts into our DB
    # Also, we should process deleted posts to remove them from our DB and keep it in sync

    # for example, let's create our custom feed that will contain all posts that contains alf related text
    return None
    posts_to_create = []
    for created_post in ops[models.ids.AppBskyFeedPost]['created']:
        logger.info(f"CREATE {created_post}")
    for deleted_post in ops[models.ids.AppBskyFeedPost]['deleted']:
        logger.info(f"DELETE {deleted_post}")
        # Enqueue a job with the JSON object record
        # record_json = {"id": 123, "content": "Sample record data"}
        # 
        # print(f"Enqueued job {job.id}")
        
        # author = created_post['author']
        # record = created_post['record']
        #
        # # print all texts just as demo that data stream works
        # post_with_images = isinstance(record.embed, models.AppBskyEmbedImages.Main)
        # inlined_text = record.text.replace('\n', ' ')
        # # only alf-related posts
        # if algo_manager.record_matches_algo(record):
        #     logger.info(
        #         f'NEW POST '
        #         f'[CREATED_AT={record.created_at}]'
        #         f'[AUTHOR={author}]'
        #         f'[WITH_IMAGE={post_with_images}]'
        #         f': {inlined_text}'
        #     )
        #     reply_root = reply_parent = None
        #     if record.reply:
        #         reply_root = record.reply.root.uri
        #         reply_parent = record.reply.parent.uri
        #
        #     post_dict = {
        #         'uri': created_post['uri'],
        #         'cid': created_post['cid'],
        #         'reply_parent': reply_parent,
        #         'reply_root': reply_root,
        #     }
        #     posts_to_create.append(post_dict)

    # posts_to_delete = ops[models.ids.AppBskyFeedPost]['deleted']
    # if posts_to_delete:
    #     post_uris_to_delete = [post['uri'] for post in posts_to_delete]
    #     Post.delete().where(Post.uri.in_(post_uris_to_delete))
    #     # logger.info(f'Deleted from feed: {len(post_uris_to_delete)}')
    #
    # if posts_to_create:
    #     with db.atomic():
    #         for post_dict in posts_to_create:
    #             Post.create(**post_dict)
    #     logger.info(f'Added to feed: {len(posts_to_create)}')
