import os
import subprocess
import sys
from datetime import datetime
import venv

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script for installing Nginx
# python3 install_nginx.py


# Constants
REPO_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_FILE = os.path.join(REPO_DIR, "install_nginx.log")
NGINX_CONF_DIR = "/opt/homebrew/etc/nginx"
WWW_DIR = "/usr/local/var/www"
LOG_DIR = os.path.join(REPO_DIR, "log")


def log(message):
    """Log messages to both the console and a log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")


def run_command(command, check=True):
    """Run a shell command and optionally check for errors."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if check and result.returncode != 0:
            log(f"Command failed: {command}\n{result.stderr}")
            sys.exit(1)
        return result.stdout
    except Exception as e:
        log(f"Exception running command: {command}\n{e}")
        sys.exit(1)


def install_homebrew():
    """Ensure Homebrew is installed."""
    if run_command("command -v brew", check=False).strip() == "":
        log("Installing Homebrew...")
        run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    else:
        log("Homebrew is already installed.")


def install_nginx():
    """Install or update Nginx using Homebrew."""
    log("Installing or updating Nginx...")
    run_command("brew install nginx")


def setup_nginx_config():
    """Set up custom Nginx configuration."""
    nginx_conf = os.path.join(REPO_DIR, "nginx.conf")
    if not os.path.exists(nginx_conf):
        log("Custom nginx.conf not found!")
        sys.exit(1)
    run_command(f"sudo cp {nginx_conf} {NGINX_CONF_DIR}/nginx.conf")
    log("Custom Nginx configuration copied successfully.")


def setup_directories():
    """Ensure required directories exist."""
    os.makedirs(WWW_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    log(f"Directories {WWW_DIR} and {LOG_DIR} created or verified.")


def setup_virtualenv():
    """Create and activate a Python virtual environment."""
    venv_dir = os.path.join(REPO_DIR, "venv")
    venv.EnvBuilder(clear=True).create(venv_dir)
    log("Virtual environment created successfully.")
    run_command(f"source {venv_dir}/bin/activate && pip install requests pytz")


def setup_cron_jobs():
    """Set up required cron jobs."""
    log("Setting up cron jobs...")
    cron_jobs = [
        f"0 1,13 * * * source {REPO_DIR}/venv/bin/activate && python3 {REPO_DIR}/scripts/merge_epg.py >> {LOG_DIR}/merge_cron.log 2>&1",
        f"0 */6 * * * nginx -s reload >> {LOG_DIR}/nginx_reload.log 2>&1",
        f"* * * * * echo 'Cron is working at $(date)' >> {LOG_DIR}/cron_test.log"
    ]
    current_cron = run_command("crontab -l", check=False).strip()
    with open("/tmp/crontab.tmp", "w") as f:
        f.write(current_cron + "\n" + "\n".join(cron_jobs) + "\n")
    run_command("crontab /tmp/crontab.tmp")
    log("Cron jobs set up successfully.")


def main():
    log("Starting Nginx installation script.")
    install_homebrew()
    install_nginx()
    setup_nginx_config()
    setup_directories()
    setup_virtualenv()
    setup_cron_jobs()
    log("Nginx installation completed successfully.")


if __name__ == "__main__":
    main()
