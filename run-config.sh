#/bin/bash

# Project to use cloud run
PROJECT_ID='chess-ocr-000'
PROJECT_NAME='Chess OCR'

# Used for image name and service name
APP_NAME='web'

# "Cloud run" settings (more on "gcloud beta run deploy --help")
REGION='asia-northeast1'
PLATFORM='managed'
DEPLOY_OPTS=(
  --allow-unauthenticated
  --cpu=1
  --memory=256Mi   # default 256Mi
  --concurrency=10 # default 80
  --timeout=1m     # default 5m
)

# Specify local image name
IMAGE_NAME='registry.heroku.com/chess-ocr/web:latest'
