from collections import Counter
import json
import random
from multiprocessing import get_context, Process
import redis
from server.bluesky_api import BlueskyAPI

# Initialize Redis connection
r = redis.Redis(host='redis', port=6379, db=0)

# Load initial user_dids and populate Redis hash
user_dids = Counter(json.loads(open("bluesky_user_dids.json").read()))
user_did_list = list(user_dids.keys())
random.shuffle(user_did_list)

# Redis key for user DID counts
redis_key = "user_dids"
#r.delete(redis_key)
#for did, count in user_dids.items():
#    _ = r.hincrby(redis_key, did, count)

# Define a function to create a new client instance
def create_client_instance():
    return BlueskyAPI("devingaffney.com", "uab7-jt2t-pape-izqh", 'devingaffney.com:::did:plc:jijwtzgroy76samnivlqrpec:::eyJ0eXAiOiJhdCtqd3QiLCJhbGciOiJFUzI1NksifQ.eyJzY29wZSI6ImNvbS5hdHByb3RvLmFwcFBhc3MiLCJzdWIiOiJkaWQ6cGxjOmppand0emdyb3k3NnNhbW5pdmxxcnBlYyIsImlhdCI6MTczMTM0Mjk0NywiZXhwIjoxNzMxMzUwMTQ3LCJhdWQiOiJkaWQ6d2ViOnBvcmNpbmkudXMtZWFzdC5ob3N0LmJza3kubmV0d29yayJ9.wRqtQ5VfjDAenQD3zoNnuw3xKYI-g50s-s8e0eH6CLH8WSR192ZL8z8SrTK-g4w6ejQXfj47a6a3zNlftPoM3w:::eyJ0eXAiOiJyZWZyZXNoK2p3dCIsImFsZyI6IkVTMjU2SyJ9.eyJzY29wZSI6ImNvbS5hdHByb3RvLnJlZnJlc2giLCJzdWIiOiJkaWQ6cGxjOmppand0emdyb3k3NnNhbW5pdmxxcnBlYyIsImF1ZCI6ImRpZDp3ZWI6YnNreS5zb2NpYWwiLCJqdGkiOiIzK2xxRkEzaVRCNTVabGRPb3VleVphTVZWTlRjcUprbmp1ZWZLTW55bXdnIiwiaWF0IjoxNzMxMzQyOTQ3LCJleHAiOjE3MzkxMTg5NDd9.pT39p8i9tLGGvg8OD53jXw0WXidkKUWtuxNeNZGVgGIgXUnqbvsDpp5g4rSwmEUDpRyPLyjF6Sx057vKfRw4HQ:::https://porcini.us-east.host.bsky.network')

# Worker class that processes DIDs
class Worker:
    def __init__(self, task_queue, print_interval=100):
        self.task_queue = task_queue
        self.print_interval = print_interval
        self.client = create_client_instance()  # Instantiate client once

    def run(self):
        while True:
            did = self.task_queue.get()  # Get DID from the queue
            if did is None:  # None is the signal to stop processing
                break
            self.process_did(did)

    def process_did(self, did):
        # Check if the DID has already been processed
        processed_key = f"processed_{did}"
        if r.exists(processed_key):
            print(f"Skipping {did}: already processed")
            return

        try:
            user_set = self.client.get_all_follows(did)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Nope: {e}")
            return

        # Process and update Redis
        for idx, user in enumerate(user_set, start=1):
            _ = r.set(user.did, user.json())  # Store user data in Redis
            _ = r.hincrby(redis_key, user.did, 1)
            if idx % self.print_interval == 0:
                print(f"Current Redis hash size: {r.hlen(redis_key)}")
        
        # Mark this DID as processed
        r.set(processed_key, 1)
        print(f"Marked {did} as processed")

# Function to start each worker process
def start_worker(task_queue, print_interval):
    worker = Worker(task_queue, print_interval)
    worker.run()

# Main execution guard
if __name__ == "__main__":
    context = get_context("spawn")  # Use spawn context for all multiprocessing objects
    num_workers = 2  # Number of worker processes
    task_queue = context.Queue()  # Create Queue using the spawn context

    # Enqueue all DIDs
    for did in user_did_list:
        task_queue.put(did)

    # Add stop signals (None) for each worker
    for _ in range(num_workers):
        task_queue.put(None)

    # Start worker processes
    processes = [
        context.Process(target=start_worker, args=(task_queue, 100))
        for _ in range(num_workers)
    ]

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Process interrupted by user.")

    # Retrieve final counts if needed
    final_user_dids = Counter({k.decode(): int(v) for k, v in r.hgetall(redis_key).items()})
    print(f"Total unique user DIDs accumulated: {len(final_user_dids)}")

