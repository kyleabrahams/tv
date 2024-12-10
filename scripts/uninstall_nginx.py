import os
import subprocess
import sys
import logging

# --- Constants ---
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # Directory of this script
LOG_DIR = os.path.join(REPO_DIR, "log")
LOG_FILE = os.path.join(LOG_DIR, "uninstall_nginx.log")

# --- Logging Setup ---
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)  # Ensure log directory exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def log(message):
    """Log to console and file."""
    logger.info(message)

def run_command(command, check=True, real_time=False):
    """Run a shell command and log its output."""
    try:
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

def check_nginx_installed():
    """Check if Nginx is installed."""
    result = run_command("brew list nginx", check=False, real_time=False).strip()
    return result != ""

def uninstall_nginx():
    """Uninstall Nginx."""
    if check_nginx_installed():
        log("Uninstalling Nginx...")
        try:
            run_command("brew uninstall nginx")
            log("Nginx uninstalled.")
        except Exception as e:
            log(f"Failed to uninstall Nginx: {e}")
            sys.exit(1)
    else:
        log("Nginx is not installed via Homebrew.")

def remove_homebrew_cron_jobs():
    """Remove Homebrew-related cron jobs."""
    log("Checking for Homebrew-related cron jobs...")

    try:
        # List all cron jobs for the user
        cron_jobs = run_command("crontab -l", check=False).strip()
        
        if cron_jobs:
            # Identify Homebrew-related cron jobs (if any), e.g., nginx reload
            homebrew_jobs = [line for line in cron_jobs.splitlines() if "nginx" in line]
            
            if homebrew_jobs:
                log("Homebrew-related cron jobs found. Removing...")
                # Remove those cron jobs
                new_cron = "\n".join([line for line in cron_jobs.splitlines() if "nginx" not in line])
                # Set the new crontab without the Homebrew jobs
                subprocess.run(f"echo '{new_cron}' | crontab", shell=True, check=True)
                log("Homebrew-related cron jobs removed.")
            else:
                log("No Homebrew-related cron jobs found.")
        else:
            log("No cron jobs found.")
    except Exception as e:
        log(f"Failed to remove Homebrew-related cron jobs: {e}")
        sys.exit(1)

def clear_cron_jobs():
    """Clears all cron jobs for the current user."""
    log("Clearing all cron jobs...")
    try:
        # Check if any cron jobs exist first
        cron_jobs = run_command("crontab -l", check=False)
        
        if cron_jobs:
            subprocess.check_call(["crontab", "-r"])
            log("All cron jobs cleared successfully.")
        else:
            log("No cron jobs to clear.")
    except subprocess.CalledProcessError as e:
        # Handle case where no crontab exists
        if "no crontab for" in str(e):
            log("No cron jobs to clear.")
        else:
            log(f"Failed to clear cron jobs: {e}")
            sys.exit(1)
    except Exception as e:
        log(f"Exception clearing cron jobs: {e}")
        sys.exit(1)

def main():
    """Main uninstallation process."""
    try:
        uninstall_nginx()
        remove_homebrew_cron_jobs()  # Remove Homebrew-related cron jobs
        clear_cron_jobs()  # Optionally clear all cron jobs
        log("Uninstallation of Nginx and removal of cron jobs completed successfully.")
    except Exception as e:
        log(f"Error during uninstallation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()