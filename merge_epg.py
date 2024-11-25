import requests
import xml.etree.ElementTree as ET
import logging
import os
import gzip
import io
import subprocess
from time import sleep
import sys
import socket
import time  # Missing import for time.sleep

# See Android TV sheets doc, nginx tab for commands,
# sudo nginx -s reload

## Create Virtual Environment for Python
# python3 -m venv ~/venv
# source ~/venv/bin/activate

## Run this script
# python3 merge_epg.py

# Below used to grab xumo.tv (5.1 mb xml file) and other sites https://github.com/iptv-org/epg
# npm run grab -- --site=xumo.tv

# https://i.mjh.nz/
# http://10.0.0.30:8080/epg.xml

# Step 1: Define the path to your virtual environment python
venv_python = os.path.join(os.getenv('HOME'), 'venv/bin/python')  # Adjust this if necessary

# Step 2: Define script directory
script_dir = os.path.dirname(os.path.abspath(__file__))  # Path to the directory where the script is located

# Step 3: Define the path to your dummy_epg.py script
dummy_epg_path = os.path.join(script_dir, "dummy_epg.py")
print(dummy_epg_path)  # To verify the constructed path

# Step 3.1: Define the npm command and arguments (requires npm install)
command = ["npm", "run", "grab", "--", "--site=xumo.tv"]

# Step 3.2: Run the npm command
try:
    # Navigate to the directory containing your package.json, if necessary
    os.chdir(script_dir)
    
    # Run the npm command
    print(f"Running command: {' '.join(command)}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Show progress from the stdout of the npm command
    for line in process.stdout:
        print(f"Progress: {line.strip()}")  # Display each line of output from the command

    # Wait for the process to complete
    process.wait()

    # Check for errors in stderr
    if process.returncode == 0:
        print("npm command completed successfully.")
    else:
        # Capture any error messages from stderr
        error_message = process.stderr.read()
        print("Error while running npm command:")
        print(error_message)

except subprocess.CalledProcessError as e:
    # Handle errors if the npm command fails
    print("Error while running npm command:")
    print(e.stderr)
except FileNotFoundError:
    # Handle the case where npm is not installed or the command is invalid
    print("Error: npm command not found. Ensure Node.js and npm are installed and in your PATH.")

# Step 4: Function to fetch EPG data from URLs
def fetch_epg_data(url, index, total, retries=3, delay=5):
    logging.info(f"Fetching {index + 1}/{total} - {url}")
    print(f"Fetching {index + 1}/{total} - {url}")
    
    attempt = 0
    while attempt < retries:
        try:
            if url.startswith('http'):  # Handle remote URLs
                response = requests.get(url, timeout=10)  # Timeout to avoid hanging
                if response.status_code == 200:
                    try:
                        if url.endswith('.gz'):  # Handle compressed .gz files
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
            else:  # Handle local XML files
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

    logging.error(f"Failed to fetch {url} after {retries} attempts.")
    print(f"Failed to fetch {url} after {retries} attempts.")
    return None


# Step 5: Function to run dummy_epg.py script
def run_dummy_epg():
    try:
        # Using the virtual environment's Python interpreter to run the script
        result = subprocess.run([venv_python, dummy_epg_path], check=True, capture_output=True, text=True)
        print("dummy_epg.py executed successfully")
        print(result.stdout)  # Output from dummy_epg.py
    except subprocess.CalledProcessError as e:
        print(f"Error while running dummy_epg.py: {e}")
        print(e.stderr)


# Step 6: Function to merge EPG data
def merge_epg_data():
    # Execute the dummy_epg.py script before merging
    run_dummy_epg()
    print("Merging EPG data...")
    # The merging process would go here...

# Step 7: Example call to merge_epg_data, where you run the dummy_epg.py script
merge_epg_data()

# Step 8: Read EPG URLs from a file
def read_epg_urls_from_file(file_path):
    epg_urls = []
    try:
        with open(file_path, 'r') as file:
            # Strip out empty lines or comments
            epg_urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
        print(f"Read {len(epg_urls)} EPG URLs from {file_path}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return epg_urls

# Step 9: Read and process EPG data
epg_urls_file = os.path.join(script_dir, "epg_urls.txt")
epg_urls = read_epg_urls_from_file(epg_urls_file)

# Step 10: Path to save the merged EPG file
save_path = "/usr/local/var/www/epg.xml"  # Path for Nginx serving
gz_directory = "/usr/local/var/www/"  # Path for .gz file storage

# Step 11: Log directory setup
log_dir = os.path.join(script_dir, "log")  # Log directory setup
log_file = os.path.join(log_dir, "merge_epg.log")  # Log file setup

# Step 12: Ensure log directory exists
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# Step 13: Set up logger to capture error-level logs
logger = logging.getLogger()
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # Set to INFO instead of ERROR

# Log the start of the process
logger.info("Starting EPG merge process...")

# Step 15: Initialize merge counters
success_count = 0
total_urls = len(epg_urls)  # Total URLs to process

# Step 16: Define the SUCCESS log level
SUCCESS_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def log_success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

# Add the success method to the logger class
logging.Logger.success = log_success

# Configure logging to only log the essential messages
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Step 17: Initialize merge counters
success_count = 0
total_urls = len(epg_urls)  # Total URLs to process
merged_root = None

# Step 18: Log starting message
logger.info("Starting EPG merge process...")

# Step 18: Fetch and merge EPG data
for i, url in enumerate(epg_urls):
    # Step 18.1: Fetch EPG data from the URL
    epg_tree = fetch_epg_data(url, i, total_urls)  # Fetch data from each URL
    
    # Step 18.2: Check if EPG data was successfully fetched
    if epg_tree is not None:
        # Step 18.3: Merge the fetched data
        if merged_root is None:
            merged_root = epg_tree.getroot()  # Initialize with first data
        else:
            merged_root.extend(epg_tree.getroot())  # Merge subsequent data
        
        # Step 18.4: Increment the success counter
        success_count += 1  # Increment success counter
    # Step 18.5: Log fetch failure (Only failed fetches are logged)
    else:
        # Suppress individual fetch log
        continue

# Step 19: Log merge results
if merged_root is not None:
    try:
        # Step 19.1: Save merged XML as .xml (instead of .gz)
        save_file_path = os.path.join(gz_directory, "epg.xml")  # Change the file extension to .xml
        
        # Step 19.2: Write the merged data to a standard XML file
        with open(save_file_path, 'wb') as f:
            merged_tree = ET.ElementTree(merged_root)
            merged_tree.write(f)  # Write XML to file

        # Step 20: Log success message
        if success_count == total_urls:
            # Step 20.1: Log success if all URLs were merged
            logger.success(f"EPG file successfully saved after merging {success_count}/{total_urls} URLs to {save_file_path}")
            print(f"EPG file successfully saved after merging {success_count}/{total_urls} URLs to {save_file_path}")
    except Exception as e:
        # Step 20.4: Log error if there's an issue during the saving process
        logger.error(f"Error saving merged EPG file: {e}")
        print(f"Error saving merged EPG file: {e}")
else:
    # Step 19.3: Log error if no data was merged
    logger.error("No EPG data to merge.")
    print("No EPG data to merge.")
