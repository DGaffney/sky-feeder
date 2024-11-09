import os
import sys
import asyncio
import signal
from server import config, data_stream
from server.data_filter import operations_callback

stream_stop_event = asyncio.Event()

async def start_data_stream():
    """Starts the data stream."""
    await data_stream.run(config.SERVICE_DID, operations_callback, stream_stop_event)

def sigint_handler(*_):
    """Graceful shutdown on SIGINT."""
    print('Stopping data stream...')
    stream_stop_event.set()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    asyncio.run(start_data_stream())
