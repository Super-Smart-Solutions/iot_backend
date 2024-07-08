#!/bin/bash

# Command to run your FastAPI app and generate the OpenAPI JSON
poetry run python -m iot_backend &

# Wait for the app to start
sleep 10

# Download the OpenAPI JSON file
curl -o api_doc.json http://127.0.0.1:8000/api/openapi.json

# Terminate the FastAPI app
pkill -f "python -m iot_backend"

# Install Redoc CLI
npm install -g redoc-cli

# Generate Redoc HTML
mkdir -p docs
redoc-cli bundle api_doc.json -o iot_backend/docs/index.html


# Switch to gh-pages branch
git checkout gh-pages || git checkout -b gh-pages

# Copy generated docs
cp -r docs/* .

# Commit and push changes
git add index.html
git commit -m "Update API documentation"
git push origin gh-pages
