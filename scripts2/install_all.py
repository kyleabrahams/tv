import subprocess
import sys
import os

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script
# python3 install_all.py

# Function to prompt the user with a y/n question, including script name and custom prompt message
def prompt_user(script_name, question):
    while True:
        user_input = input(f"{question} ({script_name}) (y/n): ").lower()
        if user_input in ['y', 'n']:
            return user_input == 'y'
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# Function to ensure script has executable permissions (chmod +x)
def ensure_executable(script_path):
    """Ensure the script has executable permissions."""
    try:
        if not os.access(script_path, os.X_OK):
            print(f"Setting executable permissions for {script_path}...")
            subprocess.check_call(["chmod", "+x", script_path])
            print(f"Permissions set for {script_path}.")
        else:
            print(f"{script_path} already has executable permissions.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting permissions for {script_path}: {e}")

# Function to run a Python script
def run_script(script_path):
    try:
        # Ensure the script has executable permissions
        ensure_executable(script_path)
        
        print(f"Running script: {script_path}...")
        subprocess.check_call([sys.executable, script_path])
        print(f"Script {script_path} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_path}: {e}")

# Function to create and activate a virtual environment
def setup_virtualenv(venv_path="venv"):
    """
    Create a virtual environment and restart the script within it.
    """
    venv_path = os.path.abspath(venv_path)
    print(f"Resolved virtual environment path: {venv_path}")
    
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_path])
            print("Virtual environment created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print(f"Virtual environment already exists at {venv_path}.")
    
    # Determine the Python executable in the virtual environment
    venv_python = os.path.join(venv_path, "bin", "python3")
    print(f"Resolved virtual environment Python path: {venv_python}")
    
    if not os.path.exists(venv_python):
        print(f"Error: Python executable not found at {venv_python}.")
        sys.exit(1)
    
    # Restart the script within the virtual environment
    if sys.executable != venv_python:
        print(f"Restarting script within the virtual environment at {venv_path}...")
        print(f"sys.argv: {sys.argv}")
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print("Script is already running within the virtual environment.")

# Function to install requests within the virtual environment
def install_requests():
    print("Installing requests library...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("requests library installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requests: {e}")
        sys.exit(1)

# Main function to handle the installation logic
def main():
    # Ensure the script is running in a virtual environment
    setup_virtualenv("venv")
    print("Virtual environment setup complete. Proceeding with installation...")

    # Install the requests library
    install_requests()

    # Define the relative paths to the Python scripts
    script_1_path = os.path.join(os.getcwd(), 'install_dependencies.py')  # Simplified path
    script_2_path = os.path.join(os.getcwd(), 'install_nginx.py')  # Simplified path

    # Ensure the scripts exist before proceeding
    if not os.path.exists(script_1_path):
        print(f"Error: {script_1_path} not found.")
        return

    if not os.path.exists(script_2_path):
        print(f"Error: {script_2_path} not found.")
        return

    # Ask if the user wants to install all necessary dependencies (custom prompt)
    if prompt_user("install_dependencies.py", "Do you want to install all necessary dependencies needed for this repository?"):
        run_script(script_1_path)  # Run the first script

    # Ask if the user wants to install Nginx (custom prompt)
    if prompt_user("install_nginx.py", "Do you want to install Nginx for automating the renewal of the epg.xml file?"):
        run_script(script_2_path)  # Run the second script

if __name__ == "__main__":
    main()
