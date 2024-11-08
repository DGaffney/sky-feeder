from datetime import datetime

import peewee

db = peewee.SqliteDatabase('feed_database.db')


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Post(BaseModel):
    uri = peewee.CharField(index=True)
    cid = peewee.CharField()
    reply_parent = peewee.CharField(null=True, default=None)
    reply_root = peewee.CharField(null=True, default=None)
    indexed_at = peewee.DateTimeField(default=datetime.utcnow)


class SubscriptionState(BaseModel):
    service = peewee.CharField(unique=True)
    cursor = peewee.IntegerField()

class UserAlgorithm(BaseModel):
    user_id = peewee.CharField()
    algo_uri = peewee.CharField()
    manifest = peewee.TextField()      # Store the JSON manifest as a string
    version_hash = peewee.CharField()   # Hash to track version changes

    class Meta:
        indexes = (
            (('user_id', 'algo_uri'), True),  # unique constraint on user_id and algo_uri
        )



if db.is_closed():
    db.connect()
    db.create_tables([Post, SubscriptionState])
