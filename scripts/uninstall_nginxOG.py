import os
import subprocess
import sys
import logging
import re # Removes crontab

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

def run_command(command, retries=3):
    """Run a shell command with retry logic and log its output."""
    for attempt in range(retries):
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
            if result.stdout:
                log(result.stdout.strip())
            return result.stdout
        except subprocess.CalledProcessError as e:
            log(f"Attempt {attempt + 1} failed: Command: {command}\nError: {e.stderr.strip()}")
            if attempt == retries - 1:
                log(f"Command failed after {retries} attempts: {command}")
                return None
        except Exception as e:
            log(f"Exception running command: {command}\n{str(e)}")
            sys.exit(1)

def deactivate_venv():
    """Deactivate the virtual environment if active."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        log("Deactivating virtual environment...")
        deactivate_script = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'deactivate')
        if os.path.exists(deactivate_script):
            exec(open(deactivate_script).read(), {'__file__': deactivate_script})
            log("Virtual environment deactivated.")

def stop_nginx_processes():
    """Stop any running Nginx processes."""
    log("Stopping any running Nginx processes...")
    result = run_command("sudo pkill nginx", retries=1)
    if result is None:
        log("No running Nginx processes found or permission denied.")
    else:
        log(f"Nginx processes stopped: {result}")

def uninstall_nginx_from_source():
    """Remove Nginx if installed from source."""
    log("Checking if Nginx was installed from source...")
    nginx_directories = [
        "/usr/local/nginx",
        "/usr/local/sbin/nginx",
        "/usr/local/bin/nginx",
        "/etc/nginx",
        "/var/log/nginx",
        "/var/run/nginx"
    ]

    found_nginx = False

    for path in nginx_directories:
        if os.path.exists(path):
            found_nginx = True
            log(f"Removing Nginx-related files from {path}...")
            run_command(f"sudo rm -rf {path}", retries=1)

    if found_nginx:
        log("Nginx source files removed successfully.")
    else:
        log("No Nginx source files detected.")

def detect_package_manager():
    """Detect the available package manager."""
    for cmd in ["apt-get", "yum", "dnf", "zypper", "pacman"]:
        if run_command(f"command -v {cmd}", retries=1):
            return cmd
    return None

def uninstall_nginx_package_manager():
    """Remove Nginx if installed via a package manager."""
    log("Checking for Nginx installations via package managers...")
    pkg_manager = detect_package_manager()

    if pkg_manager == "apt-get":
        log("Removing Nginx installed via apt...")
        run_command("sudo apt-get remove --purge -y nginx nginx-common")
        run_command("sudo apt-get autoremove -y")
        run_command("sudo apt-get clean")

    elif pkg_manager == "yum":
        log("Removing Nginx installed via yum...")
        run_command("sudo yum remove -y nginx")

    elif pkg_manager == "dnf":
        log("Removing Nginx installed via dnf...")
        run_command("sudo dnf remove -y nginx")

    elif pkg_manager == "zypper":
        log("Removing Nginx installed via zypper...")
        run_command("sudo zypper remove -y nginx")

    elif pkg_manager == "pacman":
        log("Removing Nginx installed via pacman...")
        run_command("sudo pacman -Rsn --noconfirm nginx")

    else:
        log("No supported package manager found. Skipping package-based Nginx removal.")

def check_nginx_installed():
    """Check if Nginx is installed via Homebrew."""
    try:
        result = run_command("brew list nginx", retries=1)
        if result and result.strip():  # Only proceed if result is not empty
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def uninstall_nginx_homebrew():
    """Uninstall Nginx if installed via Homebrew."""
    if check_nginx_installed():
        log("Uninstalling Nginx via Homebrew...")
        run_command("brew uninstall nginx")
        log("Nginx uninstalled via Homebrew.")
    else:
        log("Nginx is not installed via Homebrew.")

def validate_removal():
    """Ensure Nginx is fully removed."""
    binaries = ["/usr/local/bin/nginx", "/usr/sbin/nginx", "/usr/bin/nginx"]
    for binary in binaries:
        if os.path.exists(binary):
            log(f"Error: Nginx binary still exists: {binary}")
        else:
            log(f"Nginx binary removed: {binary}")

def remove_user_plists():
    """Remove user-level Nginx plist files."""
    user_plist = os.path.expanduser("~/Library/LaunchAgents/homebrew.mxcl.nginx.plist")
    if os.path.exists(user_plist):
        log(f"Removing user-level plist file: {user_plist}")
        run_command(f"rm {user_plist}")
        log(f"User-level plist file removed: {user_plist}")
    else:
        log("No user-level plist file found for Nginx.")

def remove_nginx_cron_jobs():
    """Remove Nginx-related cron jobs."""
    log("Removing Nginx-related cron jobs...")
    
    cron_jobs = run_command("crontab -l", retries=1)
    if cron_jobs:
        # Find and remove Nginx-related cron jobs using regex (adjust the pattern if needed)
        nginx_cron_pattern = re.compile(r".*nginx.*", re.IGNORECASE)
        new_cron_jobs = "\n".join(line for line in cron_jobs.splitlines() if not nginx_cron_pattern.match(line))
        
        if new_cron_jobs != cron_jobs:
            # If cron jobs were removed, update crontab
            with open("temp_cron_jobs.txt", "w") as temp_file:
                temp_file.write(new_cron_jobs)
            run_command("crontab temp_cron_jobs.txt", retries=1)
            os.remove("temp_cron_jobs.txt")
            log("Nginx-related cron jobs removed successfully.")
        else:
            log("No Nginx-related cron jobs found.")
    else:
        log("No cron jobs found.")

def remove_nginx_plist_files():
    """Remove Nginx plist files from LaunchAgents and LaunchDaemons."""
    plist_paths = [
        os.path.expanduser("~/Library/LaunchAgents/homebrew.mxcl.nginx.plist"),
        "/Library/LaunchAgents/homebrew.mxcl.nginx.plist",
        "/Library/LaunchDaemons/com.nginx.server.plist"
    ]
    
    for plist_path in plist_paths:
        if os.path.exists(plist_path):
            log(f"Removing plist file: {plist_path}")
            unload_command = f"sudo launchctl unload {plist_path}" if "/Library/" in plist_path else f"launchctl unload {plist_path}"
            run_command(unload_command, retries=1)
            remove_command = f"sudo rm -f {plist_path}" if "/Library/" in plist_path else f"rm {plist_path}"
            run_command(remove_command, retries=1)
            log(f"Plist file removed: {plist_path}")
        else:
            log(f"No plist file found at {plist_path}.")

def uninstall_nginx():
    """Master function to uninstall Nginx."""
    log("Starting Nginx uninstallation process...")
    deactivate_venv()
    stop_nginx_processes()
    uninstall_nginx_homebrew()
    remove_nginx_plist_files()  # Corrected function name
    uninstall_nginx_from_source()
    uninstall_nginx_package_manager()
    remove_nginx_cron_jobs()
    validate_removal()

def main():
    log("Initiating Nginx removal script...")
    try:
        uninstall_nginx()
        log("Nginx uninstallation completed successfully.")
    except Exception as e:
        log(f"Uninstallation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()