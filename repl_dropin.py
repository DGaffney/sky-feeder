import uvicorn
import asyncio

from server.app import app  # Make sure this imports your FastAPI app correctly

# Function to start Uvicorn server
def start_fastapi_app():
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())

# Run the function to start the FastAPI app
start_fastapi_app()