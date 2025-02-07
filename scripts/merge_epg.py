# merge_epg.py Feb 6 2025 905p
import xml.etree.ElementTree as ET
import os
import io
import subprocess  # Add this import to resolve the error
from time import sleep
import sys # Used for venv_python
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
# import fcntl


# Define REPO_DIR at the top of merge_epg.py if it's not already defined
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # This will set REPO_DIR to the script's directory
venv_python = sys.executable # Relative path from the script to the virtual environment
print(venv_python)
print("Starting data processing...")



# # Step 0: Run this script on schedule
# import schedule

# # Lock file path
# lock_file_path = "merge_epg.lock"

# def run_merge_epg():
#     # Get the directory of the current script
#     script_dir = os.path.dirname(os.path.abspath(__file__))

#     # Path to the virtual environment Python
#     venv_python = os.path.join(script_dir, "venv", "bin", "python3")

#     # Path to the `merge_epg.py` script
#     merge_epg_path = os.path.join(script_dir, "merge_epg.py")

#     # Path for the lock file to prevent multiple script instances
#     lock_file_path = os.path.join(script_dir, "merge_epg.lock")

#     # Check if the lock file already exists (indicating another instance is running)
#     if os.path.exists(lock_file_path):
#         print("Script is already running. Skipping execution.")
#         return

#     # Create the lock file to indicate the script is running
#     with open(lock_file_path, 'w') as lock_file:
#         try:
#             print("Lock file created. Running the script...")

#             # Define the command to run your Python script
#             command = f'{venv_python} {merge_epg_path}'

#             # Run the command
#             result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             print(f"stdout: {result.stdout.decode()}")
#             print(f"stderr: {result.stderr.decode()}")

#         except (subprocess.CalledProcessError, IOError) as e:
#             print(f"Error occurred: {e}")

#         finally:
#             # Delete the lock file once the script finishes
#             if os.path.exists(lock_file_path):
#                 os.remove(lock_file_path)
#             print("Lock file removed. Script execution finished.")

# # Schedule the job at 2:36 AM and 2:36 PM
# schedule.every().day.at("02:36").do(run_merge_epg)  # 2:36 AM
# schedule.every().day.at("14:36").do(run_merge_epg)  # 2:36 PM

# # Infinite loop to keep the scheduler running
# while True:
#     schedule.run_pending()
#     time.sleep(1)



# Step 1: Set up Logging
# Get current time for logging
formatted_time = datetime.now().strftime("%b %d %Y %H:%M:%S")
print(formatted_time)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the log file path
log_file_path = os.path.join(script_dir, 'www', 'merge_epg.log')

# Ensure the 'www' directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Overwrite log file by opening in 'w' mode
with open(log_file_path, 'w'):
    pass  # This clears the file

# Set up logging configuration
log_format = "%(asctime)s - %(levelname)s - %(message)s"
date_format = "%b %d %Y %H:%M:%S"

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    filemode='w'  # Overwrites file each time the script runs
)

# Create a logger instance
logger = logging.getLogger(__name__)

# Define SuccessFilter to filter messages
class SuccessFilter(logging.Filter):
    def filter(self, record):
        return "EPG file successfully saved" in record.getMessage()

# Create a RotatingFileHandler (if needed)
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5 * 1024 * 1024, backupCount=4  # 5 MB limit, keep 4 backups
)
file_handler.setFormatter(logging.Formatter(log_format, date_format))
file_handler.addFilter(SuccessFilter())

# Add the file handler to the logger
logger.addHandler(file_handler)

# Log the start of the process
logger.info("Starting EPG merge process...")

# Step 2.1: Function to run dummy_epg.py script
def run_dummy_epg():
    """Runs the dummy EPG generation script."""
    try:
        # Define paths
        script_dir = os.path.dirname(os.path.realpath(__file__))  # Current script directory
        dummy_epg_path = os.path.join(script_dir, "dummy_epg.py")  # Path to dummy_epg.py
        venv_python = os.path.join(sys.prefix, "bin", "python3")

        # Debugging: Print paths
        print(f"dummy_epg_path: {dummy_epg_path}")
        print(f"venv_python: {venv_python}")

        # Run the dummy_epg.py script
        result = subprocess.run(
            [venv_python, dummy_epg_path],
            check=True,
            capture_output=True,
            text=True
        )

        # Output success
        print("dummy_epg.py executed successfully")
        print(result.stdout)  # Output from dummy_epg.py

    except subprocess.CalledProcessError as e:
        # Output error
        print(f"Error while running dummy_epg.py: {e}")
        print(e.stderr)

# Run dummy_epg.py
if __name__ == "__main__":
    run_dummy_epg()

# Step 2.2: Function to load channel data from a JSON file (  channels.json  )
# Include channels_json.xml in epg_urls.txt 
# python3 merge_epg.py
import re # Count / Log  Channels

def run_npm_grab():
    # Get current date and time for timestamping the output file
    # current_datetime = datetime.now().strftime("%m-%d-%I-%M-%S %p")
    current_datetime = datetime.now().strftime("%Y-%m-%d-%I-%M-%S %p")
    # List of npm commands with timestamped output file
    commands = [
        ["npm", "run", "grab", "--", 
        #  f"--channels=./scripts/_epg-start/channels-custom-start.xml", 
        #  f"--output=./scripts/_epg-end/channels-custom-{current_datetime}.xml"]

         f"--channels=./scripts/_epg-start/channels-test-start.xml", 
         f"--output=./scripts/_epg-end/channels-test--{current_datetime}.xml"]

        #  f"--channels=./scripts/_epg-start/channels-test-start-copy.xml", 
        #  f"--output=./scripts/_epg-end/channels-test-copy{current_datetime}.xml"]

    ]
    # Set the output directory for deleting old files
    output_dir = os.path.join(script_dir, "_epg-end")
    # Delete all older files except the latest one
    try:
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)

            # Check if the file matches the pattern 'dummy-YYYY-MM-DD-HH-MM-SS AM/PM.xml' and is not the latest file
            if file_name.startswith("channels-") and file_name != f"channels-{current_datetime}.xml":
                os.remove(file_path)
                print(f"Old file {file_path} deleted.")
    except Exception as e:
        print(f"Error deleting old files: {e}")

    for command in commands:
        try:
            # Combine the command into a string for logging and display
            command_str = ' '.join(command)
            logger.info(f"Running command: {command_str}")
            print(f"Running command: {command_str}")

            # Run the command and capture output
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            stdout_output = []
            stderr_output = []

            # Process stdout and capture lines
            for line in process.stdout:
                stripped_line = line.strip()
                stdout_output.append(stripped_line)
                logger.info(f"STDOUT: {stripped_line}")
                print(f"STDOUT: {stripped_line}")

            # Process stderr and capture lines
            for line in process.stderr:
                stripped_line = line.strip()
                stderr_output.append(stripped_line)
                logger.error(f"STDERR: {stripped_line}")
                print(f"STDERR: {stripped_line}")

            # Wait for process completion
            process.wait()

            # Check for successful execution
            if process.returncode == 0:
                logger.info(f"Command {command_str} executed successfully.")
                print(f"Command {command_str} executed successfully.")

                # Extract and log the number of channels found
                channel_count_pattern = r"found (\d+) channel\(s\)"
                for line in stdout_output:
                    match = re.search(channel_count_pattern, line)
                    if match:
                        channel_count = match.group(1)
                        logger.info(f"Found {channel_count} channel(s) in the output.")
                        print(f"Found {channel_count} channel(s) in the output.")
                        break  # Stop after the first match
            else:
                logger.error(f"Command {command_str} failed with error code {process.returncode}.")
                print(f"Command {command_str} failed with error code {process.returncode}.")

        except Exception as e:
            logger.error(f"Error while running npm command {command_str}: {e}")
            print(f"Error while running npm command {command_str}: {e}")

# Run the process
if __name__ == "__main__":
    run_npm_grab()    



# Step 4: Main merge_epg function
def merge_epg_data():
    """Coordinates the EPG generation and merging process."""

    print("Merging EPG data...") # Proceed with EPG merging logic

# Execute the process
if __name__ == "__main__":
    merge_epg_data()

# Step 5: Function to read the EPG URLs from a file
def load_epg_urls(file_path):
    """Read EPG URLs from the specified file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            epg_urls = [line.strip() for line in file.readlines() if line.strip()]  # Remove empty lines and strip whitespace
        return epg_urls
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

# Step 6: Check for XML files if no URLs are found
def load_local_xml_files(directory):
    """Look for XML files in the directory if no EPG URLs are found."""
    xml_files = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                xml_files.append(os.path.join(directory, filename))  # Add XML file path to the list
        return xml_files
    except Exception as e:
        print(f"Error loading XML files from {directory}: {e}")
        return []

# Get the directory where the script is located (absolute path)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # Ensure the 'log' directory exists

# Relative path to the epg_urls.txt file
epg_urls_file = os.path.join(script_dir, '_epg-start', 'epg_urls.txt')

# Load EPG URLs using the relative path
epg_urls = load_epg_urls(epg_urls_file)

# Check if URLs are found, if not, look for XML files in the _epg-end directory
if not epg_urls:
    # Use a relative path to the _epg-end directory
    epg_end_dir = os.path.join(script_dir, '_epg-end')  # Relative path to _epg-end directory
    print(f"No EPG URLs found in {epg_urls_file}, scanning {epg_end_dir} for XML files...")
    epg_urls = load_local_xml_files(epg_end_dir)

# Print out the list of EPG URLs or local XML files found
print("EPG URLs or local XML files found:", epg_urls)

# Step 7: Path to save the merged EPG file
save_path = os.path.join(REPO_DIR, "www", "epg.xml")  # Path where the EPG file will be saved
gz_directory = os.path.join(REPO_DIR, "www")  # Directory where .gz files are located

# Step 8: Function to ensure directory and file permissions
def ensure_permissions(file_path):
    # Ensure the directory exists
    directory = os.path.dirname(file_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it...")
        os.makedirs(directory, exist_ok=True)

    # Check if we have write permissions on the directory, and if not, set it
    if not os.access(directory, os.W_OK):
        print(f"Directory {directory} does not have write permissions. Updating permissions...")
        os.chmod(directory, 0o755)  # Set write permission for the directory owner

    # If the file already exists, check and ensure it has write permissions
    if os.path.exists(file_path):
        if not os.access(file_path, os.W_OK):
            print(f"File {file_path} does not have write permissions. Updating permissions...")
            os.chmod(file_path, 0o644)  # Set write permission for the file owner
    else:
        print(f"File {file_path} does not exist. It will be created.")

# Ensure permissions for the save path
ensure_permissions(save_path)


# Step 9: Function to fetch and merge EPG data
import requests
import gzip

def fetch_epg_data(url, index, total, retries=3, delay=5):
    logging.info(f"Fetching {index + 1}/{total} - {url}")
    print(f"Fetching {index + 1}/{total} - {url}")

    attempt = 0
    while attempt < retries:
        try:
            if url.startswith('http'):  # Step 5.1: Handle remote URLs
                response = requests.get(url, timeout=10)  # Timeout to avoid hanging
                if response.status_code == 200:
                    try:
                        if url.endswith('.gz'):  # Step 5.2: Handle .gz files (compressed XML)
                            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                                xml_content = gz.read()
                            epg_tree = ET.ElementTree(ET.fromstring(xml_content))
                        else:
                            epg_tree = ET.ElementTree(ET.fromstring(response.content))
                        print(f"Successfully fetched {index + 1}/{total}")
                        logging.info(f"Successfully fetched {index + 1}/{total}")
                        return epg_tree
                    except ET.ParseError as e:
                        logging.error(f"XML parse error for {url}: {e}")
                        print(f"XML parse error for {url}: {e}")
                        return None
                    except Exception as e:
                        logging.error(f"Error processing {url}: {e}")
                        print(f"Error processing {url}: {e}")
                        return None
                else:
                    logging.error(f"Error fetching {url}: HTTP {response.status_code}")
                    print(f"Error fetching {url}: HTTP {response.status_code}")
                    return None
            else:  # Step 5.3: Handle local XML files
                try:
                    epg_tree = ET.parse(url)
                    print(f"Successfully loaded local file: {url}")
                    logging.info(f"Successfully loaded local file: {url}")
                    return epg_tree
                except ET.ParseError as e:
                    logging.error(f"Failed to parse local XML file {url}: {e}")
                    print(f"Failed to parse local XML file {url}: {e}")
                except Exception as e:
                    logging.error(f"Error processing local file {url}: {e}")
                    print(f"Error processing local file {url}: {e}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            attempt += 1
            time.sleep(delay)  # Wait before retrying
    return None  # Return None after all attempts fail    

# Function to extract XML from .gz files
import log 
def extract_gz_files(gz_directory):
    """Extract .gz files in the specified directory."""
    # Make sure you're using the correct directory
    gz_directory = os.path.join(REPO_DIR, "www")  # Ensure this points to the right directory

    if not os.path.exists(gz_directory):
        log(f"Error: Directory {gz_directory} does not exist.")
        return []

    extracted_files = []
    for filename in os.listdir(gz_directory):
        if filename.endswith(".gz"):
            file_path = os.path.join(gz_directory, filename)
            log(f"Extracting {file_path}...")
            # Your extraction code here
            extracted_files.append(file_path)
    return extracted_files


# Step 10: Merge EPG data into a single XML
merged_root = ET.Element("tv")
total_files = len(epg_urls)


# Step 11: Process each EPG URL
for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress


# Step 12: Extract XML from .gz files
print("Extracting XML from .gz files...")
extracted_files = extract_gz_files(gz_directory)
for xml_file in extracted_files:
    try:
        epg_tree = ET.parse(xml_file)
        for element in epg_tree.getroot():
            merged_root.append(element)
    except ET.ParseError as e:
        logging.error(f"Failed to parse extracted XML file {xml_file}: {e}")
        print(f"Failed to parse extracted XML file {xml_file}: {e}")


# Get the current Eastern Time
import pytz # Timezone

eastern = pytz.timezone('US/Eastern')
current_time_et = datetime.now(eastern).strftime("%b %d, %Y %H:%M:%S %p")


# Step 13: Save the merged EPG/log file and push to Github
# python3 merge_epg.py

# Define directories to auto-commit
script_dir = os.path.dirname(os.path.abspath(__file__))
directories_to_commit = [
    os.path.join(script_dir, "www"),
    os.path.join(script_dir, "_epg-end"),
    os.path.join(script_dir, "scripts"),
]

# Get the current time for logging and commit messages
current_time_et = datetime.now().strftime("%b %d, %Y %I:%M:%S %p")

def run_command(cmd, check=True, capture_output=False):
    """Run a shell command with error handling."""
    try:
        result = subprocess.run(cmd, check=check, text=True, capture_output=capture_output)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Command failed: {' '.join(cmd)}\nError: {e}")
        return None

try:
    print("🔄 Pulling latest changes from GitHub (rebase mode)...")
    
    # 🔹 Ensure there are no unstaged deletions before pulling
    run_command(["git", "add", "-A"])
    
    pull_result = run_command(["git", "pull", "--rebase", "origin", "main"], check=False)

    if pull_result is None:
        print("⚠️ Git rebase failed. Attempting automatic fix...")

        run_command(["git", "stash"])
        run_command(["git", "pull", "--rebase", "origin", "main"])
        run_command(["git", "stash", "pop"])

    print("📌 Staging all changes (new, modified, deleted files)...")
    run_command(["git", "add", "-A"])

    # 🔹 Check for staged changes
    staged_changes = run_command(["git", "diff", "--cached", "--quiet"], check=False)

    if staged_changes is None:
        commit_message = f"Auto commit at {current_time_et} ET"
        print(f"✅ Changes detected. Committing: {commit_message}")
        run_command(["git", "commit", "-m", commit_message])

        print("🚀 Pushing changes to GitHub...")
        push_result = run_command(["git", "push", "origin", "main"], check=False)

        if push_result is None:
            print("⚠️ Git push failed. Checking branch status...")

            # 🔹 Check if remote branch has diverged
            branch_status = run_command(["git", "status", "-uno"], capture_output=True)
            if "Your branch is ahead" in branch_status:
                print("⚠️ Force-pushing with lease...")
                run_command(["git", "push", "--force-with-lease", "origin", "main"])
            else:
                print("✅ Everything is already up to date.")

    else:
        print("✅ No changes to commit. Skipping push.")

except Exception as e:
    logging.error(f"🚨 Unexpected Error: {str(e)}")
    print(f"🚨 Unexpected Error: {str(e)}")