import os
import subprocess
import sys
from datetime import datetime
import venv
import logging
import time
import subprocess
import requests

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
LOG_FILE = os.path.join(LOG_DIR, "install_nginx.log")
NGINX_CONF = os.path.join(REPO_DIR, "nginx.conf")
WWW_DIR = os.path.join(REPO_DIR, "www")
NGINX_CONF_DIR = "/usr/local/etc/nginx"  # Adjust if necessary based on your setup
EPG_FILE = os.path.join(WWW_DIR, "epg.xml")

# Ensure necessary directories exist
for directory in [LOG_DIR, WWW_DIR, NGINX_CONF_DIR]:
    os.makedirs(directory, exist_ok=True)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger()

def log(message):
    """Log to console and file."""
    logger.info(message)

# Example usage
if __name__ == "__main__":
    log("Starting Nginx installation process...")
    # Add other script logic here
    log("Installation complete.")

# --- Utilities ---
def run_command(command, check=True, real_time=False):
    """Run a shell command and log its output."""
    try:
        if real_time:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                log(line.strip())
            process.wait()
            if process.returncode != 0:
                log(f"Error: {process.stderr.read().strip()}")
            return process.returncode
        else:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            if check and result.returncode != 0:
                log(f"Command failed: {command}\n{result.stderr}")
                sys.exit(1)
            if result.stdout:
                log(result.stdout.strip())
            return result.stdout
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

def install_requests_in_venv(venv_dir):
    """Ensure 'requests' module is installed in the virtual environment."""
    log("Checking if 'requests' is installed in the virtual environment...")
    pip_path = './venv/bin/pip'

    if not os.path.exists(pip_path):
        log(f"pip not found in {pip_path}. Attempting to ensure pip is installed.")
        # Ensure pip is installed if missing
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)

    try:
        subprocess.run([pip_path, "install", "requests"], check=True)
        log("Requests installed successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Error installing requests: {e}")
        sys.exit(1)


def setup_nginx_config():
    """Set up Nginx with custom configuration."""
    if not os.path.exists(NGINX_CONF):
        log("Custom nginx.conf not found!")
        sys.exit(1)
    destination_conf = os.path.join(NGINX_CONF_DIR, "nginx.conf")
    run_command(f"sudo cp {NGINX_CONF} {destination_conf}")
    log(f"Custom Nginx configuration copied to {destination_conf}.")
    # Set correct file permissions for Nginx to access it
    run_command(f"sudo chmod 644 {destination_conf}")
    log(f"Permissions set for {destination_conf}.")

def setup_directories():
    """Ensure required directories exist and set correct permissions."""
    os.makedirs(WWW_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    log(f"Directories {WWW_DIR} and {LOG_DIR} created or verified.")
    # Ensure directories have proper permissions
    run_command(f"chmod -R 755 {WWW_DIR}")
    run_command(f"chmod -R 755 {LOG_DIR}")
    log(f"Permissions set for {WWW_DIR} and {LOG_DIR}.")
    
    # Set permissions recursively for the www directory (for Nginx to access files)
    run_command(f"sudo chmod -R 755 {WWW_DIR}")

def set_permissions_for_epg():
    """Create an empty epg.xml if it doesn't exist, ensure the www directory exists, and set permissions."""
    epg_file_path = os.path.join(WWW_DIR, "epg.xml")
    
    # Ensure the www directory exists
    if not os.path.exists(WWW_DIR):
        log(f"{WWW_DIR} not found. Creating the directory...")
        os.makedirs(WWW_DIR)  # Create the directory if it doesn't exist
        log(f"Directory {WWW_DIR} created.")
    
    # Check if the epg.xml file exists
    if not os.path.exists(epg_file_path):
        log(f"{epg_file_path} not found. Creating an empty file...")
        
        # Create an empty epg.xml file with basic XML structure
        with open(epg_file_path, 'w') as epg_file:
            epg_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<epg></epg>")  # Basic empty XML structure
        
        log(f"Empty {epg_file_path} created.")
    
    # Now set permissions for the epg.xml file (644: owner can read/write, others can read)
    run_command(f"sudo chmod 644 {epg_file_path}")
    log(f"Permissions set for {epg_file_path}.")

def setup_virtualenv():
    """Set up Python virtual environment."""
    venv_dir = os.path.join(REPO_DIR, "venv")
    if not os.path.exists(venv_dir):
        log("Creating virtual environment...")
        venv.EnvBuilder(clear=True).create(venv_dir)
        log("Virtual environment created.")
    run_command(f"chmod -R 755 {venv_dir}")
    
    # Ensure requests is installed
    install_requests_in_venv(venv_dir)

def install_requests_in_venv(venv_dir):
    """Ensure 'requests' module is installed in the virtual environment."""
    log("Checking if 'requests' is installed in the virtual environment...")
    pip_path = os.path.join(venv_dir, "bin", "pip")

    # Check if pip is available
    if not os.path.exists(pip_path):
        log(f"pip not found in {pip_path}. Attempting to ensure pip is installed.")
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)

    # Now install the requests package
    try:
        subprocess.run([pip_path, "install", "requests"], check=True)
        log("Requests installed successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Error installing requests: {e}")
        sys.exit(1)

def setup_cron_jobs():
    """Set up cron jobs."""
    log("Setting up cron jobs...")
    cron_jobs = [
        f"0 1,13 * * * source {REPO_DIR}/venv/bin/activate && python3 {REPO_DIR}/merge_epg.py >> {LOG_DIR}/merge_cron.log 2>&1",
        f"0 */6 * * * nginx -s reload >> {LOG_DIR}/nginx_reload.log 2>&1",
        f"* * * * * echo 'Cron test at $(date)' >> {LOG_DIR}/cron_test.log"
    ]
    current_cron = run_command("crontab -l", check=False).strip()
    for job in cron_jobs:
        if job not in current_cron:
            current_cron += f"\n{job}"
    with open("/tmp/crontab.tmp", "w") as f:
        f.write(current_cron + "\n")
    run_command("crontab /tmp/crontab.tmp")
    log("Cron jobs set up successfully.")

def prompt_run_merge_epg():
    """Optionally run the merge_epg.py script."""
    response = input("Do you want to run merge_epg.py now? (y/n): ").strip().lower()
    if response == 'y':
        log("Running merge_epg.py...")
        run_command(f"source {REPO_DIR}/venv/bin/activate && python3 {REPO_DIR}/merge_epg.py", real_time=True)

def reload_nginx():
    """Reload Nginx."""
    log("Reloading Nginx...")
    try:
        # Using brew to restart nginx service
        run_command("brew services restart nginx")
        log("Nginx reloaded successfully.")
    except Exception as e:
        log(f"Failed to reload Nginx: {e}")
        sys.exit(1)

def provide_epg_xml_link():
    """Provide the link to the epg.xml file."""
    url = "http://localhost:8080/epg.xml"
    log(f"EPG XML is available at: {url}")
    print(f"EPG XML is available at: {url}")

if __name__ == "__main__":
    install_homebrew()
    install_nginx()
    setup_nginx_config()
    setup_directories()
    set_permissions_for_epg()
    setup_virtualenv()  # This ensures 'requests' is installed
    setup_cron_jobs()
    prompt_run_merge_epg()
    reload_nginx()
