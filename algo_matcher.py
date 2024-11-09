import os
import logging
import json
import redis
from rq import Queue, Worker, get_current_job
from atproto import models
from server.logger import logger
from server.algos.manager import AlgoManager
from server.database import SessionLocal, UserAlgorithm, Post
from server.algos.shared_model_store import SharedModelStore


# Configure Redis connection
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_conn = redis.from_url(redis_url)

# Initialize RQ queue
queue = Queue("algo_matcher", connection=redis_conn)
# Load the AlgoManager, assuming it takes in a user-specific manifest
def algo_matches(user_algorithm, record):
    algo_manager = AlgoManager(user_algorithm.algo_manifest)
    return algo_manager.record_matches_algo(record)

def match_algo(record_data):
    """
    Process a JSON object record through the algorithms.
    
    Args:
        record_data (dict): JSON object to process.
    """
    any_matches = False
    match_ids = []
    # Use a context manager for database session to ensure proper closing
    with SessionLocal() as db:
        for user_algorithm in db.query(UserAlgorithm).all():
            record = models.get_or_create(record_data["record"], strict=False)
            if algo_matches(user_algorithm, record):
                any_matches = True
                match_ids.append(user_algorithm.id)
        if any_matches:
            post_dict = {
                'uri': record_data['create_info']['uri'],
                'cid': record_data['create_info']['cid'],
                'author': record_data['create_info']['author'],
                'reply_parent': record.reply.parent.uri if record.reply else None,
                'reply_root': record.reply.root.uri if record.reply else None,
            }
            logger.info(f"Post dict is {post_dict}, matches are {match_ids}")
            post = db.query(Post).filter_by(uri=post_dict['uri']).first()
            if not post:
                post = Post(**post_dict)
                db.add(post)
                db.commit()
                db.refresh(post)
            # Associate the post with each matching UserAlgorithm
            for algo_id in match_ids:
                user_algorithm = db.query(UserAlgorithm).get(algo_id)
                if user_algorithm:
                    post.algorithms.append(user_algorithm)
            
            # Commit all associations
            db.commit()
            logger.info(f"Post created with URI {post.uri}, associated with algorithms {match_ids}")
    return {"matches": match_ids}

def delete_record(record_data):
    """
    Delete a record from the feeds
    
    Args:
        record_data (dict): JSON object to process.
    """
    # Run the record through algo_manager
    return True

if __name__ == "__main__":
    with redis_conn:
        worker = Worker(["algo_matcher"], connection=redis_conn)
        worker.work()
