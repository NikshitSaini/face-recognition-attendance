#!/bin/bash

# Script to deploy the Flask application on PythonAnywhere

# --- Configuration ---
PROJECT_DIR="/home/<your_pythonanywhere_username>/face-recognition-attendance"
VIRTUALENV_DIR="$PROJECT_DIR/myenv"
WSGI_FILE="/var/www/<your_pythonanywhere_username>_pythonanywhere_com_wsgi.py"

# --- Functions ---

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# --- Main Script ---

log "Starting deployment..."

# 1. Navigate to the project directory
log "Navigating to project directory: $PROJECT_DIR"
cd "$PROJECT_DIR" || { log "Error: Could not navigate to project directory."; exit 1; }

# 2. Activate the virtual environment
log "Activating virtual environment: $VIRTUALENV_DIR"
source "$VIRTUALENV_DIR/bin/activate" || { log "Error: Could not activate virtual environment."; exit 1; }

# 3. Pull the latest changes from Git
log "Pulling latest changes from Git..."
git pull origin main || { log "Error: Could not pull latest changes from Git."; exit 1; }

# 4. Upgrade dependencies
log "Upgrading dependencies..."
pip install --upgrade pip || { log "Error: Could not upgrade pip."; exit 1; }
pip install -r requirements.txt || { log "Error: Could not install dependencies."; exit 1; }

# 5. Touch the WSGI file to trigger a reload
log "Touching WSGI file to trigger reload: $WSGI_FILE"
touch "$WSGI_FILE" || { log "Error: Could not touch WSGI file."; exit 1; }

log "Deployment complete!"

