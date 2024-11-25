#!/bin/bash

## Create Virtual Environment fot Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script
# bash install_nginx.sh

# chmod +x install_nginx.sh
# ./install_nginx.sh


# 1. Get the directory of the current Git repository
REPO_DIR=$(git rev-parse --show-toplevel)

# 2. Define the log file path relative to the repo directory
LOG_FILE="$REPO_DIR/install_nginx.log"

# 3. Define common paths
NGINX_CONF_DIR="/opt/homebrew/etc/nginx"
NGINX_PID_DIR="/usr/local/var/run"
WWW_DIR="/usr/local/var/www"

# 4. Function to log messages to both console and log file
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# 5. Start logging
log "Starting Nginx installation script."
echo "Starting Nginx installation script."

## Function to prompt the user to continue or exit on error
prompt_to_continue() {
    read -p "An error occurred. Do you want to continue? (y/n): " answer
    if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
        echo "Exiting script."
        exit 1
    fi
}

# 6. Check if Nginx is already running and stop it if necessary
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

# 7. Ensure Homebrew is installed
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

# 8. Fix Homebrew permissions to ensure proper operation
log "Fixing Homebrew permissions..."
echo "Fixing Homebrew permissions..."
sudo chown -R $(whoami) /opt/homebrew/Cellar/nginx
sudo chown -R $(whoami) /opt/homebrew/opt/nginx
sudo chown -R $(whoami) /opt/homebrew/var/homebrew
log "Homebrew permissions fixed successfully."
echo "Homebrew permissions fixed successfully."

# 9. Install or update Nginx
log "Installing or updating Nginx..."
brew install nginx
log "Nginx installed successfully."
echo "Nginx installed successfully."

# 10. Set up directories
log "Checking /usr/local/var/www directory."
if [ ! -d "/usr/local/var/www" ]; then
  sudo mkdir -p /usr/local/var/www
  sudo chown -R $(whoami):$(id -gn) /usr/local/var/www
  log "/usr/local/var/www created and permissions set."
else
  log "/usr/local/var/www already exists."
fi

# 11. Copy custom Nginx config
log "Copying custom Nginx config..."

# 12. Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# 13. Define the relative path to nginx.conf
NGINX_CONF="$SCRIPT_DIR/nginx.conf"

# 14. Check if nginx.conf exists
if [ ! -f "$NGINX_CONF" ]; then
    log "nginx.conf not found in $SCRIPT_DIR"
    echo "nginx.conf not found in $SCRIPT_DIR"
    exit 1
fi

# 15. Copy the nginx.conf to the appropriate directory
sudo cp "$NGINX_CONF" /opt/homebrew/etc/nginx/nginx.conf
log "Custom Nginx configuration copied successfully."
echo "Custom Nginx configuration copied successfully."

# 16. Ensure directories for runtime exist
log "Ensuring /usr/local/var/run exists."
sudo mkdir -p /usr/local/var/run
sudo chown -R $(whoami):$(id -gn) /usr/local/var/run
log "/usr/local/var/run exists."

# 17. Test Nginx configuration
log "Testing Nginx configuration..."
nginx -t
if [ $? -ne 0 ]; then
    log "Nginx configuration test failed."
    exit 1
fi
log "Nginx configuration test successful."
echo "Nginx configuration test successful."

# 18. Start Nginx
log "Starting Nginx..."
nginx
log "Nginx started successfully."

# 19. Ensure Nginx runs on boot
log "Ensuring Nginx runs on boot..."
PLIST_PATH="/Library/LaunchDaemons/homebrew.mxcl.nginx.plist"
if [ -f "$PLIST_PATH" ]; then
    sudo sed -i '' "s/UserName=root/UserName=$(whoami)/g" "$PLIST_PATH"
    sudo sed -i '' "s/GroupName=root/GroupName=$(id -gn)/g" "$PLIST_PATH"
else
    log "$PLIST_PATH not found. Skipping modification."
    echo "$PLIST_PATH not found. Please configure Nginx to start on boot manually."
fi

# 20. Start Nginx service with user privileges
brew services start nginx
log "Nginx configured to start on boot."
echo "Nginx Installation completed successfully!"

# 21. Create a virtual environment
log "Creating a virtual environment..."
python3 -m venv "$REPO_DIR/venv"

# 22. Activate the virtual environment
source "$REPO_DIR/venv/bin/activate"

# 24. Install requests module
log "Installing Python requests module..."
pip install requests
if [ $? -ne 0 ]; then
    log "Failed to install requests module."
    echo "Failed to install requests module."
    exit 1
fi

# Install pytz module
log "Installing Python pytz module..."
pip install pytz
if [ $? -ne 0 ]; then
    log "Failed to install pytz module."
    echo "Failed to install pytz module."
    exit 1
fi

# 25. Ask for confirmation before running merge_epg.py
read -p "Do you want to run the merge_epg.py script? (y/n): " answer

# Check the user's response
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    log "Running merge_epg.py script..."
    python3 "$REPO_DIR/merge_epg.py"
    if [ $? -ne 0 ]; then
        log "Failed to execute merge_epg.py."
        echo "Failed to execute merge_epg.py."
        exit 1
    fi
else
    log "merge_epg.py script execution skipped."
    echo "merge_epg.py script execution skipped."
fi

# 26. Set up cron job to run merge_epg.py every 12 hours and log output 1pm,1am
log "Setting up cron job to run merge_epg.py every 12 hours and log output 1pm, 1am..."

# Define the log directory path
LOG_DIR="$REPO_DIR/log"
mkdir -p "$LOG_DIR"  # Ensure log directory exists

# Create a cron job for the current user
(crontab -l 2>/dev/null; echo "0 1,13 * * * /bin/bash -c 'source $REPO_DIR/venv/bin/activate && /usr/local/bin/python3 $REPO_DIR/merge_epg.py >> $LOG_DIR/merge_cron.log 2>&1'") | crontab -

log "Cron job for merge_epg.py set up successfully."
echo "Cron job for merge_epg.py set up successfully."

# 27. Set up cron job to reload Nginx every 6 hours after the EPG update and log output
log "Setting up cron job to reload Nginx every 6 hours after the EPG update and log output..."

# Add cron job to reload Nginx every 6 hours
(crontab -l 2>/dev/null; echo "0 */6 * * * /usr/local/bin/nginx -s reload >> $LOG_DIR/nginx_reload.log 2>&1") | crontab -

log "Cron job for Nginx reload set up successfully."
echo "Cron job for Nginx reload set up successfully."

# 28. Set up cron job to log cron is working every minute for testing
log "Setting up cron job to log 'Cron is working' every minute..."

# Add cron job to test if cron is working
(crontab -l 2>/dev/null; echo "* * * * * echo 'Cron is working at $(date)' >> $LOG_DIR/cron_test.log") | crontab -

log "Cron job for cron_test.log set up successfully."
echo "Cron job for cron_test.log set up successfully."

