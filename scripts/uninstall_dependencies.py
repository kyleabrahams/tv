import subprocess  # For running commands
import sys  # For accessing Python's runtime environment
import os  # For file and directory handling
import platform  # For detecting system architecture

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script
# python3 uninstall_dependencies.py

# Step 1: Function to uninstall packages listed in requirements.txt
def uninstall_requirements():
    """
    Uninstall all dependencies listed in requirements.txt.
    """
    if os.path.exists("requirements.txt"):
        confirmation = input("Are you sure you want to uninstall all dependencies listed in requirements.txt? (y/n): ")
        if confirmation.lower() != 'y':
            print("Uninstallation aborted.")
            return
        print("Uninstalling dependencies listed in requirements.txt...")
        try:
            # Use pip to uninstall all packages in requirements.txt
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-r", "requirements.txt", "-y"])
            print("Dependencies uninstalled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling dependencies: {e}")
            sys.exit(1)
    else:
        print("No requirements.txt found. Skipping uninstallation.")

# Step 2: Detect system architecture (Intel or ARM)
def detect_architecture():
    """
    Detect the system architecture (Intel or ARM).
    """
    arch = platform.machine().lower()  # Returns machine type (e.g., 'x86_64' for Intel, 'arm64' for ARM)
    if 'arm' in arch:
        print("ARM architecture detected.")
        return 'arm64'
    elif 'x86_64' in arch:
        print("Intel architecture detected.")
        return 'x86_64'
    else:
        print(f"Unknown architecture: {arch}")
        return None

# Check if we are in a virtual environment
def check_virtualenv():
    """
    Ensure we are in a virtual environment before proceeding.
    """
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("You are already in a virtual environment.")
    else:
        sys.exit("No virtual environment found. Please activate your virtual environment before running this script.")

# Main script logic
if __name__ == "__main__":
    check_virtualenv()  # Ensure virtual environment is active
    architecture = detect_architecture()  # Detect architecture
    if architecture is None:
        sys.exit("Unsupported architecture. Exiting...")
    
    uninstall_requirements()  # Step 1: Uninstall packages from requirements.txt

    # Add architecture-specific logic here if necessary
    if architecture == 'arm64':
        print("ARM-specific tasks can be added here.")
        # Example: Uninstall ARM-specific packages
    elif architecture == 'x86_64':
        print("Intel-specific tasks can be added here.")
        # Example: Uninstall Intel-specific packages
