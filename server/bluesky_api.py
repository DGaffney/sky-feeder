import re
from atproto import Client, models

from atproto_client.models.app.bsky.embed.external import ViewExternal

class BlueskyAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = Client()
        self.client.login(self.username, self.password)

    def get_client_feeds(self):
        return self.client.com.atproto.repo.list_records({"collection": models.ids.AppBskyFeedGenerator, "repo": self.client.me.did})

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

