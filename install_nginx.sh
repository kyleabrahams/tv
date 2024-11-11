#!/bin/bash

# Get the directory of the current Git repository
REPO_DIR=$(git rev-parse --show-toplevel)

# Define the log file path relative to the repo directory
LOG_FILE="$REPO_DIR/install_nginx.log"

# Function to log messages to both console and log file
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Start logging
log "Starting Nginx and FileZilla Server installation script."

# Ensure Homebrew is installed
echo "Checking if Homebrew is installed..."
log "Checking if Homebrew is installed."
if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Installing Homebrew..."
  log "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ $? -ne 0 ]; then
    log "Failed to install Homebrew."
    exit 1
  fi
else
  echo "Homebrew is already installed."
  log "Homebrew is already installed."
fi

# Define the directory path
DIR="/usr/local/var/www/"

# Check if the directory exists
if [ ! -d "$DIR" ]; then
  echo "Directory $DIR not found. Creating it..."
  log "Directory $DIR not found. Creating it..."
  sudo mkdir -p "$DIR"
  echo "Directory $DIR created successfully."
  log "Directory $DIR created successfully."
else
  echo "Directory $DIR already exists."
  log "Directory $DIR already exists."
fi

# Set permissions and ownership
echo "Setting permissions and ownership for $DIR..."
log "Setting permissions and ownership for $DIR..."
sudo chmod -R 775 "$DIR"
sudo chown -R $USER "$DIR"
echo "Permissions and ownership set successfully for $DIR."
log "Permissions and ownership set successfully for $DIR."

# Install Nginx using Homebrew
echo "Installing Nginx..."
log "Installing Nginx..."
if ! brew install nginx; then
  log "Failed to install Nginx."
  exit 1
fi

# Replace the default Nginx configuration with the one from GitHub
echo "Copying custom Nginx config..."
log "Copying custom Nginx config..."
sudo cp "$REPO_DIR/nginx.conf" /opt/homebrew/etc/nginx/nginx.conf
if [ $? -ne 0 ]; then
  log "Failed to copy nginx.conf."
  exit 1
fi

sudo cp "$REPO_DIR/default.conf" /opt/homebrew/etc/nginx/servers/default
if [ $? -ne 0 ]; then
  log "Failed to copy default.conf."
  exit 1
fi

echo "Custom Nginx configuration copied successfully."
log "Custom Nginx configuration copied successfully."

# Test the configuration for syntax errors
echo "Testing Nginx configuration..."
log "Testing Nginx configuration..."
sudo nginx -t
if [ $? -ne 0 ]; then
  log "Nginx configuration test failed."
  exit 1
fi

# Restart Nginx to apply changes
echo "Restarting Nginx..."
log "Restarting Nginx..."
sudo nginx -s reload
if [ $? -ne 0 ]; then
  log "Failed to reload Nginx."
  exit 1
fi

# Enable Nginx to start on boot (macOS-specific)
echo "Enabling Nginx to start on boot..."
log "Enabling Nginx to start on boot..."
sudo brew services start nginx
if [ $? -ne 0 ]; then
  log "Failed to enable Nginx to start on boot."
  exit 1
fi

echo "Nginx setup is complete!"
log "Nginx setup is complete!"


# Define the download URL and download location for FileZilla
FILEZILLA_URL="https://dl3.cdn.filezilla-project.org/server/FileZilla_Server_1.9.4_macos-arm64.pkg?h=-u7CEaIjMa1hOAuFXutdQg&x=1731356532"
PKG_PATH="$HOME/Downloads/FileZilla_Server.pkg"
FILEZILLA_INSTALL_PATH="/Applications/FileZilla Server.app"

# Check if the package exists at the given path
if [ -f "$PKG_PATH" ]; then
  echo "Package found at $PKG_PATH"
else
  echo "Package not found at $PKG_PATH. Downloading..."
  
  # Download the FileZilla Server package with the updated URL and handle redirects
  curl -L -o "$PKG_PATH" "$FILEZILLA_URL"
  
  # Verify if download was successful
  if [ -f "$PKG_PATH" ]; then
    echo "Package downloaded successfully to $PKG_PATH"
  else
    echo "Failed to download FileZilla Server package."
    exit 1
  fi
fi

# Set permissions and ownership for the FileZilla package
echo "Setting permissions and ownership for FileZilla Server package..."
sudo chmod 644 "$PKG_PATH"
sudo chown "$USER" "$PKG_PATH"

# Now install FileZilla Server if it is not already installed
if [ ! -d "$FILEZILLA_INSTALL_PATH" ]; then
  echo "Installing FileZilla Server..."
  sudo installer -pkg "$PKG_PATH" -target /

  if [ $? -eq 0 ]; then
    echo "FileZilla Server installed successfully."
  else
    echo "Failed to install FileZilla Server."
    exit 1
  fi
else
  echo "FileZilla Server is already installed."
fi

# Check if FileZilla Server exists in the /Applications folder
echo "Checking for FileZilla Server in /Applications folder..."
FILEZILLA_PATH="/Applications/FileZilla Server.app"

if [ ! -d "$FILEZILLA_PATH" ]; then
  echo "FileZilla Server was not installed correctly. Please check the installation."
  exit 1
else
  echo "FileZilla Server found at $FILEZILLA_PATH"
fi

# Start FileZilla Server after installation
echo "Starting FileZilla Server..."
open -a "$FILEZILLA_PATH"

# Run merge_epg.py script after installation of FileZilla Server
echo "Running merge_epg.py script..."
log "Running merge_epg.py script..."
python3 "$REPO_DIR/merge_epg.py"

if [ $? -eq 0 ]; then
  echo "merge_epg.py executed successfully."
  log "merge_epg.py executed successfully."
else
  echo "Failed to execute merge_epg.py."
  log "Failed to execute merge_epg.py."
  exit 1
fi

echo "FileZilla Server installation and start completed."

# Define the path to the plist file from the repo
PLIST_FILE="$REPO_DIR/com.filezilla_server.plist"

# Check if the plist file exists in the repo
if [ -f "$PLIST_FILE" ]; then
  echo "Copying plist file from repository to ~/Library/LaunchAgents..."
  cp "$PLIST_FILE" ~/Library/LaunchAgents/com.filezilla.server.plist

  # Load the plist to ensure FileZilla starts on boot
  echo "Loading plist file to start FileZilla Server on login..."
  launchctl load ~/Library/LaunchAgents/com.filezilla.server.plist

  echo "FileZilla Server will now start on login."
else
  echo "Plist file not found in the repository. Please ensure the filezilla_server.plist exists at the root of the repo."
  exit 1
fi