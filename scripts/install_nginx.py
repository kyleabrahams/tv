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

## Stop Nginx pids
# sudo brew services stop nginx

# sudo nginx -s stop
# sudo nginx


# --- Constants ---
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # Directory of this script
LOG_DIR = os.path.join(REPO_DIR, "log")
NGINX_CONF = os.path.join(REPO_DIR, "nginx.conf")
WWW_DIR = os.path.join(REPO_DIR, "www")
EPG_FILE = os.path.join(WWW_DIR, "epg.xml")
VENVS_DIR = os.path.join(REPO_DIR, "venv")

# Ensure necessary directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(WWW_DIR, exist_ok=True)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "setup.log")),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger()

# --- Utilities ---
def log(message):
    """Log messages to console and file."""
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

# --- Setup Functions ---
def install_homebrew():
    """Ensure Homebrew is installed."""
    if run_command("command -v brew", check=False).strip() == "":
        log("Installing Homebrew...")
        run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    else:
        log("Homebrew is already installed.")

def install_nginx():
    """Install or update Nginx."""
    log("Installing or updating Nginx...")
    run_command("brew install nginx")

def setup_nginx_config():
    """Copy custom Nginx configuration."""
    # Try to get the Nginx configuration path automatically
    nginx_conf_path = run_command("nginx -V 2>&1 | grep --only-matching --perl-regexp 'conf-path=[^ ]*' | cut -d= -f2").strip()

    if not nginx_conf_path:
        log("Nginx configuration path not found automatically.")
        # Suggest a default path and create it
        default_path = "/opt/homebrew/etc/nginx/nginx.conf"
        nginx_conf_dir = os.path.dirname(default_path)
        
        # Create the directory automatically
        os.makedirs(nginx_conf_dir, exist_ok=True)
        log(f"Directory {nginx_conf_dir} created.")

        nginx_conf_path = default_path

    # The configuration directory is the parent directory of the conf-path
    nginx_conf_dir = os.path.dirname(nginx_conf_path)

    # Ensure the Nginx directory exists
    if not os.path.exists(nginx_conf_dir):
        log(f"Nginx configuration directory not found: {nginx_conf_dir}")
        
        # Automatically create the directory without asking
        os.makedirs(nginx_conf_dir, exist_ok=True)
        log(f"Directory {nginx_conf_dir} created.")

    # Copy the custom configuration
    destination_conf = os.path.join(nginx_conf_dir, "nginx.conf")
    run_command(f"sudo cp {NGINX_CONF} {destination_conf}")
    log(f"Custom Nginx configuration copied to {destination_conf}.")
    run_command(f"sudo chmod 644 {destination_conf}")
    log(f"Permissions set for {destination_conf}.")

    # Copy the custom configuration
    destination_conf = os.path.join(nginx_conf_dir, "nginx.conf")
    run_command(f"sudo cp {NGINX_CONF} {destination_conf}")
    log(f"Custom Nginx configuration copied to {destination_conf}.")
    run_command(f"sudo chmod 644 {destination_conf}")
    log(f"Permissions set for {destination_conf}.")

def setup_virtualenv():
    """Set up Python virtual environment."""
    if not os.path.exists(VENVS_DIR):
        log("Creating virtual environment...")
        venv.EnvBuilder(clear=True).create(VENVS_DIR)
    run_command(f"chmod -R 755 {VENVS_DIR}")
    
    # Ensure pip is available
    pip_path = os.path.join(VENVS_DIR, "bin", "pip")
    run_command(f"{pip_path} install --upgrade pip")  # Upgrade pip if necessary
    run_command(f"{pip_path} install requests")  # Install required packages
    log("Virtual environment set up and 'requests' installed.")

def setup_directories_and_epg():
    """Ensure directories and permissions for www and epg.xml."""
    os.makedirs(WWW_DIR, exist_ok=True)
    if not os.path.exists(EPG_FILE):
        with open(EPG_FILE, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<epg></epg>')
        log(f"Empty {EPG_FILE} created.")
    run_command(f"sudo chmod 644 {EPG_FILE}")
    log(f"Permissions set for {EPG_FILE}.")

def reload_nginx():
    """Reload Nginx."""
    log("Reloading Nginx...")
    run_command("brew services restart nginx")
    log("Nginx reloaded successfully.")

def setup_cron_jobs():
    """Set up cron jobs."""
    log("Setting up cron jobs...")
    cron_jobs = [
        f"0 1,13 * * * source {VENVS_DIR}/bin/activate && python3 {REPO_DIR}/merge_epg.py >> {LOG_DIR}/merge_cron.log 2>&1",
        f"0 */6 * * * nginx -s reload >> {LOG_DIR}/nginx_reload.log 2>&1",
    ]
    current_cron = run_command("crontab -l", check=False)
    for job in cron_jobs:
        if job not in current_cron:
            current_cron += f"\n{job}"
    with open("/tmp/crontab.tmp", "w") as f:
        f.write(current_cron)
    run_command("crontab /tmp/crontab.tmp")
    log("Cron jobs set up successfully.")

# --- Main Logic ---
if __name__ == "__main__":
    log("Starting setup process...")
    install_homebrew()
    install_nginx()
    setup_nginx_config()
    setup_virtualenv()
    setup_directories_and_epg()
    setup_cron_jobs()
    reload_nginx()
    log("Setup complete. You can access EPG XML at http://localhost:8080/epg.xml")
