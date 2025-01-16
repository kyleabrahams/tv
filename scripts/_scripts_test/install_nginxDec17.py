import os
import subprocess
import sys
from datetime import datetime
import venv
import logging
import time  # Ensure the time module is imported
import hashlib # Used to remove dupe crontab entries
import platform # Detects platform
import time


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

# --- Step 1: Constants ---
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # Directory of this script
LOG_DIR = os.path.join(REPO_DIR, "log")
NGINX_CONF = os.path.join(REPO_DIR, "nginx.conf")
WWW_DIR = os.path.join(REPO_DIR, "www")
EPG_FILE = os.path.join(WWW_DIR, "epg.xml")
VENVS_DIR = os.path.join(REPO_DIR, "venv")
LAST_RUN_FILE = f"{LOG_DIR}/merge_epg_last_run.txt" # Dec 11 2024
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB in bytes


# --- Step 2: Logging Setup ---
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Set up logging configuration to overwrite the log file each time
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Only format the message, date will be handled separately
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "setup.log"), mode='w'),  # 'w' to overwrite the log
    ]
)

# Initialize the logger
logger = logging.getLogger()

def log(message):
    """Log to console and file."""
    # Get the current date in the desired format
    current_date = datetime.now().strftime("%b %d %Y")
    
    # Format the log message with the custom date format
    log_message = f"{current_date} - {message}"

    # Log the message
    logger.info(log_message)

    # Print the message to the console
    print(log_message)

# --- Step 3: Run Command Function ---
def ask_for_user_permission():
    """Ask the user for permission to proceed with an action."""
    user_input = input("Do you want to proceed with this action? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    else:
        print("Action canceled by the user.")
        return False

def run_command(command, check=True, fail_silently=False, real_time=False):
    """Run a shell command and handle output."""
    try:
        log(f"Running command: {command}")  # Log the command being run

        if real_time:
            process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in process.stdout:
                log(line.strip())  # Log stdout line by line
            for err_line in process.stderr:
                log(f"ERROR: {err_line.strip()}")  # Log stderr in real-time
            process.stdout.close()
            process.stderr.close()
            return_code = process.wait()  # Wait for the command to finish
            if check and return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)
            return None
        else:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
            if result.stdout:
                log(result.stdout.strip())
            if result.stderr:
                log(f"ERROR: {result.stderr.strip()}")
            # Ensure that if there's no result, an empty string is returned
            return result.stdout.strip() if result.stdout else ''  
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed: {command}\nExit Code: {e.returncode}\nError Output: {e.stderr.strip() if e.stderr else 'None'}"
        log(error_message)
        if not fail_silently:
            raise e  # Re-raise exception for error handling
    except Exception as e:
        log(f"Exception running command: {command}\n{e}")
        if not fail_silently:
            raise e  # Re-raise exception for error handling
                        
# --- Step 4: Homebrew Setup ---
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
    system = platform.system()

    if system == "Darwin":  # macOS
        log("Detected macOS, checking for Homebrew installation...")
        if run_command("command -v brew", check=False).strip() == "":
            log("Homebrew not found. Installing Homebrew...")
            
            # Ask for user confirmation before installing Homebrew
            if not ask_for_user_permission():  # This will prompt the user
                return  # Exit if user cancels
            run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        else:
            log("Step 4. Homebrew is already installed.")
        
        # Fix ownership issues for Homebrew directories (without sudo)
        fix_homebrew_permissions()
        log("Homebrew installation or permissions check completed.")
    
    elif system == "Linux":  # Linux
        log("Detected Linux, checking for Homebrew installation...")
        if run_command("command -v brew", check=False).strip() == "":
            log("Homebrew not found. Installing Homebrew...")
            # Ask for user confirmation before installing Homebrew
            if not ask_for_user_permission():  # This will prompt the user
                return  # Exit if user cancels
            run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/linuxbrew-core/master/install.sh)"')
        else:
            log("Homebrew is already installed.")
        
        # Fix ownership issues for Homebrew directories (without sudo)
        fix_homebrew_permissions()
        log("Homebrew installation or permissions check completed.")

# --- Step 5: Install Nginx ---
def force_stop_nginx():
    """Force stop any running Nginx processes and unload services."""
    log("Attempting to stop any running Nginx processes...")

    # Kill any Nginx processes running on port 8080
    nginx_pid = run_command("sudo lsof -i :8080 | grep nginx | awk '{print $2}'", check=False)
    if nginx_pid:
        nginx_pid = nginx_pid.strip()
        if nginx_pid:
            run_command(f"sudo kill -9 {nginx_pid}")
            log(f"Stopped Nginx process on port 8080 with PID {nginx_pid}")
        else:
            log("No Nginx process found on port 8080.")
    else:
        log("No Nginx processes found on port 8080.")

    # Kill any other running Nginx processes
    try:
        run_command("sudo killall -15 nginx", check=False)
        log("Stopped all Nginx processes.")
    except Exception as e:
        log(f"Failed to stop Nginx processes: {e}")
    
    # Unload launchd plist if it exists and the service is running
nginx_plist_path = os.path.expanduser("~/Library/LaunchAgents/homebrew.mxcl.nginx.plist")
if os.path.exists(nginx_plist_path):
    try:
        # Check if the service is already unloaded
        result = run_command(f"sudo launchctl list | grep {nginx_plist_path}", check=False, fail_silently=True)
        log(f"launchctl result: {result}")  # Add this line to log the result

        if result.strip():
            run_command(f"sudo launchctl bootout system {nginx_plist_path}")
            log("Unloaded Nginx launchd service.")
        else:
            log("Nginx launchd service is not running.")
    except Exception as e:
        log(f"Failed to unload Nginx launchd service: {e}")
    
    

def remove_existing_nginx_service():
    """Remove any pre-existing Nginx service and reset it."""
    log("Removing any pre-existing Nginx service...")

    # Use relative paths for the LaunchAgent and Nginx service files
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    nginx_plist_path = os.path.join(launch_agents_dir, "homebrew.mxcl.nginx.plist")

    # Remove the old launch agent and stop Nginx service
    try:
        result = run_command(f"sudo launchctl bootout gui/501 {nginx_plist_path}", check=False, fail_silently=True)
        if result:
            log(f"Removed the launch agent {nginx_plist_path}")
        else:
            log(f"Failed to remove the launch agent {nginx_plist_path}")
    except Exception as e:
        log(f"Error removing the launch agent {nginx_plist_path}: {e}")

    try:
        result = run_command(f"sudo rm {nginx_plist_path}", check=False, fail_silently=True)
        if result:
            log(f"Removed the Nginx plist file {nginx_plist_path}")
        else:
            log(f"Failed to remove the Nginx plist file {nginx_plist_path}")
    except Exception as e:
        log(f"Error removing the Nginx plist file {nginx_plist_path}: {e}")

    # Stop and clean up the Nginx service
    try:
        result = run_command("brew services stop nginx", check=False, fail_silently=True)
        if result:
            log("Successfully stopped Nginx service.")
        else:
            log("Failed to stop Nginx service.")
    except Exception as e:
        log(f"Error stopping Nginx service: {e}")

    try:
        result = run_command("brew services cleanup", check=False, fail_silently=True)
        if result:
            log("Cleaned up any Nginx services.")
        else:
            log("Failed to clean up Nginx services.")
    except Exception as e:
        log(f"Error cleaning up Nginx services: {e}")

    return "Nginx service removal and cleanup completed."

def check_and_install_nginx():
    """Check if Nginx is installed, and install it if necessary."""
    log("Checking if Nginx is already installed...")

    # Check if Nginx is installed using Homebrew
    result = run_command("brew list nginx", check=False, fail_silently=True)
    if result:
        log("Nginx is already installed.")
    else:
        log("Installing Nginx...")
        run_command("brew install nginx")


def install_nginx():
    """Install or update Nginx."""
    log("Installing or updating Nginx...")

    # Automatically install or update Nginx without user confirmation
    success, output = run_command("brew install nginx")  # Install Nginx
    if success:
        log("Nginx installation successful.")
    else:
        log(f"Error installing Nginx: {output}")
        return

    # Start Nginx setup
    log("Starting Nginx setup...")
    success, output = run_command("brew services start nginx")
    if success:
        log("Successfully started Nginx service.")
    else:
        log(f"Error starting Nginx service: {output}")

# --- Step 6: Modify Files ---
def modify_files():
    """Modify the necessary files after installation."""
    log("Modifying system files...")

    nginx_config_path = '/opt/homebrew/etc/nginx/nginx.conf'

    if not os.path.exists(nginx_config_path):
        log(f"Error: Nginx configuration file not found at {nginx_config_path}")
        return

    # Modify the Nginx config file path (e.g., setting permissions)
    success, _ = run_command(f"chmod 644 {nginx_config_path}")
    if success:
        log("Nginx configuration file permissions modified successfully.")
    else:
        log("Failed to modify Nginx configuration file permissions.")

    log("Files modified successfully.")

# --- Step 7: Set Up Nginx Configuration ---
def setup_nginx():
    log("Starting Nginx setup...")

# Step 7.1: Check if Homebrew is installed
    brew_command = "/opt/homebrew/bin/brew"
    if os.path.exists(brew_command):
        log("Homebrew is already installed.")
    else:
        log("Homebrew not found. Installing...")
        success, _ = run_command("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        if not success:
            log("Homebrew installation failed.")
            return
            
# Step 7.2: Install or update Nginx
log("Starting setup process...")

brew_command = "/opt/homebrew/bin/brew"
if os.path.exists(brew_command):
    log("Homebrew is already installed.")
else:
    log("Homebrew not found. Installing...")
    run_command("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")

log("Installing or updating Nginx...")
run_command(f"{brew_command} install nginx")

# Step 7.3: Set up nginx configuration
nginx_conf_path = "/opt/homebrew/etc/nginx/nginx.conf"
if os.path.exists(nginx_conf_path):
    log(f"Nginx configuration found at {nginx_conf_path}")
else:
    log(f"Warning: Nginx configuration not found at {nginx_conf_path}")

# Step 7.4: Setup launchd to start Nginx at login
plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.nginx.server</string>

        <key>ProgramArguments</key>
        <array>
            <string>/opt/homebrew/bin/nginx</string>
            <string>-g</string>
            <string>daemon off;</string>
        </array>

        <key>RunAtLoad</key>
        <true/>

        <key>KeepAlive</key>
        <true/>

        <key>StandardOutPath</key>
        <string>/tmp/nginx.out</string>

        <key>StandardErrorPath</key>
        <string>/tmp/nginx.err</string>
    </dict>
</plist>
'''

# Step 7.5: Write the launchd plist file to the LaunchAgents directory
launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
plist_filename = "com.nginx.server.plist"
plist_path = os.path.join(launch_agents_dir, plist_filename)    

# --- Step 8: Set Up Virtual Environment ---
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


# --- Step 9: Set Up Directories and EPG File ---
def setup_directories_and_epg():
    """Set up directories and default EPG file."""
    os.makedirs(WWW_DIR, exist_ok=True)
    if not os.path.exists(EPG_FILE):
        with open(EPG_FILE, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<epg></epg>')
        log(f"Created empty EPG file at {EPG_FILE}.")
    run_command(f"chmod 644 {EPG_FILE}")  # Apply correct permissions
    log(f"Permissions set for {EPG_FILE}.")


# --- Step 10: Generate Job Hash for Cron Jobs ---
def generate_job_hash(job):
    """Generate a unique hash for each cron job, normalizing spacing and formatting."""
    # Normalize spacing and remove unnecessary characters to avoid false mismatches
    job = ' '.join(job.split())  # Remove any extra spaces
    return hashlib.sha256(job.encode('utf-8')).hexdigest()


# --- Step 11: Set Up Cron Jobs ---
def clear_crontab():
    """Clear the existing crontab."""
    log("Clearing existing crontab...")
    run_command("crontab -r", check=True)

def setup_cron_jobs():
    """Set up cron jobs with strict duplicate prevention."""
    log("Setting up cron jobs...")

    # Get the script's directory to use as the base for relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the cron jobs to be added (relative paths)
    cron_jobs = [
        f"0 1,13 * * * source {script_dir}/venv/bin/activate && python3 {script_dir}/merge_epg.py",
        f"0 */6 * * * /opt/homebrew/bin/nginx -s reload"
]

    # Clear the existing crontab to avoid duplicate jobs
    clear_crontab()

    # Get the current user's crontab using crontab -l
    current_cron = run_command("crontab -l", check=False).strip()

    # Normalize and store existing jobs to avoid duplicates
    existing_jobs = {job.strip() for job in current_cron.splitlines() if job.strip()}

    # Add new cron jobs if they are not already present
    updated_cron = current_cron
    for job in cron_jobs:
        if job.strip() not in existing_jobs:
            updated_cron += f"\n{job}"
            existing_jobs.add(job.strip())  # Add the actual job text to avoid future duplicates
        else:
            log(f"Duplicate job detected: {job.strip()}, skipping...")

    # Save the updated crontab to /tmp/crontab.tmp
    with open("/tmp/crontab.tmp", "w") as f:
        f.write(updated_cron + "\n")
    
    # Apply the updated crontab and force a rewrite
    run_command("crontab /tmp/crontab.tmp")
    
    log("Cron jobs set up successfully.")

# --- Step 12: Check if Merge EPG Should Be Run ---
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


# --- Step 13: Prompt to Run Merge EPG ---
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


# --- Step 14: Reload Nginx ---
def reload_nginx():
    """Reload Nginx."""
    log("Reloading Nginx...")
    run_command("brew services restart nginx")
    log("Nginx reloaded successfully.")


# --- Step 15: Main Script ---
def main():
    log("Starting setup process...")
    try:
        install_homebrew()
        force_stop_nginx()  # Ensure Nginx is force stopped before proceeding
        check_and_install_nginx()
        install_nginx()
        modify_files()  # Step 3
        setup_nginx()
        setup_virtualenv()
        setup_directories_and_epg()
        setup_cron_jobs()  # If needed
        reload_nginx()  # Reload Nginx after setup
        log("Setup complete. Access EPG XML at http://localhost:8080/epg.xml")
    except Exception as e:
        log(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()