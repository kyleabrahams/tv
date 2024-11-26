import subprocess
import sys
import os

# Function to prompt the user with a y/n question
def prompt_user(script_name, question):
    """
    Prompt the user with a custom question specific to the script being run.
    """
    while True:
        user_input = input(f"{question} ({script_name}) (y/n): ").lower()
        if user_input in ['y', 'n']:
            return user_input == 'y'
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# Function to run a Python script
def run_script(script_path):
    """
    Execute a Python script using subprocess.
    """
    try:
        print(f"Running script: {script_path}...")
        subprocess.check_call([sys.executable, script_path])
        print(f"Script {script_path} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_path}: {e}")

# Main function to handle the uninstall logic
def main():
    # Corrected path to the first uninstall script
    script1_path = os.path.join(os.getcwd(), 'uninstall_dependencies.py')

    # Corrected path to the second uninstall script
    script2_path = os.path.join(os.getcwd(), 'uninstall_nginx.py')

    # Check if the first script exists to prevent errors
    if os.path.exists(script1_path):
        # Ask if the user wants to uninstall dependencies
        if prompt_user("uninstall_dependencies.py", "Do you want to uninstall all the dependencies for this repository?"):
            run_script(script1_path)  # Run the first uninstall script
    else:
        print(f"Script {script1_path} not found. Please check the script location.")

    # Check if the second script exists to prevent errors
    if os.path.exists(script2_path):
        # Ask if the user wants to uninstall Nginx
        if prompt_user("uninstall_nginx.py", "Do you want to uninstall and remove Nginx configurations?"):
            run_script(script2_path)  # Run the second uninstall script
    else:
        print(f"Script {script2_path} not found. Please check the script location.")

if __name__ == "__main__":
    main()
