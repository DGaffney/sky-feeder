import os
import re
from atproto import Client, models, AtUri

from atproto_client.models.app.bsky.embed.external import ViewExternal

from server.logger import logger
HOSTNAME = os.getenv("HOSTNAME")
class BlueskyAPI:
    def __init__(self, username, password, session_string=None):
        self.username = username
        self.password = password
        self.client = Client()
        if not self.session_string:
            self.client.login(self.username, self.password)
            self.session_string = client.export_session_string()
        else:
            client.login(session_string=session_string)
            self.session_string = client.export_session_string()
    
    def get_client_feeds(self):
        #needs cursoring/pagination
        return self.client.com.atproto.repo.list_records({"collection": models.ids.AppBskyFeedGenerator, "repo": self.client.me.did})
    
    def publish_feed(self, record_name, display_name, description, feed_did=f'did:web:{HOSTNAME}'):
        logger.info(f"calling publish_feed on {record_name} {display_name} {description} {feed_did}")
        response = self.client.com.atproto.repo.put_record(models.ComAtprotoRepoPutRecord.Data(
            repo=self.client.me.did,
            collection=models.ids.AppBskyFeedGenerator,
            rkey=record_name,
            record=models.AppBskyFeedGenerator.Record(
                did=feed_did,
                display_name=display_name,
                description=description,
                avatar=None,
                created_at=self.client.get_current_time_iso(),
            )
        ))
        return [response, feed_did]
    
    def delete_feed(self, algo_uri):
        return self.client.app.bsky.feed.generator.delete(self.client.me.did, AtUri.from_str(algo_uri).rkey)
    
    def get_all_follows(self, actor_handle):
        cursor = None
        follows = []
        while True:
            response = self.client.app.bsky.graph.get_follows({"actor": actor_handle, "cursor": cursor, "limit": 100})
            follows.extend(response.follows)
            if not response.cursor:
                break
            cursor = response.cursor
        return follows

    def get_all_follower_dids(self, actor_handle):
        cursor = None
        followers = []
        while True:
            response = self.client.app.bsky.graph.get_followers({"actor": actor_handle, "cursor": cursor, "limit": 100})
            followers.extend(response.followers)
            if not response.cursor:
                break
            cursor = response.cursor
        return followers

def is_app_passwordy(s: str) -> bool:
    """
    Determines if a string matches the pattern with four 4-character segments separated by dashes.
    """
    if len(s) != 19:  # Check total length
        return False
    if s.count('-') != 3:  # Check the number of dashes
        return False
    # Check the pattern with a regular expression
    pattern = r'^[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$'
    return bool(re.match(pattern, s))

