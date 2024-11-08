#!/bin/bash

# Define the log file path
LOG_FILE="/Users/kyleabrahams/Documents/GitHub/tv/install_nginx.log"

# Function to log messages to both console and log file
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Start logging
log "Starting Nginx installation script."

# Ensure Homebrew is installed
echo "Checking if Homebrew is installed..."
if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew is already installed."
fi

# Install Nginx using Homebrew
echo "Installing Nginx..."
brew install nginx

# Replace the default Nginx configuration with the one from GitHub
echo "Copying custom Nginx config..."
# Adjusting paths for Homebrew installation of Nginx on macOS
sudo cp nginx.conf /opt/homebrew/etc/nginx/nginx.conf
sudo cp default.conf /opt/homebrew/etc/nginx/servers/default

# Test the configuration for syntax errors
echo "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx to apply changes
echo "Restarting Nginx..."
sudo nginx -s reload

# Enable Nginx to start on boot (macOS-specific)
echo "Enabling Nginx to start on boot..."
sudo brew services start nginx

echo "Nginx setup is complete!"

# Check if Python 3 is installed
echo "Checking if Python 3 is installed..."
if ! command -v python3 &> /dev/null; then
  echo "Python 3 not found. Installing Python 3..."
  brew install python
else
  echo "Python 3 is already installed."
fi

# Run merge_epg.py (if it exists in the current directory or provide the full path)
EPG_SCRIPT="./merge_epg.py"

if [[ -f "$EPG_SCRIPT" ]]; then
  echo "Running EPG merge script..."
  python3 "$EPG_SCRIPT"
else
  echo "EPG merge script (merge_epg.py) not found in the current directory."
fi

echo "EPG creation (if applicable) is complete!"
