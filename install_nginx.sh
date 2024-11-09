#!/bin/bash

# Define the log file path relative to the repo directory
REPO_DIR=$(git rev-parse --show-toplevel)
LOG_FILE="$REPO_DIR/install_nginx.log"

# Function to log messages to both console and log file
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Start logging
log "Starting Nginx installation script."

# Get the current user's username and group name
USER_NAME=$(whoami)
GROUP_NAME=$(id -gn)

# Ensure Homebrew is installed
echo "Checking if Homebrew is installed..."
if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>&1 | tee -a "$LOG_FILE"
  if [ $? -ne 0 ]; then
    log "Failed to install Homebrew."
    exit 1
  fi
else
  echo "Homebrew is already installed."
fi



# Set directories for Nginx
HOMEBREW_PREFIX=$(brew --prefix)
PID_DIR="/usr/local/var/run/"
PID_FILE="$PID_DIR/nginx.pid"
DIR="$HOMEBREW_PREFIX/var/www/"

# Set ownership and permissions for the directories
echo "Setting ownership for $DIR to $USER_NAME:$GROUP_NAME"
sudo chown -R "$USER_NAME:$GROUP_NAME" "$DIR" 2>&1 | tee -a "$LOG_FILE"

# Verify the changes
ls -l "$DIR" 2>&1 | tee -a "$LOG_FILE"

# Create necessary directories if they do not exist
if [ ! -d "$DIR" ]; then
  echo "Directory $DIR not found. Creating it..."
  sudo mkdir -p "$DIR" 2>&1 | tee -a "$LOG_FILE"
  echo "Directory $DIR created successfully."
else
  echo "Directory $DIR already exists."
fi

# Set permissions and ownership
echo "Setting permissions and ownership for $DIR..."
sudo chmod -R 775 "$DIR" 2>&1 | tee -a "$LOG_FILE"
sudo chown -R $USER "$DIR" 2>&1 | tee -a "$LOG_FILE"
echo "Permissions and ownership set successfully for $DIR."

# Install Nginx using Homebrew (without sudo)
echo "Installing Nginx..."
if ! brew install nginx 2>&1 | tee -a "$LOG_FILE"; then
  log "Failed to install Nginx."
  exit 1
fi

# Set permissions for Nginx
echo "Setting permissions for Nginx..."
sudo chmod -R 775 "$DIR" 2>&1 | tee -a "$LOG_FILE"
sudo chown -R $USER "$DIR" 2>&1 | tee -a "$LOG_FILE"

# Ensure the PID directory exists
if [ ! -d "$PID_DIR" ]; then
  echo "Creating the PID directory $PID_DIR..."
  sudo mkdir -p "$PID_DIR" || { echo "Failed to create directory $PID_DIR"; exit 1; }
  sudo chown -R "$USER_NAME:$GROUP_NAME" "$PID_DIR" || { echo "Failed to set ownership for $PID_DIR"; exit 1; }
  echo "PID directory created and ownership set."
else
  echo "PID directory already exists."
fi

# Check for existing nginx.pid and remove if it exists
if [ -f "$PID_FILE" ]; then
  echo "Removing existing Nginx PID file..."
  sudo rm -f "$PID_FILE" || { echo "Failed to remove $PID_FILE"; exit 1; }
fi

# Ensure the PID file is created if it doesn't exist
if [ ! -f "$PID_FILE" ]; then
  sudo touch "$PID_FILE" || { echo "Failed to create $PID_FILE"; exit 1; }
  sudo chown "$USER_NAME:$GROUP_NAME" "$PID_FILE" || { echo "Failed to set ownership for $PID_FILE"; exit 1; }
  echo "PID file created and ownership set."
else
  echo "PID file already exists."
fi

# Restart Nginx to apply changes
echo "Restarting Nginx..."
sudo nginx -s reload 2>&1 | tee -a "$LOG_FILE"

# Test the configuration for syntax errors
echo "Testing Nginx configuration..."
sudo nginx -t 2>&1 | tee -a "$LOG_FILE"

# Enable Nginx to start on boot (macOS-specific)
echo "Enabling Nginx to start on boot..."
sudo brew services start nginx 2>&1 | tee -a "$LOG_FILE"

log "Nginx setup is complete!"

# ** Add this to ensure the fix script is executable before calling it **
echo "Making sure fix_nginx.sh is executable..."
chmod +x fix_nginx.sh

# After installing and configuring Nginx, call the fix script
echo "Running fix_nginx.sh to resolve potential issues..."
./fix_nginx.sh

log "Nginx setup is complete!"
# Check if Python 3 is installed
echo "Checking if Python 3 is installed..."
if ! command -v python3 &> /dev/null; then
  echo "Python 3 not found. Installing Python 3..."
  if ! brew install python 2>&1 | tee -a "$LOG_FILE"; then
    log "Python 3 installation failed."
    exit 1
  fi
else
  echo "Python 3 is already installed."
fi

# Check if `requests` is installed, and install if not
echo "Checking if 'requests' module is installed..."
if ! python3 -c "import requests" &> /dev/null; then
  echo "'requests' module not found. Installing 'requests'..."
  python3 -m pip install requests 2>&1 | tee -a "$LOG_FILE"
  if [ $? -ne 0 ]; then
    log "Failed to install 'requests'."
    exit 1
  fi
else
  echo "'requests' module is already installed."
fi

# Run merge_epg.py (if it exists in the current directory or provide the full path)
EPG_SCRIPT="$REPO_DIR/merge_epg.py"
if [[ -f "$EPG_SCRIPT" ]]; then
  echo "Running EPG merge script..."
  python3 "$EPG_SCRIPT" 2>&1 | tee -a "$LOG_FILE"
  if [ $? -ne 0 ]; then
    log "Failed to run $EPG_SCRIPT."
    exit 1
  else
    echo "EPG merge script executed successfully."
  fi
else
  log "EPG merge script not found at $EPG_SCRIPT."
  exit 1
fi
