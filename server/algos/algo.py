from datetime import datetime
from typing import Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from server.database import UserAlgorithm, Post, post_user_algorithm_association

CURSOR_EOF = 'eof'

def get_posts(db: Session, algo: UserAlgorithm, cursor: Optional[str], limit: int) -> dict:
    # Initialize the query to fetch posts associated with the specific UserAlgorithm
    posts_query = (
        db.query(Post)
        .join(post_user_algorithm_association, Post.id == post_user_algorithm_association.c.post_id)
        .filter(post_user_algorithm_association.c.user_algorithm_id == algo.id)
    )

    # Apply cursor-based pagination if a cursor is provided
    if cursor:
        if cursor == CURSOR_EOF:
            return {
                'cursor': CURSOR_EOF,
                'feed': []
            }
        cursor_parts = cursor.split('::')
        if len(cursor_parts) != 2:
            raise ValueError('Malformed cursor')

        indexed_at, cid = cursor_parts
        indexed_at = datetime.fromtimestamp(int(indexed_at) / 1000)

        # Add filtering for cursor-based pagination before limit
        posts_query = posts_query.filter(
            or_(
                and_(Post.indexed_at == indexed_at, Post.cid < cid),
                Post.indexed_at < indexed_at
            )
        )

    # Apply ordering and limit after filtering
    posts_query = posts_query.order_by(Post.indexed_at.desc(), Post.cid.desc()).limit(limit)

    # Execute the query and fetch results
    posts = posts_query.all()

    # Build the feed response
    feed = [{'post': post.uri} for post in posts]

    # Update the cursor
    cursor = CURSOR_EOF
    last_post = posts[-1] if posts else None
    if last_post:
        cursor = f'{int(last_post.indexed_at.timestamp() * 1000)}::{last_post.cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
