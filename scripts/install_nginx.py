import os
import subprocess
import sys
from datetime import datetime
import venv
import logging
import time  # Ensure the time module is imported

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
LAST_RUN_FILE = f"{LOG_DIR}/merge_epg_last_run.txt" # Dec 11 2024
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB in bytes


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
    from datetime import datetime
    print(f"{datetime.now()} - {message}")

def run_command(command, check=True, fail_silently=False, real_time=False):
    """
    Run a shell command and handle output.

    Parameters:
        command (str): The shell command to execute.
        check (bool): Whether to check the return code and raise an error if it fails.
        fail_silently (bool): If True, log errors without exiting the script.
        real_time (bool): If True, stream the output in real-time.

    Returns:
        str: The standard output of the command.
    """
    try:
        if real_time:
            process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in process.stdout:
                log(line.strip())
            process.stdout.close()
            return_code = process.wait()
            if check and return_code != 0:
                raise subprocess.CalledProcessError(return_code, command, output=None, stderr=process.stderr.read())
        else:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
            if result.stdout:
                log(result.stdout.strip())
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed: {command}\nExit Code: {e.returncode}\nError Output: {e.stderr.strip()}"
        log(error_message)
        if not fail_silently:
            sys.exit(1)
    except Exception as e:
        log(f"Exception running command: {command}\n{e}")
        if not fail_silently:
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

def should_prompt_run_merge_epg():
    """
    Check if merge_epg.py cron job was executed recently,
    if the EPG file is missing, or if the EPG file is smaller than 1MB.
    """
    try:
        # Check if the EPG file exists
        if not os.path.exists(EPG_FILE):
            log(f"{EPG_FILE} not found. Prompting user to run merge_epg.py.")
            return True
        
        # Check the file size
        if os.path.getsize(EPG_FILE) < MAX_FILE_SIZE:
            log(f"{EPG_FILE} is smaller than 1MB. Prompting user to run merge_epg.py.")
            return True

        # Check the last run timestamp
        if not os.path.exists(LAST_RUN_FILE):
            log("Last run timestamp file not found. Prompting user to run merge_epg.py.")
            return True
        
        with open(LAST_RUN_FILE, "r") as f:
            last_run_timestamp = int(f.read().strip())
        
        # Check if the last execution was more than 12 hours ago
        twelve_hours_ago = int(time.time()) - 12 * 3600
        if last_run_timestamp < twelve_hours_ago:
            log("Last run was over 12 hours ago. Prompting user to run merge_epg.py.")
            return True
    except Exception as e:
        log(f"Error checking conditions: {e}. Prompting user to run merge_epg.py.")
        return True  # Assume the need to run in case of error

    # No need to prompt
    return False

def prompt_run_merge_epg():
    """Optionally run the merge_epg.py script if the previous cron job wasn't executed."""
    if should_prompt_run_merge_epg():
        response = input("Do you want to run merge_epg.py now? (y/n): ").strip().lower()
        if response == 'y':
            log("Running merge_epg.py...")
            run_command(f"source {REPO_DIR}/venv/bin/activate && python3 {REPO_DIR}/merge_epg.py && echo $(date +%s) > {LAST_RUN_FILE}", real_time=True)
            log("merge_epg.py executed.")
        else:
            log("User chose not to run merge_epg.py.")
    else:
        log("Cron job has been executed recently. No need to prompt.")

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
        setup_cron_jobs()
        prompt_run_merge_epg()
        reload_nginx()
        log("Setup complete. Access EPG XML at http://localhost:8080/epg.xml")
    except Exception as e:
        log(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()