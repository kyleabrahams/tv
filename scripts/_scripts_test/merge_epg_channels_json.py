import requests
import xml.etree.ElementTree as ET
import os
import gzip
import io
import subprocess  # Add this import to resolve the error
from time import sleep
import sys # Used for venv_python
from datetime import datetime
import time
import logging

# Get the current time and format it
formatted_time = datetime.now().strftime("%b %d %Y %H:%M:%S")
print(formatted_time)


# See Android TV sheets doc, nginx tab for commands,
# sudo nginx -s reload
# python3 merge_epg.py

# Below used to grab xumo.tv (5.1 mb xml file) and other sites https://github.com/iptv-org/epg
# npm run grab -- --site=xumo.tv
# npm run grab -- --channels=sites/ontvtonight.com/ontvtonight.com_ca.channels.xml --output=./scripts/ontvtonight.com_ca.channels.xml
# npm run channels:parse --- --config=./sites/ontvtonight.com/ontvtonight.com.config.js --output=./scripts/ontvtonight.com_ca.channels.xml --set=country:ca


# Define REPO_DIR at the top of merge_epg.py if it's not already defined
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # This will set REPO_DIR to the script's directory

# Relative path from the script to the virtual environment
venv_python = sys.executable
print(venv_python)
import os


# Step 1.1: Function to run dummy_epg.py script
script_dir = os.path.dirname(os.path.realpath(__file__)) # Get the directory of the current script of dummy_epg.py
dummy_epg_path = os.path.join(script_dir, "dummy_epg.py") # Construct the relative path
print(dummy_epg_path)  # To verify the constructed path

def run_dummy_epg():
    """Runs the dummy EPG generation script."""
    try:
        # Example paths
        venv_python = "./venv/bin/python3"  # Adjust to your virtual environment path
        dummy_epg_path = "dummy_epg.py"  # Adjust to your script location

        # Use the virtual environment's Python interpreter
        result = subprocess.run([venv_python, dummy_epg_path], check=True, capture_output=True, text=True)
        print("dummy_epg.py executed successfully")
        print(result.stdout)  # Output from dummy_epg.py
    except subprocess.CalledProcessError as e:
        print(f"Error while running dummy_epg.py: {e}")
        print(e.stderr)

# Run dummy_epg.py
run_dummy_epg()




# Step 1.2: Function to load channel data from a JSON file (  channels.json  ) (  Include channels_json.xml in epg_urls.txt)
import json  # Import the json module to read from a JSON file

def load_channels_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading channels from file: {e}")
        return {}

# Function to fetch the EPG data for a specific channel
def fetch_epg_data(channel_id, date):
    url = f"https://epg.pw/api/epg.xml?lang=en&date={date}&channel_id={channel_id}"
    try:
        # Send the request to fetch the EPG data for the channel
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse the XML data
            epg_tree = ET.ElementTree(ET.fromstring(response.content))
            return epg_tree
        else:
            print(f"Error fetching data for channel {channel_id}: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for channel {channel_id}: {e}")
        return None

# Function to fetch EPG data for multiple channels
def fetch_multiple_channels_data(channel_dict):
    current_date = datetime.now().strftime("%Y%m%d") # Get the current date in YYYYMMDD format
    tv_root = ET.Element("tv") # Create the root <tv> element for the XML
    channels_str = "" # String to hold the formatted channel data
    
    # Loop through all the channels in the dictionary and fetch the EPG data for each
    for channel_id, channel_name in channel_dict.items():
        print(f"Fetching EPG data for {channel_name} (Channel ID: {channel_id}) on {current_date}...")
        epg_data = fetch_epg_data(channel_id, current_date)
        if epg_data:
            # Get the channel element and convert it to a string
            channel_element = epg_data.getroot().find("channel")
            if channel_element is not None:
                # Manually build the channel element string on a single line
                channel_str = ET.tostring(channel_element, encoding="unicode").strip()
                channels_str += channel_str  # Add it to the channels_str
    
            # Append the <programme> elements to the root of the XML
            for programme in epg_data.getroot().findall("programme"):
                tv_root.append(programme)

    # Create a new tree with the root <tv> element and the combined channel data
    tv_str = f"<?xml version='1.0' encoding='utf-8'?>\n<tv>{channels_str}\n"
    
    # Append the programmes at the end of the XML
    for programme in tv_root.findall('programme'):
        tv_str += ET.tostring(programme, encoding="unicode").strip() + "\n"
    
    tv_str += "</tv>"
    
    # Save the final XML to a file
    with open("channels_json.xml", "w", encoding="utf-8") as f:
        f.write(tv_str)
    
    print("Combined EPG data saved to channels_json.xml")

# Load the channel dictionary from the JSON file
channel_dict = load_channels_from_file('channels.json')

# Check if channel_dict is empty before proceeding
if not channel_dict:
    print("No channels to fetch EPG data for. Exiting.")
else:
    # Display the number of channels found
    total_channels = len(channel_dict)
    print(f"Loaded {total_channels}/{total_channels} channels from channels.json successfully.")
    
    # Record the start time
    start_time = time.time()

    # Fetch EPG data for all channels and create the combined XML
    fetch_multiple_channels_data(channel_dict)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

# Function to merge EPG data step
def merge_epg():
    # Load the channel dictionary from the JSON file    https://epg.pw/index.html?lang=en
    channel_dict = load_channels_from_file('channels.json')

    # Record the start time
    start_time = time.time()

    # Fetch EPG data for all channels and create the combined XML
    fetch_multiple_channels_data(channel_dict)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    merge_epg()





# Step 2: Function to run the npm grab command and show real-time output https://github.com/iptv-org/epg/tree/master/sites
# npm run grab --- --channels=channels_custom_start.xml --output ./scripts/channels_custom_end.xml
def run_npm_grab():
    # List of npm commands
    commands = [
        ["npm", "run", "grab", "--", "--channels=channels_custom_start.xml", "--output", "./scripts/channels_custom_end.xml"]
        # ["npm", "run", "grab", "--", "--channels=test_start.xml", "--output", "./scripts/test_end.xml"]
    ]

    for command in commands:
            try:
                print(f"Running command: {' '.join(command)}")
                # Use Popen for real-time output
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Stream stdout and stderr as the command runs
                for line in process.stdout:
                    print(f"STDOUT: {line.strip()}")  # Real-time standard output

                for line in process.stderr:
                    print(f"STDERR: {line.strip()}")  # Real-time error output

                process.wait()  # Wait for the process to complete

                if process.returncode == 0:
                    print(f"Command {' '.join(command)} executed successfully.")
                else:
                    print(f"Command {' '.join(command)} failed with error code {process.returncode}.")
            except Exception as e:
                print(f"Error while running npm command: {e}")    

run_npm_grab() # Run npm grab commands




# Step 3: Main merge_epg function
def merge_epg_data():
    """Coordinates the EPG generation and merging process."""

    print("Merging EPG data...") # Proceed with EPG merging logic

# Execute the process
if __name__ == "__main__":
    merge_epg_data()

# Step 4: Function to read the EPG URLs from a file
def load_epg_urls(file_path):
    """Read EPG URLs from the specified file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            epg_urls = [line.strip() for line in file.readlines() if line.strip()]  # Remove empty lines and strip whitespace
        return epg_urls
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

script_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory where the script is located (absolute path)
log_file_path = os.path.join(script_dir, 'log', 'merge_epg.log') # Create the relative path for the log file
os.makedirs(os.path.dirname(log_file_path), exist_ok=True) # Ensure the 'log' directory exists

# # Now log the message using the relative path
# import logging
# log_format = "%(asctime)s - %(message)s"
# date_format = "%b %d %Y %H:%M:%S"

# logging.basicConfig(filename=log_file_path,
#                     level=logging.INFO,
#                     format=log_format,
#                     datefmt=date_format)

# logging.info("This is a log entry with the formatted timestamp.") # Example of logging a message

# Relative path to the epg_urls.txt file
epg_urls_file = os.path.join(script_dir, 'epg_urls.txt')

# Load EPG URLs using the relative path
epg_urls = load_epg_urls(epg_urls_file)

# Now you can use the epg_urls list in the rest of your script
print(epg_urls)

# Step 5: Path to save the merged EPG file
save_path = os.path.join(REPO_DIR, "www", "epg.xml")  # Path where the EPG file will be saved
gz_directory = os.path.join(REPO_DIR, "www")  # Directory where .gz files are located

# Step 6: Function to ensure directory and file permissions
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

# Step 7: Set up Logging
class SuccessFilter(logging.Filter):
    def filter(self, record):
        return "EPG file successfully saved" in record.getMessage()

# Get the directory where the script is located (absolute path)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create the relative path for the log file
log_file_path = os.path.join(script_dir, 'log', 'merge_epg.log')

# Ensure the 'log' directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Now log the message using the relative path
import logging
log_format = "%(asctime)s - %(message)s"
date_format = "%b %d %Y %H:%M:%S"

logging.basicConfig(filename=log_file_path,
                    level=logging.INFO,
                    format=log_format,
                    datefmt=date_format)

# Set up logging
logger = logging.getLogger()

# Ensure the log directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Create file handler and set up formatter
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.addFilter(SuccessFilter())

# Add handler to the logger and set log level
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# Log starting message
logger.info("Starting EPG merge process...")

# Step 8: Function to fetch and merge EPG data
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


# Step 9: Merge EPG data into a single XML
merged_root = ET.Element("tv")
total_files = len(epg_urls)


# Step 10: Process each EPG URL
for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress


# Step 11: Extract XML from .gz files
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


# Step 12: Save the merged EPG file and log success
try:
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    
    # Log success message
    success_message = f"EPG file successfully saved to {save_path}"
    logging.info(success_message)  # Log to merge_epg.log
    print(success_message)  # Echo success to console
 
except Exception as e:
    # Log error if save fails
    error_message = f"Failed to save EPG file - Error: {e}"
    logging.error(error_message)
    print(error_message)