#!/bin/bash

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script
# bash install_nginx.sh

# chmod +x install_nginx.sh
# ./uninstall_nginx.sh


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

# Ensure the log file exists
touch "$LOG_FILE" || { echo "Failed to create log file. Exiting."; exit 1; }

# Start logging
log "Starting Nginx uninstallation script."
echo "Starting Nginx uninstallation script."

# Step 1: Stop Nginx if running
log "Step 1: Checking if Nginx is running."
echo "Step 1: Checking if Nginx is running."
if pgrep nginx > /dev/null; then
    log "Nginx is running. Attempting to stop it..."
    echo "Nginx is running. Attempting to stop it..."
    if sudo nginx -s stop; then
        log "Nginx stopped successfully."
        echo "Nginx stopped successfully."
    else
        log "Failed to stop Nginx. Proceeding with uninstallation."
        echo "Failed to stop Nginx. Proceeding with uninstallation."
    fi
else
    log "Nginx is not running."
    echo "Nginx is not running."
fi

# Step 2: Uninstall Nginx via Homebrew
log "Step 2: Uninstalling Nginx using Homebrew..."
echo "Step 2: Uninstalling Nginx using Homebrew..."
if brew uninstall nginx; then
    log "Nginx uninstalled successfully."
    echo "Nginx uninstalled successfully."
else
    log "Failed to uninstall Nginx. It may not be installed."
    echo "Failed to uninstall Nginx. It may not be installed."
fi

# Step 3: Remove Nginx configuration files
log "Step 3: Removing Nginx configuration files..."
echo "Step 3: Removing Nginx configuration files..."
if [ -f "$NGINX_CONF_DIR/nginx.conf" ]; then
    if sudo rm "$NGINX_CONF_DIR/nginx.conf"; then
        log "Nginx configuration file removed."
        echo "Nginx configuration file removed."
    else
        log "Failed to remove Nginx configuration file."
        echo "Failed to remove Nginx configuration file."
    fi
else
    log "Nginx configuration file does not exist."
    echo "Nginx configuration file does not exist."
fi

# Step 4: Remove directories
log "Step 4: Removing /usr/local/var/www directory..."
echo "Step 4: Removing /usr/local/var/www directory..."
if [ -d "$WWW_DIR" ]; then
    if sudo rm -rf "$WWW_DIR"; then
        log "/usr/local/var/www directory removed."
        echo "/usr/local/var/www directory removed."
    else
        log "Failed to remove /usr/local/var/www directory."
        echo "Failed to remove /usr/local/var/www directory."
    fi
else
    log "/usr/local/var/www directory does not exist."
    echo "/usr/local/var/www directory does not exist."
fi

log "Step 4: Removing /usr/local/var/run directory..."
echo "Step 4: Removing /usr/local/var/run directory..."
if [ -d "$NGINX_PID_DIR" ]; then
    if sudo rm -rf "$NGINX_PID_DIR"; then
        log "/usr/local/var/run directory removed."
        echo "/usr/local/var/run directory removed."
    else
        log "Failed to remove /usr/local/var/run directory."
        echo "Failed to remove /usr/local/var/run directory."
    fi
else
    log "/usr/local/var/run directory does not exist."
    echo "/usr/local/var/run directory does not exist."
fi

# Step 5: Remove LaunchDaemon plist file for Nginx
log "Step 5: Removing Nginx LaunchDaemon plist..."
echo "Step 5: Removing Nginx LaunchDaemon plist..."
if [ -f "/Library/LaunchDaemons/homebrew.mxcl.nginx.plist" ]; then
    if sudo rm "/Library/LaunchDaemons/homebrew.mxcl.nginx.plist"; then
        log "Nginx LaunchDaemon plist removed."
        echo "Nginx LaunchDaemon plist removed."
    else
        log "Failed to remove Nginx LaunchDaemon plist."
        echo "Failed to remove Nginx LaunchDaemon plist."
    fi
else
    log "Nginx LaunchDaemon plist does not exist."
    echo "Nginx LaunchDaemon plist does not exist."
fi

# Step 6: Stop Nginx service from starting on boot
log "Step 6: Ensuring Nginx service is stopped on boot..."
echo "Step 6: Ensuring Nginx service is stopped on boot..."
if brew services stop nginx; then
    log "Nginx service stopped from starting on boot."
    echo "Nginx service stopped from starting on boot."
else
    log "Failed to stop Nginx service from starting on boot or it was not running."
    echo "Failed to stop Nginx service from starting on boot or it was not running."
fi

# Step 7: Remove Nginx-related cron jobs
log "Step 7: Removing Nginx-related cron jobs..."
echo "Step 7: Removing Nginx-related cron jobs..."

# Backup current crontab
CRONTAB_BACKUP="$(crontab -l 2>/dev/null)"
if [ $? -eq 0 ]; then
    echo "$CRONTAB_BACKUP" > "$(pwd)/crontab_backup_$(date +'%Y%m%d_%H%M%S').txt"
    log "Crontab backup saved."
    echo "Crontab backup saved."
else
    log "No existing crontab found to back up."
    echo "No existing crontab found to back up."
fi

# Clear all cron jobs (remove all cron jobs for the user)
log "Clearing all cron jobs for the user..."
crontab -r
if [ $? -eq 0 ]; then
    log "All cron jobs cleared."
    echo "All cron jobs cleared."
else
    log "Failed to clear cron jobs."
    echo "Failed to clear cron jobs."
fi

# Remove Nginx-related entries (match against the full command or path)
UPDATED_CRONTAB=$(echo "$CRONTAB_BACKUP" | grep -vE 'nginx|merge_epg.py|path/to/nginx/script')

if [ "$UPDATED_CRONTAB" != "$CRONTAB_BACKUP" ]; then
    echo "$UPDATED_CRONTAB" | crontab -
    if [ $? -eq 0 ]; then
        log "Nginx-related cron jobs removed successfully."
        echo "Nginx-related cron jobs removed successfully."
    else
        log "Failed to update crontab."
        echo "Failed to update crontab."
    fi
else
    log "No Nginx-related cron jobs found."
    echo "No Nginx-related cron jobs found."
fi
