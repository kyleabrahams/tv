#!/bin/bash

# Update package list and install Nginx
echo "Updating package list..."
sudo apt-get update

echo "Installing Nginx..."
sudo apt-get install -y nginx

# Replace the default Nginx configuration with the one from GitHub
echo "Copying custom Nginx config..."
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo cp default.conf /etc/nginx/sites-available/default

# Test the configuration for syntax errors
echo "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx to apply changes
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Enable Nginx to start on boot
echo "Enabling Nginx to start on boot..."
sudo systemctl enable nginx

echo "Nginx setup is complete!"
