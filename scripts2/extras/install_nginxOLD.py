import os
import subprocess
import sys
from datetime import datetime
import logging
import venv

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script for installing Nginx
# python3 install_nginx.py


# --- Step 1: Logging Setup ---
# Configure logging to output both to the console and to a file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Ensure the log directory exists
LOG_DIR = "/Users/kyleabrahams/Documents/GitHub/tv/log"
os.makedirs(LOG_DIR, exist_ok=True)

# Define log file path
log_file = os.path.join(LOG_DIR, "script.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# --- Step 2: Directory Paths ---
# Define the repository and log directories
REPO_DIR = "/Users/kyleabrahams/Documents/GitHub/tv"
NGINX_CONF_DIR = "/opt/homebrew/etc/nginx"
WWW_DIR = "/usr/local/var/www"

# Verify or create the WWW directory
os.makedirs(WWW_DIR, exist_ok=True)
logger.info(f"Directories {LOG_DIR} and {WWW_DIR} created or verified.")
print(f"Directories {LOG_DIR} and {WWW_DIR} created or verified.")  # Echo the step

# --- Step 3: Set up cron jobs without duplication ---
def setup_cron_jobs():
    """Set up required cron jobs without duplication."""
    logger.info("Step 3: Removing old cron jobs and setting up new ones...")
    print("Step 3: Removing old cron jobs and setting up new ones...")  # Echo the step

    # 3.1 Backup current cron jobs
    try:
        current_crontab = run_command("crontab -l", check=False) or ""
        backup_file_path = os.path.join(REPO_DIR, f"crontab_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(backup_file_path, "w") as backup:
            backup.write(current_crontab)
        logger.info(f"Cron jobs backup saved at {backup_file_path}")
        print(f"Cron jobs backup saved at {backup_file_path}")  # Echo the backup path
    except Exception as e:
        logger.error(f"Error during cron jobs backup: {e}")
        print(f"Error during cron jobs backup: {e}")  # Echo the error
        sys.exit(1)

    # 3.2 Define new cron jobs with a unique comment to avoid duplication
    cron_jobs = [
        f"0 1,13 * * * source {REPO_DIR}/scripts/venv/bin/activate && python3 {REPO_DIR}/scripts/merge_epg.py >> {LOG_DIR}/merge_cron.log 2>&1 # cron-job-merge-epg",
        f"0 */6 * * * nginx -s reload >> {LOG_DIR}/nginx_reload.log 2>&1 # cron-job-nginx-reload",
        f"0 0 * * * mkdir -p {os.path.join(os.path.dirname(REPO_DIR), 'log')} && exit # cron-job-create-folder"
    ]
    print("Cron jobs defined.")  # Echo the cron job definition

    # 3.3 Filter out existing cron jobs with the unique comment
    current_crontab = run_command("crontab -l", check=False).strip()
    new_crontab = current_crontab

    for job in cron_jobs:
        if f"# {job.split('#')[-1]}" not in current_crontab:
            new_crontab += f"\n{job}"
            logger.info(f"Adding new cron job: {job}")
            print(f"Adding new cron job: {job}")  # Echo the job
        else:
            logger.info(f"Cron job already exists, skipping: {job}")
            print(f"Cron job already exists, skipping: {job}")  # Echo the skip

    # 3.4 Write new cron jobs back to crontab
    if new_crontab != current_crontab:
        run_command(f"echo '{new_crontab}' | crontab -")
        logger.info("Cron jobs set up successfully.")
        print("Cron jobs set up successfully.")  # Echo the success
    else:
        logger.info("No new cron jobs to add. All jobs are already in place.")
        print("No new cron jobs to add. All jobs are already in place.")  # Echo no changes

    # 3.5 Force reload of cron service to apply changes (for macOS)
    try:
        run_command("sudo launchctl unload /System/Library/LaunchDaemons/com.vix.cron.plist", check=False)
        run_command("sudo launchctl load /System/Library/LaunchDaemons/com.vix.cron.plist", check=False)
        logger.info("Cron service reloaded successfully.")
        print("Cron service reloaded successfully.")  # Echo the success
    except Exception as e:
        logger.error(f"Error reloading cron service: {e}")
        print(f"Error reloading cron service: {e}")  # Echo the error

# --- Step 4: Utility Function to Run Shell Commands ---
def run_command(command, check=True):
    """
    Executes a shell command and checks for errors.

    :param command: Command to run
    :param check: If True, will raise an error if the command fails
    :return: Output of the command
    """
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if check and result.returncode != 0:
            logger.error(f"Command failed: {command}\n{result.stderr}")
            print(f"Command failed: {command}\n{result.stderr}")  # Echo the failure
            sys.exit(1)
        return result.stdout
    except Exception as e:
        logger.error(f"Exception running command: {command}\n{e}")
        print(f"Exception running command: {command}\n{e}")  # Echo the exception
        sys.exit(1)

# --- Step 5: Install Homebrew ---
def install_homebrew():
    """
    Ensures Homebrew is installed on the system.
    """
    if run_command("command -v brew", check=False).strip() == "":
        logger.info("Homebrew is not installed. Installing now...")
        run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    else:
        logger.info("Homebrew is already installed.")

# --- Step 6: Install Nginx ---
def install_nginx():
    """
    Installs or updates Nginx using Homebrew.
    """
    logger.info("Installing or updating Nginx...")
    run_command("brew install nginx")

# --- Step 7: Set Up Custom Nginx Configuration ---
def setup_nginx_config():
    """
    Copies the custom Nginx configuration file to the appropriate directory.
    """
    nginx_conf = os.path.join(REPO_DIR, "nginx.conf")
    if not os.path.exists(nginx_conf):
        logger.error("Custom nginx.conf not found!")
        sys.exit(1)
    run_command(f"sudo cp {nginx_conf} {NGINX_CONF_DIR}/nginx.conf")
    logger.info("Custom Nginx configuration copied successfully.")

# --- Step 8: Set Up Virtual Environment ---
def setup_virtualenv():
    """
    Creates a Python virtual environment and installs necessary dependencies.
    """
    # Define the virtual environment directory (update to /Users/kyleabrahams/Documents/GitHub/tv/scripts/venv/bin)
    venv_dir = "/Users/kyleabrahams/Documents/GitHub/tv/scripts/venv"  # Updated to your specified location
    
    # Create the virtual environment if it doesn't exist already
    venv.EnvBuilder(clear=True).create(venv_dir)  
    logger.info("Virtual environment created successfully.")
    
    # Ensure the virtual environment is activated before installing dependencies
    pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Check if pip exists in the virtual environment
    if os.path.exists(pip_path):
        # Upgrade pip and install required packages
        run_command(f"{pip_path} install --upgrade pip")
        run_command(f"{pip_path} install requests pytz")
    else:
        logger.error(f"pip not found in the virtual environment at {pip_path}.")
        sys.exit(1)

# --- Step 9: Set Up Cron Jobs ---
def setup_cron_jobs():
    """
    Sets up cron jobs for scheduled tasks.
    """
    logger.info("Removing old cron jobs and setting up new ones...")

    # Step 9.1: Backup current cron jobs
    try:
        current_crontab = run_command("crontab -l", check=False) or ""
        backup_file_path = os.path.join(REPO_DIR, f"crontab_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(backup_file_path, "w") as backup:
            backup.write(current_crontab)
        logger.info(f"Cron jobs backup saved at {backup_file_path}")
    except Exception as e:
        logger.error(f"Error during cron jobs backup: {e}")
        sys.exit(1)

    # Step 9.2: Remove all existing cron jobs
    run_command("crontab -r", check=False)
    logger.info("All existing cron jobs removed.")

    # Step 9.3: Add new cron jobs
    current_crontab = run_command("crontab -l", check=False)
    existing_jobs = set(current_crontab.splitlines())

    # Step 9.4: Only add new jobs that don't already exist
    new_jobs = []
    for job in cron_jobs:
        if job not in existing_jobs:
            new_jobs.append(job)
            logger.info(f"Adding new cron job: {job}")
        else:
            logger.info(f"Cron job already exists, skipping: {job}")

    # Step 9.5: Write new cron jobs to crontab
    if new_jobs:
        new_crontab = "\n".join(new_jobs)
        run_command(f"echo '{new_crontab}' | crontab -")
        logger.info("Cron jobs set up successfully.")
    else:
        logger.info("No new cron jobs to add.")

# --- Step 10: Prompt to Run `merge_epg.py` ---
def prompt_run_merge_epg():
    """
    Prompts the user to run the merge_epg.py script.
    """
    user_input = input("Do you want to run merge_epg.py now? (y/n): ").strip().lower()
    if user_input == 'y':
        run_command(f"{os.path.join(REPO_DIR, 'scripts', 'merge_epg.py')}")
        logger.info("merge_epg.py script executed successfully.")
    else:
        logger.info("Skipping execution of merge_epg.py.")

# --- Step 11: Main Function ---
def main():
    """
    Main function that runs the entire setup process.
    """
    logger.info("Starting Nginx installation script.")

    # Step 11.1: Install or update Homebrew
    install_homebrew()

    # Step 11.2: Install or update Nginx
    install_nginx()

    # Step 11.3: Set up custom Nginx configuration
    setup_nginx_config()

    # Step 11.4: Set up virtual environment
    setup_virtualenv()

    # Step 11.5: Set up cron jobs
    setup_cron_jobs()

    # Step 11.6: Prompt to run merge_epg.py
    prompt_run_merge_epg()

    logger.info("Script completed.")

if __name__ == "__main__":
    main()