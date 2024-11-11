#!/bin/bash

# Get the directory of the current Git repository
REPO_DIR=$(git rev-parse --show-toplevel)

# Define the log file path relative to the repo directory
LOG_FILE="$REPO_DIR/install_nginx.log"

# Define common paths
NGINX_CONF_DIR="/opt/homebrew/etc/nginx"
NGINX_PID_DIR="/usr/local/var/run"
WWW_DIR="/usr/local/var/www"

# Function to log messages to both console and log file
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Start logging
log "Starting Nginx and FileZilla Server installation script."
echo "Starting Nginx and FileZilla Server installation script."

# Check if Nginx is already running and stop it if necessary
log "Checking if Nginx is running."
echo "Checking if Nginx is running."
if pgrep nginx > /dev/null; then
    log "Nginx is running. Stopping Nginx..."
    echo "Nginx is running. Stopping Nginx..."
    sudo nginx -s stop
    log "Nginx stopped successfully."
    echo "Nginx stopped successfully."
else
    log "Nginx is not running."
    echo "Nginx is not running."
fi

# Ensure Homebrew is installed
log "Checking if Homebrew is installed."
echo "Checking if Homebrew is installed."
if ! command -v brew &> /dev/null; then
    log "Homebrew not found. Installing Homebrew..."
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    [ $? -ne 0 ] && log "Failed to install Homebrew." && exit 1
else
    log "Homebrew is already installed."
    echo "Homebrew is already installed."
fi

# Step 1: Fix Homebrew permissions to ensure proper operation
log "Fixing Homebrew permissions..."
echo "Fixing Homebrew permissions..."
sudo chown -R $(whoami) /opt/homebrew/Cellar/nginx
sudo chown -R $(whoami) /opt/homebrew/opt/nginx
sudo chown -R $(whoami) /opt/homebrew/var/homebrew
log "Homebrew permissions fixed successfully."
echo "Homebrew permissions fixed successfully."

# Step 2: Install or update Nginx
log "Installing or updating Nginx..."
brew install nginx
log "Nginx installed successfully."
echo "Nginx installed successfully."

# Step 3: Set up directories
log "Checking /usr/local/var/www directory."
if [ ! -d "/usr/local/var/www" ]; then
  sudo mkdir -p /usr/local/var/www
  sudo chown -R $(whoami):$(id -gn) /usr/local/var/www
  log "/usr/local/var/www created and permissions set."
else
  log "/usr/local/var/www already exists."
fi

# Step 4: Copy custom Nginx config
log "Copying custom Nginx config..."

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# Define the relative path to nginx.conf
NGINX_CONF="$SCRIPT_DIR/nginx.conf"

# Check if nginx.conf exists
if [ ! -f "$NGINX_CONF" ]; then
    log "nginx.conf not found in $SCRIPT_DIR"
    echo "nginx.conf not found in $SCRIPT_DIR"
    exit 1
fi

# Copy the nginx.conf to the appropriate directory
sudo cp "$NGINX_CONF" /opt/homebrew/etc/nginx/nginx.conf

log "Custom Nginx configuration copied successfully."
echo "Custom Nginx configuration copied successfully."


# Step 5: Ensure directories for runtime exist
log "Ensuring /usr/local/var/run exists."
sudo mkdir -p /usr/local/var/run
sudo chown -R $(whoami):$(id -gn) /usr/local/var/run
log "/usr/local/var/run exists."

# Step 6: Test Nginx configuration
log "Testing Nginx configuration..."
nginx -t
log "Nginx configuration test successful."
echo "Nginx configuration test successful."

# Step 7: Start Nginx and enable on boot
log "Starting Nginx..."
nginx
log "Nginx started successfully."

log "Ensuring Nginx runs on boot..."

# Modify plist to use non-root user (if not already done)
sudo sed -i '' 's/UserName=root/UserName=$(whoami)/g' /Library/LaunchDaemons/homebrew.mxcl.nginx.plist
sudo sed -i '' 's/GroupName=root/GroupName=$(id -gn)/g' /Library/LaunchDaemons/homebrew.mxcl.nginx.plist

# Start Nginx service with user privileges
brew services start nginx
log "Nginx configured to start on boot."
echo "Nginx Installation completed successfully!"

# Run the EPG merge script
log "Running merge_epg.py script..."
echo "Running merge_epg.py script..."
if command -v python3 &> /dev/null; then
    python3 "$REPO_DIR/merge_epg.py"
    [ $? -ne 0 ] && log "Failed to execute merge_epg.py." && exit 1
    log "EPG data merged successfully."
    echo "EPG data merged successfully."
else
    log "Python 3 is not installed. Please install it first." && exit 1
    echo "Python 3 is not installed. Please install it first."
fi

log "Nginx and FileZilla Server setup is complete!"
echo "Nginx and FileZilla Server setup is complete!"
