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

# Define the directory paths
DIR="/usr/local/var/www/"
RUN_DIR="/usr/local/var/run/"
PID_FILE="$RUN_DIR/nginx.pid"

# Check if the www directory exists
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

# Set permissions and ownership for the www directory
echo "Setting permissions and ownership for $DIR..."
log "Setting permissions and ownership for $DIR..."
sudo chmod -R 775 "$DIR"
sudo chown -R $USER "$DIR"
echo "Permissions and ownership set successfully for $DIR."
log "Permissions and ownership set successfully for $DIR."

# Check if the run directory exists
if [ ! -d "$RUN_DIR" ]; then
  echo "Directory $RUN_DIR not found. Creating it..."
  log "Directory $RUN_DIR not found. Creating it..."
  sudo mkdir -p "$RUN_DIR"
  echo "Directory $RUN_DIR created successfully."
  log "Directory $RUN_DIR created successfully."
fi

# Set permissions for the run directory
echo "Setting permissions for $RUN_DIR..."
log "Setting permissions for $RUN_DIR..."
sudo chown -R $USER "$RUN_DIR"
sudo chmod 775 "$RUN_DIR"
echo "Permissions set successfully for $RUN_DIR."
log "Permissions set successfully for $RUN_DIR."

# Ensure the PID file exists and is writable
if [ ! -f "$PID_FILE" ]; then
  echo "Creating the missing PID file..."
  sudo touch "$PID_FILE"
  sudo chmod 664 "$PID_FILE"
  sudo chown $USER "$PID_FILE"
  echo "PID file created and permissions set."
  log "PID file created and permissions set."
fi

# Install Nginx using Homebrew
echo "Installing Nginx..."
log "Installing Nginx..."
if ! brew install nginx; then
  log "Failed to install Nginx."
  exit 1
fi

# Copy custom Nginx configuration
echo "Copying custom Nginx config..."
# Adjusting paths for Homebrew installation of Nginx on macOS (both Intel and Apple Silicon)
sudo cp "$REPO_DIR/nginx.conf" "$HOMEBREW_PREFIX/etc/nginx/nginx.conf"
if [ $? -ne 0 ]; then
  log "Failed to copy nginx.conf."
  exit 1
fi

sudo cp "$REPO_DIR/default.conf" "$HOMEBREW_PREFIX/etc/nginx/servers/default"
if [ $? -ne 0 ]; then
  log "Failed to copy default.conf."
  exit 1
fi

echo "Custom Nginx configuration copied successfully."

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

# Merge the EPG data using the merge_epg.py script
echo "Running merge_epg.py script..."
log "Running merge_epg.py script..."

# Ensure Python is installed and running the script
if ! command -v python3 &> /dev/null; then
  log "Python 3 is not installed. Please install it first."
  exit 1
fi

# Run the merge_epg.py script
python3 "$REPO_DIR/scripts/merge_epg.py"
if [ $? -ne 0 ]; then
  log "Failed to execute merge_epg.py."
  exit 1
fi

echo "EPG data merged successfully."
log "EPG data merged successfully."

echo "Nginx and FileZilla Server setup is complete!"
log "Nginx and FileZilla Server setup is complete!"
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

echo "FileZilla Server installation and start completed."

# --- Copy the pre-existing plist file from the repo root to launch FileZilla on startup ---

# Define the path to the plist file from the repo
PLIST_FILE="$REPO_DIR/filezilla_server.plist"

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
