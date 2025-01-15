import os
import subprocess
import sys
from datetime import datetime
import venv
import logging

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script for installing Nginx
# python3 install_nginx.py

## Reload Nginx
# brew services restart nginx
# sudo brew services stop nginx

## Stop Nginx pids
# sudo brew services stop nginx

# Test url in Terminal
# curl -I http://localhost:8080/epg.xml 
# curl http://localhost:8080/epg.xml 


# sudo nginx -s stop
# sudo nginx

# --- Constants ---
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # Directory of this script
LOG_DIR = os.path.join(REPO_DIR, "log")
NGINX_CONF = os.path.join(REPO_DIR, "nginx.conf")
WWW_DIR = os.path.join(REPO_DIR, "www")
EPG_FILE = os.path.join(WWW_DIR, "epg.xml")
VENVS_DIR = os.path.join(REPO_DIR, "venv")

# --- Logging Setup ---
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "setup.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def log(message):
    """Log to console and file."""
    logger.info(message)

def run_command(command, check=True):
    """Run a shell command and handle output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if check and result.returncode != 0:
            log(f"Command failed: {command}\n{result.stderr}")
            sys.exit(1)
        if result.stdout:
            log(result.stdout.strip())
        return result.stdout.strip()
    except Exception as e:
        log(f"Exception running command: {command}\n{e}")
        sys.exit(1)

def fix_homebrew_permissions():
    """Fix Homebrew directory permissions to ensure proper access."""
    homebrew_dir = "/opt/homebrew"
    if os.path.exists(homebrew_dir):
        log(f"Fixing permissions for {homebrew_dir}...")
        # Fix permissions to the current user
        run_command(f"sudo chown -R $(whoami):admin {homebrew_dir}")
        log(f"Permissions fixed for {homebrew_dir}.")
    else:
        log(f"Homebrew directory {homebrew_dir} not found.")

def install_homebrew():
    """Ensure Homebrew is installed."""
    if run_command("command -v brew", check=False).strip() == "":
        log("Installing Homebrew...")
        # Run Homebrew installation without sudo
        run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    else:
        log("Homebrew is already installed.")
    
    # Fix ownership issues for Homebrew directories (without sudo)
    fix_homebrew_permissions()
    log("Homebrew installation or permissions check completed.")

def install_nginx():
    """Install or update Nginx."""
    log("Installing or updating Nginx...")
    # Removed sudo to avoid root execution
    run_command("brew install nginx")

def setup_nginx_config():
    """Set up Nginx configuration."""
    nginx_conf_dir = "/opt/homebrew/etc/nginx"
    os.makedirs(nginx_conf_dir, exist_ok=True)
    destination_conf = os.path.join(nginx_conf_dir, "nginx.conf")
    run_command(f"cp {NGINX_CONF} {destination_conf}")
    log(f"Copied Nginx configuration to {destination_conf}.")
    run_command(f"chmod 644 {destination_conf}")
    log(f"Permissions set for {destination_conf}.")

def setup_virtualenv():
    """Set up Python virtual environment."""
    if not os.path.exists(VENVS_DIR):
        log("Creating virtual environment...")
        venv.EnvBuilder(clear=True).create(VENVS_DIR)
    run_command(f"chmod -R 755 {VENVS_DIR}")
    pip_path = os.path.join(VENVS_DIR, "bin", "pip")
    run_command(f"{pip_path} install --upgrade pip")
    run_command(f"{pip_path} install requests")
    log("Virtual environment set up.")

def setup_directories_and_epg():
    """Set up directories and default EPG file."""
    os.makedirs(WWW_DIR, exist_ok=True)
    if not os.path.exists(EPG_FILE):
        with open(EPG_FILE, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<epg></epg>')
        log(f"Created empty EPG file at {EPG_FILE}.")
    run_command(f"chmod 644 {EPG_FILE}")  # Apply correct permissions
    log(f"Permissions set for {EPG_FILE}.")

def reload_nginx():
    """Reload Nginx."""
    log("Reloading Nginx...")
    run_command("brew services restart nginx")
    log("Nginx reloaded successfully.")

# --- Main Script ---
def main():
    log("Starting setup process...")
    try:
        install_homebrew()
        install_nginx()
        setup_nginx_config()
        setup_virtualenv()
        setup_directories_and_epg()
        reload_nginx()
        log("Setup complete. Access EPG XML at http://localhost:8080/epg.xml")
    except Exception as e:
        log(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()