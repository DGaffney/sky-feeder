import os
import sys
import asyncio
import signal

from fastapi import FastAPI, Request, Depends, Form, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime

from server.bluesky_api import BlueskyAPI, is_app_passwordy
from server import config, data_stream
from server.algos import algos
from server.data_filter import operations_callback

app = FastAPI()
SECRET = os.getenv("SECRET_KEY", "foo")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

templates = Jinja2Templates(directory="templates")

stream_stop_event = asyncio.Event()

async def start_data_stream():
    await data_stream.run(config.SERVICE_DID, operations_callback, stream_stop_event)

# Conditionally start the data stream on startup
if os.getenv("ENABLE_DATA_STREAM") == "true":
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(start_data_stream())

# Signal handler for graceful shutdown
def sigint_handler(*_):
    print('Stopping data stream...')
    stream_stop_event.set()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
# Define the custom filter function
def datetimeformat(value, format='%Y-%m-%d %I:%M %p'):
    # Replace 'Z' with '+00:00' for compatibility with fromisoformat
    if value.endswith('Z'):
        value = value.replace('Z', '+00:00')
    dt = datetime.fromisoformat(value)
    return dt.strftime(format)

# Register the custom filter with the Jinja2 environment
templates.env.filters['datetimeformat'] = datetimeformat

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

    try:
        body = algo(cursor, limit)
    except ValueError:
        raise HTTPException(status_code=400, detail="Malformed cursor")

    return JSONResponse(content=body)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    response = RedirectResponse(url="/timeline", status_code=302)
    manager.set_cookie(response, username)
    request.session['username'] = username
    if is_app_passwordy(password):
        request.session['password'] = password
    else:
        raise HTTPException(status_code=401, detail="This doesn't look app-passwordy - please go generate one!")
    return response

