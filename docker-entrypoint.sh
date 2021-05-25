#!/bin/sh

export FLASK_APP=app/main.py
export FLASK_ENV=production
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=${PORT:-5000}
export APP_MODEL_FILE=data/checkpoint/default.pt
unset APP_MODEL_LOG_DIR
exec flask run
