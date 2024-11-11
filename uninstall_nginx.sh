#!/bin/bash

# Define common paths
NGINX_CONF_DIR="/opt/homebrew/etc/nginx"
NGINX_PID_DIR="/usr/local/var/run"
WWW_DIR="/usr/local/var/www"
LOG_FILE="$(pwd)/uninstall_nginx.log"

# Function to log messages to both console and log file
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Start logging
log "Starting Nginx uninstallation script."
echo "Starting Nginx uninstallation script."

# Step 1: Stop Nginx if running
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

# Step 2: Uninstall Nginx via Homebrew
log "Uninstalling Nginx..."
brew uninstall nginx
log "Nginx uninstalled successfully."
echo "Nginx uninstalled successfully."

# Step 3: Remove Nginx configuration files
log "Removing Nginx configuration files..."
if [ -f "$NGINX_CONF_DIR/nginx.conf" ]; then
    sudo rm "$NGINX_CONF_DIR/nginx.conf"
    log "Nginx configuration file removed."
    echo "Nginx configuration file removed."
else
    log "Nginx configuration file does not exist."
    echo "Nginx configuration file does not exist."
fi

# Step 4: Remove directories
log "Removing /usr/local/var/www directory..."
if [ -d "$WWW_DIR" ]; then
    sudo rm -rf "$WWW_DIR"
    log "/usr/local/var/www directory removed."
    echo "/usr/local/var/www directory removed."
else
    log "/usr/local/var/www directory does not exist."
    echo "/usr/local/var/www directory does not exist."
fi

log "Removing /usr/local/var/run directory..."
if [ -d "$NGINX_PID_DIR" ]; then
    sudo rm -rf "$NGINX_PID_DIR"
    log "/usr/local/var/run directory removed."
    echo "/usr/local/var/run directory removed."
else
    log "/usr/local/var/run directory does not exist."
    echo "/usr/local/var/run directory does not exist."
fi

# Step 5: Remove LaunchDaemon plist file for Nginx
log "Removing Nginx LaunchDaemon plist..."
if [ -f "/Library/LaunchDaemons/homebrew.mxcl.nginx.plist" ]; then
    sudo rm "/Library/LaunchDaemons/homebrew.mxcl.nginx.plist"
    log "Nginx LaunchDaemon plist removed."
    echo "Nginx LaunchDaemon plist removed."
else
    log "Nginx LaunchDaemon plist does not exist."
    echo "Nginx LaunchDaemon plist does not exist."
fi

# Step 6: Stop Nginx service from starting on boot
log "Ensuring Nginx service is stopped on boot..."
brew services stop nginx
log "Nginx service stopped from starting on boot."
echo "Nginx service stopped from starting on boot."

# Final message
log "Nginx uninstallation complete!"
echo "Nginx uninstallation complete!"
