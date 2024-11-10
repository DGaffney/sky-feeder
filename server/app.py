import json
import os
from datetime import datetime
import atproto
from pydantic import ValidationError

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from server.bluesky_api import BlueskyAPI, is_app_passwordy
from server import config
from server.database import UserAlgorithm, get_db
from server.logger import logger
from server.algos.algo import get_posts
app = FastAPI()
SECRET = os.getenv("SECRET_KEY", "foo")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

templates = Jinja2Templates(directory="templates")
manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
manager.cookie_name = "auth_cookie"

# Define the custom filter function for datetime formatting
def datetimeformat(value, format='%Y-%m-%d %I:%M %p'):
    if value.endswith('Z'):
        value = value.replace('Z', '+00:00')
    dt = datetime.fromisoformat(value)
    return dt.strftime(format)

# Register the custom filter with the Jinja2 environment
templates.env.filters['datetimeformat'] = datetimeformat

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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
async def describe_feed_generator(db: Session = Depends(get_db)):
    feeds = [{"uri": e.algo_uri} for e in db.query(UserAlgorithm).all()]
    response_content = {
        "encoding": "application/json",
        "body": {
            "did": config.SERVICE_DID,
            "feeds": feeds
        }
    }
    return JSONResponse(content={"feeds": feeds})

@app.get("/xrpc/app.bsky.feed.getFeedSkeleton")
async def get_feed_skeleton(feed: str = None, cursor: str = None, limit: int = 20, db: Session = Depends(get_db)):
    algo = db.query(UserAlgorithm).filter(UserAlgorithm.algo_uri == feed).first()
    if not algo:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    try:
        body = get_posts(db, algo, cursor, limit)
        if body["feed"] == []:
            body = {"feed": []}
    except ValueError:
        raise HTTPException(status_code=400, detail="Malformed cursor")

    return JSONResponse(content=body)

@app.get("/my_feeds")
async def my_feeds(request: Request, db: Session = Depends(get_db)):
    client = BlueskyAPI(request.session['username'], request.session['password'], request.session['session_string'])
    user_algos = db.query(UserAlgorithm).filter(UserAlgorithm.user_id == client.client.me.did).all()
    return templates.TemplateResponse("my_feeds.html", {"request": request, "feeds": client.get_client_feeds, "user_algos": user_algos})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    response = RedirectResponse(url="/my_feeds", status_code=302)
    manager.set_cookie(response, username)
    request.session['username'] = username
    if is_app_passwordy(password):
        request.session['password'] = password
        try:
            client = BlueskyAPI(username, password)
            request.session['session_string'] = client.session_string
        except atproto_client.exceptions.UnauthorizedError:
            raise HTTPException(status_code=401, detail="This username/password combo looks to have failed on login at bsky - try a different combo?")
    else:
        raise HTTPException(status_code=401, detail="This doesn't look app-passwordy - please go generate one!")
    return response

@app.post("/add_algo", name="add_algo")
async def add_algo(
    request: Request,
    feed_name: str = Form(...),
    feed_manifest: str = Form(...),
    display_name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Create a new UserAlgorithm instance
        client = BlueskyAPI(request.session['username'], request.session['password'], request.session['session_string'])
        new_algo = UserAlgorithm(
            user_id=client.client.me.did,
            algo_uri=feed_name,
            algo_manifest=json.loads(feed_manifest),
            record_name=feed_name,
            display_name=display_name,
            description=description,
            version_hash="some_hash"
        )
        

        # Attempt to publish the feed, which may trigger a pydantic ValidationError
        feed, feed_did = new_algo.publish_feed(
            request.session['username'],
            request.session['password'],
            request.session['session_string'],
            feed_name,
            display_name,
            description
        )

        # If successful, proceed to add and commit the new algorithm
        new_algo.algo_uri = feed.uri
        new_algo.feed_did = feed_did
        db.add(new_algo)
        db.commit()

        # Redirect to the feeds page
        return RedirectResponse(url="/my_feeds", status_code=303)

    except ValidationError as e:
        # Capture and format Pydantic validation errors
        error_details = [
            {"field": err["loc"], "message": err["msg"]}
            for err in e.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation failed",
                "details": error_details
            }
        )

    except Exception as e:
        # General error handler
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred", "details": str(e)}
        )

@app.post("/edit_algo", name="edit_algo")
async def edit_algo(
    request: Request,
    algo_id: int = Form(...), 
    feed_name: str = Form(...),
    feed_manifest: str = Form(...),
    display_name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    algo = db.query(UserAlgorithm).filter(UserAlgorithm.id == algo_id).first()
    if not algo:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    # Update the algorithm details
    algo.feed_name = feed_name
    logger.info(type(feed_manifest))
    algo.algo_manifest = json.loads(feed_manifest)
    algo.display_name = display_name
    algo.description = description
    algo.update_feed(request.session['username'], request.session['password'], request.session['session_string'])
    db.commit()
    return RedirectResponse(url="/my_feeds", status_code=303)

@app.post("/delete_algo", name="delete_algo")
async def delete_algo(request: Request, algo_id: int = Form(...), db: Session = Depends(get_db)):
    # Query for the algorithm by ID
    algo = db.query(UserAlgorithm).filter(UserAlgorithm.id == algo_id).first()
    algo.delete_feed(request.session['username'], request.session['password'], request.session['session_string'])
    if not algo:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    # Delete the algorithm and commit the transaction
    db.delete(algo)
    db.commit()

    # Redirect back to the feeds page
    return RedirectResponse(url="/my_feeds", status_code=303)