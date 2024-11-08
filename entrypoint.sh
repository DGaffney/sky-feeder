#!/bin/sh

if [ "$1" = "api" ]; then
    exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT"
elif [ "$1" = "data-stream" ]; then
    export ENABLE_DATA_STREAM=true
    exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT"
else
    echo "Unknown command. Use 'api' or 'data-stream'."
    exit 1
fi
