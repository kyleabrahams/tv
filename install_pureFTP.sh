#!/bin/bash

# Prompt for permission
read -p "Do you want to install and configure Pure-FTPd? (yes/no): " response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')  # Convert to lowercase
if [[ "$response" != "yes" && "$response" != "y" ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Ensure Homebrew is installed
if ! command -v brew &>/dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Install Pure-FTPd
echo "Installing Pure-FTPd..."
brew install pure-ftpd

# Create FTP directory
ftp_dir="/Users/$(whoami)/ftp_root"
mkdir -p "$ftp_dir"
chmod 755 "$ftp_dir"

# Configure Pure-FTPd
echo "Configuring Pure-FTPd..."
sudo cp /opt/homebrew/etc/pure-ftpd/pure-ftpd.conf /opt/homebrew/etc/pure-ftpd/pure-ftpd.conf.bak
sudo bash -c 'cat <<EOF > /opt/homebrew/etc/pure-ftpd/pure-ftpd.conf
# Pure-FTPd Configuration
ChrootEveryone yes
NoAnonymous yes
PAMAuthentication yes
UnixAuthentication yes
PureDB /opt/homebrew/etc/pure-ftpd/pureftpd.pdb
PassivePortRange 30000 35000
EOF'

# Create a new user for FTP
read -p "Enter a username for FTP access: " ftp_user
sudo pure-pw useradd $ftp_user -u $(whoami) -d "$ftp_dir"
sudo pure-pw mkdb

# Start Pure-FTPd
echo "Starting Pure-FTPd..."
brew services start pure-ftpd

echo "Pure-FTPd installed and configured. FTP directory is $ftp_dir."
echo "You can now access the server using the username: $ftp_user"
