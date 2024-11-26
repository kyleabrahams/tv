import os
import subprocess
from datetime import datetime

# Log file path
LOG_FILE = os.path.join(os.getcwd(), "uninstall_nginx.log")

# Define common paths
NGINX_CONF_DIR = "/opt/homebrew/etc/nginx"
NGINX_PID_DIR = "/usr/local/var/run"
WWW_DIR = "/usr/local/var/www"
PLIST_PATH = "/Library/LaunchDaemons/homebrew.mxcl.nginx.plist"

# Function to log messages
def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)

# Function to execute shell commands
def run_command(command, capture_output=False):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=capture_output)
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        log(f"Error executing command: {command} | Error: {e}")
        return None

# Ensure log file exists
try:
    open(LOG_FILE, "a").close()
except Exception as e:
    print(f"Failed to create log file: {e}")
    exit(1)

# Start uninstallation
log("Starting Nginx uninstallation script.")

# Step 1: Stop Nginx if running
log("Step 1: Checking if Nginx is running.")
if run_command("pgrep nginx"):
    log("Nginx is running. Attempting to stop it...")
    run_command("sudo nginx -s stop")
    log("Nginx stopped successfully.")
else:
    log("Nginx is not running.")

# Step 2: Uninstall Nginx via Homebrew
log("Step 2: Uninstalling Nginx using Homebrew...")
run_command("brew uninstall nginx")

# Step 3: Remove Nginx configuration files
log("Step 3: Removing Nginx configuration files...")
if os.path.exists(f"{NGINX_CONF_DIR}/nginx.conf"):
    run_command(f"sudo rm {NGINX_CONF_DIR}/nginx.conf")
    log("Nginx configuration file removed.")

# Step 4: Remove /usr/local/var/www directory
remove_www = input("Step 4: Do you want to remove the /usr/local/var/www directory? (y/n): ").strip().lower()
if remove_www == "y":
    if os.path.exists(WWW_DIR):
        run_command(f"sudo rm -rf {WWW_DIR}")
        log("/usr/local/var/www directory removed.")
else:
    log("User chose not to remove /usr/local/var/www directory.")

# Step 5: Remove /usr/local/var/run directory
if os.path.exists(NGINX_PID_DIR):
    run_command(f"sudo rm -rf {NGINX_PID_DIR}")
    log("/usr/local/var/run directory removed.")

# Step 6: Remove LaunchDaemon plist file for Nginx
log("Step 6: Removing Nginx LaunchDaemon plist...")
if os.path.exists(PLIST_PATH):
    run_command(f"sudo rm {PLIST_PATH}")
    log("Nginx LaunchDaemon plist removed.")

# Step 7: Stop Nginx service from starting on boot
log("Step 7: Ensuring Nginx service is stopped on boot...")
run_command("brew services stop nginx")

# Step 8: Remove Nginx-related cron jobs
log("Step 8: Removing Nginx-related cron jobs...")
current_crontab = run_command("crontab -l", capture_output=True) or ""
with open(f"{os.getcwd()}/crontab_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as backup:
    backup.write(current_crontab)

# Remove lines related to nginx or any relative path variations of merge_epg.py
updated_crontab = "\n".join([line for line in current_crontab.splitlines() 
                             if "nginx" not in line and 
                             "scripts/merge_epg.py" not in line and
                             "scripts/scripts/merge_epg.py" not in line])

run_command(f"echo '{updated_crontab}' | crontab -")
log("Nginx-related and merge_epg.py cron jobs removed.")

# Step 9: Remove test cron jobs
log("Step 9: Removing test cron jobs...")
updated_crontab = "\n".join([line for line in updated_crontab.splitlines() if "test" not in line])
run_command(f"echo '{updated_crontab}' | crontab -")
log("Test cron jobs removed.")

log("Nginx uninstallation completed.")
