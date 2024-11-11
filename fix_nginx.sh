#!/bin/bash

# Define the PID file directory and file
PID_DIR="/usr/local/var/run"
PID_FILE="${PID_DIR}/nginx.pid"

# Create the directory if it doesn't exist
if [ ! -d "$PID_DIR" ]; then
  echo "Directory $PID_DIR does not exist. Creating it."
  sudo mkdir -p "$PID_DIR"
  sudo chown -R $(whoami):staff "$PID_DIR"
fi

# Create the PID file if it doesn't exist
if [ ! -f "$PID_FILE" ]; then
  echo "PID file $PID_FILE does not exist. Creating it."
  sudo touch "$PID_FILE"
  sudo chown $(whoami):staff "$PID_FILE"
fi

# Set proper permissions on the PID file
echo "Setting permissions for $PID_FILE"
sudo chown $(whoami):staff "$PID_FILE"

# Ensure Nginx is not running and start it
echo "Checking if Nginx is running..."
if pgrep nginx > /dev/null; then
  echo "Nginx is already running. Restarting Nginx..."
  sudo nginx -s stop
fi

echo "Starting Nginx..."
sudo nginx

# Verify Nginx is running
if pgrep nginx > /dev/null; then
  echo "Nginx started successfully."
else
  echo "Nginx failed to start."
fi
