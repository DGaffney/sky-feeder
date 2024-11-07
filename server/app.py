import sys
import asyncio
import signal

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from server import config, data_stream
from server.algos import algos
from server.data_filter import operations_callback

app = FastAPI()

stream_stop_event = asyncio.Event()

async def start_data_stream():
    await data_stream.run(config.SERVICE_DID, operations_callback, stream_stop_event)

# Register the startup event to launch the data stream in the background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_data_stream())

# Signal handler for graceful shutdown
def sigint_handler(*_):
    print('Stopping data stream...')
    stream_stop_event.set()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

@app.get("/")
async def index():
    return "ATProto Feed Generator powered by The AT Protocol SDK for Python (https://github.com/MarshalX/atproto)."

@app.get("/.well-known/did.json")
async def did_json():
    if not config.SERVICE_DID.endswith(config.HOSTNAME):
        raise HTTPException(status_code=404, detail="Not Found")

    response_content = {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": config.SERVICE_DID,
        "service": [
            {
                "id": "#bsky_fg",
                "type": "BskyFeedGenerator",
                "serviceEndpoint": f"https://{config.HOSTNAME}"
            }
        ]
    }
    return JSONResponse(content=response_content)

@app.get("/xrpc/app.bsky.feed.describeFeedGenerator")
async def describe_feed_generator():
    feeds = [{"uri": uri} for uri in algos.keys()]
    response_content = {
        "encoding": "application/json",
        "body": {
            "did": config.SERVICE_DID,
            "feeds": feeds
        }
    }
    return JSONResponse(content=response_content)

@app.get("/xrpc/app.bsky.feed.getFeedSkeleton")
async def get_feed_skeleton(feed: str = None, cursor: str = None, limit: int = 20):
    algo = algos.get(feed)
    if not algo:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    # Example of how to check auth if giving user-specific results:
    """
    from server.auth import AuthorizationError, validate_auth
    try:
        requester_did = validate_auth(request)
    except AuthorizationError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    """

    try:
        body = await algo(cursor, limit)  # Assuming `algo` is async
    except ValueError:
        raise HTTPException(status_code=400, detail="Malformed cursor")

    return JSONResponse(content=body)
