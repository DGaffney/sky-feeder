#!/bin/sh

if [ "$1" = "api" ]; then
    exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --workers 4
elif [ "$1" = "data-stream" ]; then
    python streamer.py
elif [ "$1" = "algo-matcher-worker" ]; then
    python algo_matcher.py
else
    echo "Unknown command. Use 'api' or 'data-stream'."
    exit 1
fi