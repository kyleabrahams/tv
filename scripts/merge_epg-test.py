#!/usr/bin/env python3

# merge_epg.py Feb 19 2025 200p
import requests
import xml.etree.ElementTree as ET
import os
import gzip
import io
import subprocess
from time import sleep
import sys
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
import re
import pytz

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg-test.py

# Define REPO_DIR at the top of merge_epg.py if it's not already defined
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # This will set REPO_DIR to the script's directory
venv_python = sys.executable  # Relative path from the script to the virtual environment
print(venv_python)
print("Starting data processing...")
# your data processing code
print("Data processing complete.")

################# Step 1: Set up Logging
# Toggle logging on/off
LOGGING_ENABLED = False

# Get the script directory (absolute path)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create the relative path for the log file
log_file_path = os.path.join(script_dir, 'www', 'merge_epg.log')

# Ensure the 'www' directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Set up logging only if LOGGING_ENABLED is True
if LOGGING_ENABLED:
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%b %d %Y %H:%M:%S"

    logging.basicConfig(filename=log_file_path,
                        level=logging.INFO,
                        format=log_format,
                        datefmt=date_format)

    logger = logging.getLogger(__name__)

    # Create a RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=4  # 5 MB file size limit, keep 4 backups
    )

    # Set up the formatter
    formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(formatter)

    # Define SuccessFilter to filter messages
    class SuccessFilter(logging.Filter):
        def filter(self, record):
            return "EPG file successfully saved" in record.getMessage()

    # Add the filter
    file_handler.addFilter(SuccessFilter())

    # Add the file handler to the logger
    logger.addHandler(file_handler)
else:
    logger = None  # Disable logging

# Function to log messages (only logs if logging is enabled)
def log_message(level, message):
    if LOGGING_ENABLED and logger:
        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)

# Print formatted time for debugging
formatted_time = datetime.now().strftime("%b %d %Y %H:%M:%S")
print(formatted_time)

# Example log usage
log_message("info", "Starting EPG merge process...")

########## Step 2.1: Function to run dummy_epg.py script
def run_npm_grab():
    # Define the toggles as True/False
    toggle_channels_custom = False
    toggle_channels_test = True
    toggle_channels_test_copy = False

    # Get current date and time for timestamping the output file
    current_datetime = datetime.now().strftime("%m-%d-%I-%M-%S %p")

    # List of npm commands with timestamped output file, toggled based on True/False values
    commands = []

    if toggle_channels_custom:
        commands.append([
            "npm", "run", "grab", "--", 
            f"--channels=./scripts/_epg-start/channels-custom-start.xml", 
            f"--output=./scripts/_epg-end/channels-custom-{current_datetime}.xml"
        ])

    if toggle_channels_test:
        commands.append([
            "npm", "run", "grab", "--", 
            f"--channels=./scripts/_epg-start/channels-test-start.xml", 
            f"--output=./scripts/_epg-end/channels-test-end.xml"
        ])

    if toggle_channels_test_copy:
        commands.append([
            "npm", "run", "grab", "--", 
            f"--channels=./scripts/_epg-start/channels-test-start-copy.xml", 
            f"--output=./scripts/_epg-end/channels-test-copy-{current_datetime}.xml"
        ])

    # Set the output directory for deleting old files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "_epg-end")

    # Delete all older files except the latest one
    try:
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)

            # Check if the file matches the pattern 'channels-YYYY-MM-DD-HH-MM-SS.xml' and is not the latest file
            if file_name.startswith("channels-") and file_name != f"channels-{current_datetime}.xml":
                os.remove(file_path)
                if logger:
                    logger.info(f"Old file {file_path} deleted.")
                print(f"Old file {file_path} deleted.")
    except Exception as e:
        if logger:
            logger.error(f"❌ Error deleting old files: {e}")
        print(f"❌ Error deleting old files: {e}")

    for command in commands:
        try:
            # Combine the command into a string for logging and display
            command_str = ' '.join(command)
            if logger:
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
                if logger:
                    logger.info(f"STDOUT: {stripped_line}")
                print(f"STDOUT: {stripped_line}")

            # Process stderr and capture lines
            for line in process.stderr:
                stripped_line = line.strip()
                stderr_output.append(stripped_line)
                if logger:
                    logger.error(f"STDERR: {stripped_line}")
                print(f"STDERR: {stripped_line}")

            # Wait for process completion
            process.wait()

            # Check for successful execution
            if process.returncode == 0:
                if logger:
                    logger.info(f"Command {command_str} executed successfully.")
                print(f"Command {command_str} executed successfully.")

                # Extract and log the number of channels found
                channel_count_pattern = r"found (\d+) channel\(s\)"
                for line in stdout_output:
                    match = re.search(channel_count_pattern, line)
                    if match:
                        channel_count = match.group(1)
                        if logger:
                            logger.info(f"Found {channel_count} channel(s) in the output.")
                        print(f"Found {channel_count} channel(s) in the output.")
                        break  # Stop after the first match

            else:
                if logger:
                    logger.error(f"Command {command_str} failed with error code {process.returncode}.")
                print(f"Command {command_str} failed with error code {process.returncode}.")

        except Exception as e:
            if logger:
                logger.error(f"❌ Error while running npm command {command_str}: {e}")
            print(f"❌ Error while running npm command {command_str}: {e}")

# Run the process
if __name__ == "__main__":
    run_npm_grab()



########## Step 4: Main merge_epg function

# Main merge_epg function
def merge_epg_data():

    # Proceed with your merge EPG logic...
    print("Merging EPG data...")
    # Your existing code for merging EPG data goes here...
    
# Run the entire process
merge_epg_data()

# Execute the process
if __name__ == "__main__":
    pass  # This is already handled by the function call above


########## Step 5: Function to read the EPG URLs from a file
def load_epg_urls(file_path):
    """Read EPG URLs from the specified file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            epg_urls = [line.strip() for line in file.readlines() if line.strip()]  # Remove empty lines and strip whitespace
        return epg_urls
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []

########## Step 6: Check for XML files if no URLs are found

# Function to load EPG URLs (the actual implementation of this is not provided here, assuming it's defined elsewhere)
def load_epg_urls(epg_urls_file):
    """Load EPG URLs from the given file."""
    epg_urls = []
    try:
        with open(epg_urls_file, 'r') as file:
            epg_urls = file.readlines()
            epg_urls = [url.strip() for url in epg_urls]  # Clean up the URLs
    except Exception as e:
        print(f"❌ Error loading EPG URLs from {epg_urls_file}: {e}")
    return epg_urls

########## Step 6: Check for XML files if no URLs are found

def load_local_xml_files(directory):
    """Look for XML files in the directory if no EPG URLs are found."""
    xml_files = []
    try:
        print(f"Scanning directory: {directory}")  # Print the directory being scanned
        files_in_directory = os.listdir(directory)
        print(f"Files in directory: {files_in_directory}")  # List files in the directory
        for filename in files_in_directory:
            print(f"Checking file: {filename}")  # Print every file being checked
            if filename.endswith(".xml"):
                file_path = os.path.join(directory, filename)
                print(f"Found XML file: {file_path}")  # Print the full path of any found XML file
                xml_files.append(file_path)  # Add XML file path to the list
        print(f"XML files found: {xml_files}")  # Final list of found XML files
        return xml_files
    except Exception as e:
        print(f"❌ Error loading XML files from {directory}: {e}")
        return []

# Get the directory where the script is located (absolute path)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # Ensure the 'log' directory exists

# Relative path to the epg_urls.txt file
epg_urls_file = os.path.join(script_dir, '_epg-start', 'epg_urls.txt')

# Load EPG URLs using the relative path
epg_urls = load_epg_urls(epg_urls_file)

# Check if URLs are found, if not, look for XML files in the _epg-end directory
if not epg_urls:
    # Use a relative path to the _epg-end directory
    epg_end_dir = os.path.join(script_dir, '_epg-end')
    print(f"No EPG URLs found in {epg_urls_file}, scanning {epg_end_dir} for XML files...")
    epg_urls = load_local_xml_files(epg_end_dir)

# Print out the list of EPG URLs or local XML files found
if epg_urls:
    print("EPG URLs or local XML files found:")
    for url in epg_urls:
        print(f"  - {url}")
else:
    print("No EPG URLs or local XML files found.")

########## Step 7: Path to save the merged EPG file
REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # Assuming the script is part of the repository
save_path = os.path.join(REPO_DIR, "www", "epg-test.xml")  # Path where the EPG file will be saved

# Define the directory for .gz files
gz_directory = os.path.join(REPO_DIR, "www")  # Directory where .gz files are located

# You can now process files within the gz_directory or save to save_path
print(f"EPG file will be saved to: {save_path}")
print(f".gz files are located in: {gz_directory}")

########## Step 8: Function to ensure directory and file permissions
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


########## Step 9: Function to fetch and merge EPG data

from xml.dom import minidom

# Function to pretty-print XML
def pretty_print_xml(xml_tree):
    xml_str = ET.tostring(xml_tree.getroot(), encoding="utf-8", xml_declaration=True)
    parsed_str = minidom.parseString(xml_str)
    return parsed_str.toprettyxml(indent="  ")

def fetch_epg_data(url, index, total, retries=3, delay=5, folder_path="scripts/_epg-end"):
    # If URL is not absolute, combine it with folder_path (local path resolution)
    if not os.path.isabs(url):
        url = os.path.join(folder_path, url)

    logging.info(f"Fetching {index + 1}/{total} - {url}")
    print(f"Fetching {index + 1}/{total} - {url}")
    
    attempt = 0
    while attempt < retries:
        try:
            # Handling remote URLs
            if url.startswith('http'):
                response = requests.get(url, timeout=10)  # Timeout to avoid hanging
                if response.status_code == 200:
                    try:
                        # Handle .gz files (compressed XML)
                        if url.endswith('.gz'):
                            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                                xml_content = gz.read()
                            epg_tree = ET.ElementTree(ET.fromstring(xml_content))
                        else:
                            epg_tree = ET.ElementTree(ET.fromstring(response.content))
                        
                        print(f"✅ Successfully fetched {index + 1}/{total}")
                        logging.info(f"✅ Successfully fetched {index + 1}/{total}")
                        return epg_tree
                    except ET.ParseError as e:
                        logging.error(f"XML parse error for {url}: {e}")
                        print(f"XML parse error for {url}: {e}")
                        return None
                    except Exception as e:
                        logging.error(f"❌ Error processing {url}: {e}")
                        print(f"❌ Error processing {url}: {e}")
                        return None
                else:
                    logging.error(f"❌ Error fetching {url}: HTTP {response.status_code}")
                    print(f"❌ Error fetching {url}: HTTP {response.status_code}")
                    return None

            # Handling local XML files
            else:
                try:
                    # Ensure the file exists before attempting to parse
                    if os.path.exists(url):
                        epg_tree = ET.parse(url)
                        print(f"✅ Successfully loaded local file: {url}")
                        logging.info(f"✅ Successfully loaded local file: {url}")
                        return epg_tree
                    else:
                        logging.error(f"Local file does not exist: {url}")
                        print(f"Local file does not exist: {url}")
                        return None
                except ET.ParseError as e:
                    logging.error(f"❌ Failed to parse local XML file {url}: {e}")
                    print(f"❌ Failed to parse local XML file {url}: {e}")
                except Exception as e:
                    logging.error(f"❌ Error processing local file {url}: {e}")
                    print(f"❌ Error processing local file {url}: {e}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            attempt += 1
            time.sleep(delay)  # Wait before retrying
    return None  # Return None after all attempts fail

# EPG URLs and local file names in the _epg-end folder should be known and valid
epg_urls = [
    "dummy--epg---end.xml",  # Local file in the _epg-end folder
    "channels-test-end.xml",
    "channels-custom-end.xml"
]

folder_path = "/Users/kyleabrahams/Documents/GitHub/tv/scripts/_epg-end"
for idx, url in enumerate(epg_urls):
    fetch_epg_data(url, idx, len(epg_urls), folder_path=folder_path)



import xml.etree.ElementTree as ET
from xml.dom import minidom

# Function to reorder channels to the top of the XML
def reorder_channels(merged_root):
    # Extract all <channel> elements
    channels = [el for el in merged_root.findall('channel')]

    # Extract all <programme> elements
    programmes = [el for el in merged_root.findall('programme')]

    # Clear the current root (we'll rebuild it)
    merged_root.clear()

    # Append the channels first
    for channel in channels:
        merged_root.append(channel)

    # Then append the programmes
    for programme in programmes:
        merged_root.append(programme)

# Function to pretty-print XML with custom formatting
def pretty_print_xml(xml_tree):
    # Convert the tree to a string with xml_declaration and UTF-8 encoding
    xml_str = ET.tostring(xml_tree.getroot(), encoding="utf-8", xml_declaration=True)
    
    # Parse the string into a minidom object for pretty printing
    parsed_str = minidom.parseString(xml_str)
    
    # Return the pretty-printed XML string with proper indentation
    return parsed_str.toprettyxml(indent="  ")

# Example usage:

# Assuming merged_root is your root element containing XML data
merged_root = ET.Element("tv")

# Assuming you have added <channel> and <programme> elements to merged_root

# Reorder channels to be at the top
reorder_channels(merged_root)

# Pretty print the merged and reordered XML
pretty_xml = pretty_print_xml(ET.ElementTree(merged_root))



# Assuming epg_urls contains your XML URLs (remote or local)
epg_urls = ["dummy--epg---end.xml", "channels-test-end.xml", "channels-custom-end.xml"]
folder_path = "scripts/_epg-end"  # Update to your folder path

# Fetch and merge EPG data
total_files = len(epg_urls)
for idx, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, idx, total_files, folder_path=folder_path)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)

# Reorder the channels to appear first
reorder_channels(merged_root)

# Pretty print the merged and reordered XML
pretty_xml = pretty_print_xml(ET.ElementTree(merged_root))

# Save the final formatted XML file
with open(save_path, "w", encoding="utf-8") as f:
    f.write(pretty_xml)

success_message = f"✅ EPG file successfully saved to {save_path}"
logging.info(success_message)
print(success_message)



########## Step 10: Extract XML from .gz files

def extract_gz_files(gz_directory):
    """Extract .gz files in the specified directory."""
    # Make sure you're using the correct directory
    gz_directory = os.path.join(REPO_DIR, "www")  # Ensure this points to the right directory

    if not os.path.exists(gz_directory):
        print(f"❌ Error: Directory {gz_directory} does not exist.")
        return []

    extracted_files = []
    for filename in os.listdir(gz_directory):
        if filename.endswith(".gz"):
            file_path = os.path.join(gz_directory, filename)
            print(f"Extracting {file_path}...")
            # Your extraction code here
            extracted_files.append(file_path)
    return extracted_files


########## Step 11: Merge EPG data into a single XML

merged_root = ET.Element("tv")
total_files = len(epg_urls)

# ########## Step 12: Process each EPG URL
for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress


########## Step 13: Extract XML from .gz files

print("Extracting XML from .gz files...")
extracted_files = extract_gz_files(gz_directory)
for xml_file in extracted_files:
    try:
        epg_tree = ET.parse(xml_file)
        for element in epg_tree.getroot():
            merged_root.append(element)
    except ET.ParseError as e:
        logging.error(f"❌ Failed to parse extracted XML file {xml_file}: {e}")
        print(f"❌ Failed to parse extracted XML file {xml_file}: {e}")


########## Step 14: Save the merged EPG file and log success

try:
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    
    # Log success message
    success_message = f"✅ EPG file successfully saved to {save_path}"
    logging.info(success_message)  # Log to merge_epg.log
    print(success_message)  # Echo success to console

except Exception as e:
    # Log error if save fails
    error_message = f"❌ Failed to save EPG file - Error: {e}"
    logging.error(error_message)
    print(error_message)

