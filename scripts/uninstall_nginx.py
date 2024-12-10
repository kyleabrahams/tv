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
    if not result:
        log("No running Nginx processes found or permission denied.")

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
        result = run_command("brew list nginx", retries=1).strip()
        return result != ""
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

def uninstall_nginx():
    """Master function to uninstall Nginx."""
    log("Starting Nginx uninstallation process...")
    deactivate_venv()
    stop_nginx_processes()
    uninstall_nginx_homebrew()
    uninstall_nginx_from_source()
    uninstall_nginx_package_manager()
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
