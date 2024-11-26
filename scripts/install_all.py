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

# Function to run a Python script
def run_script(script_path):
    try:
        print(f"Running script: {script_path}...")
        subprocess.check_call([sys.executable, script_path])
        print(f"Script {script_path} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_path}: {e}")

# Main function to handle the installation logic
def main():
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
