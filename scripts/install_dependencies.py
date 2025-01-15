import subprocess  # For running commands
import sys  # For accessing Python's runtime environment
import os  # For file and directory handling
import shutil  # For removing directories
import platform  # For detecting system architecture

## Create Virtual Environment fot Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script
# python3 install_dependencies.py

# Step 1: Function to install packages listed in requirements.txt
def install_requirements():
    """
    Install all dependencies listed in requirements.txt.
    """
    if os.path.exists("requirements.txt"):
        print("Installing dependencies listed in requirements.txt...")
        try:
            # Use pip to install all packages in requirements.txt
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print("No requirements.txt found. Skipping installation.")

# Step 2: Function to create a virtual environment (if not already created)
def create_virtual_env(venv_path="venv"):
    """
    Create a virtual environment at the specified path if it does not exist.
    """
    venv_full_path = os.path.expanduser(venv_path)
    if not os.path.exists(venv_full_path):
        print(f"Creating virtual environment at {venv_full_path}...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_full_path])
            print(f"Virtual environment created at {venv_full_path}.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print(f"Virtual environment already exists at {venv_full_path}. Skipping creation.")

# Step 3: Detect system architecture (Intel or ARM)
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
    
    create_virtual_env()  # Step 1: Create virtual environment if not exists
    install_requirements()  # Step 2: Install packages from requirements.txt

    # Add architecture-specific logic here if necessary
    if architecture == 'arm64':
        print("ARM-specific tasks can be added here.")
        # Example: Install ARM-specific dependencies or tools
    elif architecture == 'x86_64':
        print("Intel-specific tasks can be added here.")
        # Example: Install Intel-specific dependencies or tools
