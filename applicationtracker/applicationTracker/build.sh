#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Build the Vue Frontend
echo "Building Frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Setup the Python Backend
echo "Setting up Backend..."
cd backend
pip install -r requirements.txt

# Create upload directories just in case
mkdir -p uploads/screenshots
mkdir -p uploads/cover_letters

# Run database migrations/creation
python -c "from app import app, db; app.app_context().push(); db.create_all()"

echo "Build complete."