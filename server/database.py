import os
from datetime import datetime
from sqlalchemy import (
    create_engine, func, Column, String, DateTime, BigInteger, Integer, ForeignKey, Table, Text, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

from server.bluesky_api import BlueskyAPI

# Configure the database connection
DATABASE_URL = os.getenv("DATABASE_URL")
# Set up the database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base model
Base = declarative_base()

# Many-to-many association table between Post and UserAlgorithm
post_user_algorithm_association = Table(
    'post_user_algorithm', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('user_algorithm_id', Integer, ForeignKey('user_algorithms.id'), primary_key=True),
    UniqueConstraint('post_id', 'user_algorithm_id', name='uix_post_user_algorithm')
)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, index=True)
    cid = Column(String)
    author = Column(String)
    reply_parent = Column(String, nullable=True, default=None)
    reply_root = Column(String, nullable=True, default=None)
    indexed_at = Column(DateTime, default=datetime.utcnow)

    # Many-to-many relationship with UserAlgorithm
    algorithms = relationship("UserAlgorithm", secondary=post_user_algorithm_association, back_populates="posts")


class SubscriptionState(Base):
    __tablename__ = 'subscription_states'

    id = Column(Integer, primary_key=True)
    service = Column(String, unique=True)
    cursor = Column(BigInteger)


class SearchFacet(Base):
    __tablename__ = 'search_facets'
    user_collection_type = "user_collection"

    id = Column(Integer, primary_key=True)
    facet_name = Column(String)
    facet_parameters = Column(JSONB)
    facet_hash = Column(String)
    facet_value = Column(JSONB)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UserAlgorithm(Base):
    __tablename__ = 'user_algorithms'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    algo_uri = Column(String)
    algo_manifest = Column(JSONB)
    version_hash = Column(String)
    record_name = Column(String)
    display_name = Column(String)
    description = Column(String)
    feed_did = Column(String)

    # Many-to-many relationship with Post
    posts = relationship("Post", secondary=post_user_algorithm_association, back_populates="algorithms")

    __table_args__ = (
        UniqueConstraint('user_id', 'algo_uri', name='uix_user_algo_uri'),
    )
    def publish_feed(self, username, password, session_string, record_name, display_name, description):
        return BlueskyAPI(username, password, session_string).publish_feed(record_name, display_name, description)

    def delete_feed(self, username, password, session_string):
        deleted_feed = BlueskyAPI(username, password, session_string).delete_feed(self.algo_uri)

    def update_feed(self, username, password, session_string):
        return BlueskyAPI(username, password, session_string).publish_feed(self.record_name, self.display_name, self.description, self.feed_did)


# Initialize the database tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency: create a new session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

