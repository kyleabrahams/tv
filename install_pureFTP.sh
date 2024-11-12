#!/bin/bash

# Check if Homebrew is installed
echo "Checking if Homebrew is installed..."
if ! command -v brew &>/dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Install Pure-FTPd
echo "Installing Pure-FTPd..."
brew install pure-ftpd

# Set FTP root directory to /usr/local/var/www
ftp_dir="/usr/local/var/www"
echo "Setting FTP root directory to $ftp_dir..."

# Ensure the FTP root directory exists
echo "Checking if FTP directory exists at $ftp_dir..."
if [ ! -d "$ftp_dir" ]; then
    sudo mkdir -p "$ftp_dir"
    sudo chmod 755 "$ftp_dir"
    echo "FTP directory created at $ftp_dir."
else
    echo "FTP root directory already exists at $ftp_dir."
fi

# Ensure the configuration directory exists at /opt/homebrew/etc/pure-ftpd
config_dir="/opt/homebrew/etc/pure-ftpd"
echo "Checking if configuration directory exists at $config_dir..."
if [ ! -d "$config_dir" ]; then
    sudo mkdir -p "$config_dir"
    sudo chown $(whoami):admin "$config_dir"
    echo "Created directory $config_dir."
else
    echo "Configuration directory already exists at $config_dir."
fi

# Create and configure Pure-FTPd configuration file if it does not exist
config_file="$config_dir/pure-ftpd.conf"
if [ ! -f "$config_file" ]; then
    echo "Creating Pure-FTPd configuration file..."
    sudo touch "$config_file"

    echo "Adding basic configuration to Pure-FTPd configuration file..."
    sudo bash -c "cat <<EOF > $config_file
# Pure-FTPd Configuration
ChrootEveryone yes
NoAnonymous yes
PAMAuthentication yes
UnixAuthentication yes
PureDB /opt/homebrew/etc/pure-ftpd/pureftpd.pdb
PassivePortRange 30000 35000
EOF"

    echo "Pure-FTPd configuration file created and configured at $config_file."
else
    echo "Pure-FTPd configuration file already exists at $config_file."
    echo "Backing up the existing configuration file..."
    sudo cp "$config_file" "${config_file}.bak"
fi

# Prompt for FTP username and password
read -p "Enter a username for FTP access: " ftp_user
read -sp "Enter a password for FTP access: " ftp_pass
echo  # Newline for better formatting

# Add or update FTP user with the specified root directory
if sudo pure-pw show "$ftp_user" &>/dev/null; then
    echo "Updating FTP user $ftp_user with new root directory..."
    echo "$ftp_pass" | sudo pure-pw usermod "$ftp_user" -d "$ftp_dir"
else
    echo "Adding new FTP user $ftp_user..."
    echo "$ftp_pass" | sudo pure-pw useradd "$ftp_user" -u $(whoami) -d "$ftp_dir" -m
fi

# Update the PureDB
echo "Updating PureDB..."
sudo pure-pw mkdb

# Create a LaunchAgent plist to start Pure-FTPd at login
plist_path=~/Library/LaunchAgents/homebrew.mxcl.pure-ftpd.plist

echo "Creating LaunchAgent plist to start Pure-FTPd at login..."
cat <<EOF > "$plist_path"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>homebrew.mxcl.pure-ftpd</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/opt/pure-ftpd/sbin/pure-ftpd</string>
        <string>--daemonize</string>
        <string>--config</string>
        <string>/opt/homebrew/etc/pure-ftpd/pure-ftpd.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Set correct permissions and load LaunchAgent
echo "Setting correct permissions for the LaunchAgent..."
chmod 644 "$plist_path"

echo "Loading the LaunchAgent plist..."
launchctl unload "$plist_path" &>/dev/null # Unload if already loaded
launchctl load "$plist_path"

# Get the public IP address
public_ip=$(curl -s http://checkip.amazonaws.com)

# FTP port (default is 21, but you can change it if needed)
ftp_port=21

# Print the public FTP server URL with the port number
echo "Pure-FTPd installed and configured. FTP directory is $ftp_dir."
echo "Your public FTP server URL is: ftp://$public_ip:$ftp_port"
echo "You can now access the server using the username: $ftp_user"

# Create and configure Pure-FTPd configuration file if it does not exist
config_file="$config_dir/pure-ftpd.conf"
if [ ! -f "$config_file" ]; then
    echo "Creating Pure-FTPd configuration file..."
    sudo touch "$config_file"

    echo "Adding basic configuration to Pure-FTPd configuration file..."
    sudo bash -c "cat <<EOF > $config_file
# Pure-FTPd Configuration
ChrootEveryone yes
NoAnonymous yes
PAMAuthentication yes
UnixAuthentication yes
PureDB /opt/homebrew/etc/pure-ftpd/pureftpd.pdb
PassivePortRange 30000 35000
EOF"

    echo "Pure-FTPd configuration file created and configured at $config_file."
else
    echo "Pure-FTPd configuration file already exists at $config_file."
    echo "Backing up the existing configuration file..."
    sudo cp "$config_file" "${config_file}.bak"
fi

# Prompt for FTP username and password
read -p "Enter a username for FTP access: " ftp_user
read -sp "Enter a password for FTP access: " ftp_pass
echo  # Newline for better formatting

# Add or update FTP user with the specified root directory
if sudo pure-pw show "$ftp_user" &>/dev/null; then
    echo "Updating FTP user $ftp_user with new root directory..."
    echo "$ftp_pass" | sudo pure-pw usermod "$ftp_user" -d "$ftp_dir"
else
    echo "Adding new FTP user $ftp_user..."
    echo "$ftp_pass" | sudo pure-pw useradd "$ftp_user" -u $(whoami) -d "$ftp_dir" -m
fi

# Update the PureDB
echo "Updating PureDB..."
sudo pure-pw mkdb

# Create a LaunchAgent plist to start Pure-FTPd at login
plist_path=~/Library/LaunchAgents/homebrew.mxcl.pure-ftpd.plist

echo "Creating LaunchAgent plist to start Pure-FTPd at login..."
cat <<EOF > "$plist_path"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>homebrew.mxcl.pure-ftpd</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/opt/pure-ftpd/sbin/pure-ftpd</string>
        <string>--daemonize</string>
        <string>--config</string>
        <string>/opt/homebrew/etc/pure-ftpd/pure-ftpd.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Set correct permissions and load LaunchAgent
echo "Setting correct permissions for the LaunchAgent..."
chmod 644 "$plist_path"

echo "Loading the LaunchAgent plist..."
launchctl unload "$plist_path" &>/dev/null # Unload if already loaded
launchctl load "$plist_path"

# Get the public IP address
public_ip=$(curl -s http://checkip.amazonaws.com)

# FTP port (default is 21, but you can change it if needed)
ftp_port=21

# Print the public FTP server URL with the port number
echo "Pure-FTPd installed and configured. FTP directory is $ftp_dir."
echo "Your public FTP server URL is: ftp://$public_ip:$ftp_port"
echo "You can now access the server using the username: $ftp_user"
