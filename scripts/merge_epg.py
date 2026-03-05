#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
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

# merge_epg.py Mar 4 2026 901 p 
# python3 -m venv myenv
# source myenv/bin/activate
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/merge_epg.py

# === Configuration ===
CI_SAFE = os.getenv("GITHUB_ACTIONS") == "true"  # Detect if running in GitHub Actions
delay = 5
sleep_time = 1 if CI_SAFE else delay

# Base directory of the repo
REPO_DIR = os.path.abspath(os.path.dirname(__file__))

# EPG file paths (absolute)
FAST_EPG_FILE = os.path.join(REPO_DIR, "scripts", "_epg-end", "fast-epg-end.xml")
DUMMY_EPG_FILE = os.path.join(REPO_DIR, "scripts", "_epg-end", "dummy--epg---end.xml")
BUILD_FAST_EPG_SCRIPT = os.path.join(REPO_DIR, "build_fast_epg.py")
BUILD_DUMMY_EPG_SCRIPT = os.path.join(REPO_DIR, "build_dummy_epg.py")

# Python executable
venv_python = sys.executable

  


################# Step 1: Set up Logging
# Toggle logging on/off
LOGGING_ENABLED = True

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path for log file
log_file_path = os.path.join(script_dir, 'www', 'merge_epg.log')
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # Ensure directory exists

# -----------------------------
# Set up logger
# -----------------------------
logger = None
if LOGGING_ENABLED:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=4
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%b %d %Y %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# -----------------------------
# Unified log function
# -----------------------------
def log_message(level, message):
    """
    Logs a message to file (if enabled) and prints it to console with timestamp.
    Supports 'info', 'error', 'warning'.
    """
    timestamp = datetime.now().strftime("%b %d %Y %H:%M:%S")
    print(f"{timestamp} - {level.upper()} - {message}")

    if LOGGING_ENABLED and logger:
        level = level.lower()
        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)
        else:
            logger.warning(message)

# -----------------------------
# Example usage
# -----------------------------
log_message("info", "Starting EPG merge process...")  

 


########## Step 2: Function to run dummy_epg.py script
def run_npm_grab():
    # -------------------------
    # TOGGLE RUNNING PRE-SCRIPTS
    # -------------------------
    run_build_dummy_epg = True
    run_build_fast_epg = True  
    run_channels_custom = False
    run_channels_custom_date = False
    run_channels_test = False
    run_channels_test_copy = False

    # -------------------------
    # DIRECTORIES
    # -------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    epg_end_dir = os.path.join(script_dir, "_epg-end")
    os.makedirs(epg_end_dir, exist_ok=True)  # ensure output folder exists

    # -------------------------
    # PRE-SCRIPTS
    # -------------------------
    pre_scripts = [
        (run_build_dummy_epg, os.path.join(script_dir, "build_dummy_epg.py")),
        (run_build_fast_epg, os.path.join(script_dir, "build_fast_epg.py")),
    ]

    for toggle, script_path in pre_scripts:
        if toggle:
            if os.path.exists(script_path):
                print(f"▶️ Running {os.path.basename(script_path)}...")
                result = subprocess.run([sys.executable, script_path],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
            else:
                print(f"❌ {os.path.basename(script_path)} not found, skipping")
        else:
            print(f"🔴 Skipping {os.path.basename(script_path)} (toggle is False)")

    # -------------------------
    # TIMESTAMP
    # -------------------------
    current_datetime = datetime.now().strftime("%m-%d-%I-%M-%S %p")

    # -------------------------
    # NPM GRAB COMMANDS
    # -------------------------
    commands = []

    if run_channels_custom_date:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-custom-start.xml')}",
            f"--output={os.path.join(epg_end_dir, f'channels-custom-{current_datetime}.xml')}"
        ])

    if run_channels_custom:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-custom-start.xml')}",
            f"--output={os.path.join(epg_end_dir, 'channels-custom-end.xml')}"
        ])

    if run_channels_test:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-test-start.xml')}",
            f"--output={os.path.join(epg_end_dir, 'channels-test-end.xml')}"
        ])

    if run_channels_test_copy:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-test-start-copy.xml')}",
            f"--output={os.path.join(epg_end_dir, f'channels-test-copy-{current_datetime}.xml')}"
        ])

    # -------------------------
    # CLEAN OLD TIMESTAMPED FILES
    # -------------------------
    try:
        for file_name in os.listdir(epg_end_dir):
            file_path = os.path.join(epg_end_dir, file_name)
            if file_name.startswith("channels-") and file_name.endswith(".xml") and not file_name.endswith("-end.xml"):
                os.remove(file_path)
                print(f"🧹 Deleted old timestamped file: {file_path}")
    except Exception as e:
        print(f"❌ Error deleting old files: {e}")

    # -------------------------
    # RUN NPM COMMANDS
    # -------------------------
    for command in commands:
        command_str = " ".join(command)
        print(f"▶️ Running command: {command_str}")
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            # Output stdout
            for line in process.stdout.splitlines():
                print(f"STDOUT: {line}")

            # Output stderr
            for line in process.stderr.splitlines():
                print(f"STDERR: {line}")

            if process.returncode == 0:
                print(f"✅ Command executed successfully: {command_str}")
                # Optional: detect number of channels
                channel_count_pattern = r"found (\d+) channel\(s\)"
                for line in process.stdout.splitlines():
                    match = re.search(channel_count_pattern, line)
                    if match:
                        print(f"✅ {match.group(1)} channel(s) in output")
                        break
            else:
                print(f"⚠️ Command failed (continuing anyway): {command_str}, return code: {process.returncode}")

        except Exception as e:
            print(f"❌ Exception running command {command_str}: {e}")




########## Step 3: Merge EPG data
def merge_epg_data(epg_urls, epg_end_dir, save_path):
    """
    Merge multiple EPG XML files into a single XML and save it.
    """
    print("▶️ Merging EPG data...")
    merged_root = ET.Element("tv")
    total = len(epg_urls)

    for index, url in enumerate(epg_urls):
        tree = fetch_epg_data(url, index, total, folder_path=epg_end_dir)
        if tree:
            for el in tree.getroot():
                merged_root.append(el)

    reorder_channels(merged_root)
    ensure_permissions(save_path)

    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)

    success_message = f"✅ EPG file successfully saved to {save_path}"
    log_message("info", success_message)
    print(success_message)





################# Step 4: Check for XML files if no URLs are found
def load_local_xml_files(directory):
    """Look for XML files in the directory if no EPG URLs are found."""
    xml_files = []
    try:
        log_message("info", f"Scanning directory: {directory}")
        files_in_directory = os.listdir(directory)
        log_message("info", f"Files in directory: {files_in_directory}")
        
        for filename in files_in_directory:
            # Skip hidden macOS metadata files starting with ._
            if filename.endswith(".xml") and not filename.startswith("._"):
                file_path = os.path.join(directory, filename)
                log_message("info", f"🟢 Found XML file: {file_path}")
                xml_files.append(file_path)
        
        log_message("info", f"🔍 XML files found: {xml_files}")
        return xml_files
    
    except Exception as e:
        log_message("error", f"❌ Error loading XML files from {directory}: {e}")
        return []




########## Step 5: Path to save the merged EPG file
REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # Assuming the script is part of the repository
save_path = os.path.join(REPO_DIR, "www", "epg.xml")  # Path where the EPG file will be saved
# save_path = os.path.join(REPO_DIR, "www", "epg-test.xml")  # Path where the EPG file will be saved

# Define the directory for .gz files
gz_directory = os.path.join(REPO_DIR, "www")  # Directory where .gz files are located

# You can now process files within the gz_directory or save to save_path
print(f"⬇️ EPG file will be saved to: {save_path}")
print(f"⬇️ .gz files are located in: {gz_directory}")




########## Step 6: Function to ensure directory and file permissions
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




########## Step 7: Function to fetch and merge EPG data
# Function to pretty-print XML
def pretty_print_xml(xml_tree):
    xml_str = ET.tostring(xml_tree.getroot(), encoding="utf-8", xml_declaration=True)
    parsed_str = minidom.parseString(xml_str)
    return parsed_str.toprettyxml(indent="  ")




def fetch_epg_data(url, index, total, retries=3, delay=5, folder_path="scripts/_epg-end"):
    import os, gzip, io, xml.etree.ElementTree as ET, time
    import requests

    is_remote = url.startswith("http://") or url.startswith("https://")
    print(f"🔄Fetching {index + 1}/{total} - {url}")

    if is_remote:
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    if not response.content or not isinstance(response.content, (bytes, str)):
                        print(f"⚠️ Empty response from site: {url}")
                        return None

                    try:
                        # Handle .gz files
                        if url.endswith(".gz"):
                            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                                xml_content = gz.read()
                            return ET.ElementTree(ET.fromstring(xml_content))
                        else:
                            return ET.ElementTree(ET.fromstring(response.content))
                    except ET.ParseError as e:
                        print(f"⚠️ Invalid XML from site {url}: {e}")
                        return None
                else:
                    print(f"❌ HTTP error {response.status_code} from site {url}")
                    return None
            except requests.RequestException as e:
                print(f"⚠️ Attempt {attempt+1}/{retries} failed for site {url}: {e}")
                attempt += 1
                if attempt < retries:
                    time.sleep(delay)
        print(f"❌ Failed to fetch from site {url} after {retries} attempts.")
        return None

    else:
        # Local file path
        if not os.path.isabs(url):
            url = os.path.join(folder_path, url)

        if not os.path.exists(url):
            print(f"❌ Local file does not exist: {url}")
            return None

        try:
            if url.endswith(".gz"):
                with gzip.open(url, "rb") as f:
                    xml_content = f.read()
                if not xml_content:
                    print(f"⚠️ Empty local file: {url}")
                    return None
                return ET.ElementTree(ET.fromstring(xml_content))
            else:
                tree = ET.parse(url)
                if tree is None:
                    print(f"⚠️ Empty local file: {url}")
                    return None
                return tree
        except ET.ParseError as e:
            print(f"❌ Failed to parse local XML file {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error processing local file {url}: {e}")
            return None




################# Step 8: Function to reorder channels to the top of the XML
def reorder_channels(merged_root):
    # Extract all <channel> elements
    channels = [el for el in merged_root.findall('channel')]

    # Extract all <programme> elements
    programmes = [el for el in merged_root.findall('programme')]

    # Clear the current root (we'll rebuild it)
    merged_root.clear()

    # Append the channels first
    for channel in channels:
        # Remove any <icon> elements
        for icon in channel.findall("icon"):
            channel.remove(icon)
        merged_root.append(channel)

    # Then append the programmes
    for programme in programmes:
        merged_root.append(programme)


# Assuming merged_root is your root element containing XML data
merged_root = ET.Element("tv")

# Reorder channels to be at the top
reorder_channels(merged_root)

# Pretty print the merged and reordered XML
pretty_xml = pretty_print_xml(ET.ElementTree(merged_root))

# Assuming epg_urls contains your XML URLs (remote or local)
folder_path = "scripts/_epg-end"  # Update to your folder path




################# Step 9: Save the merged EPG file and log success
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
  

  

################# Step 10: __main__ block
if __name__ == "__main__":
    log_message("info", "Starting EPG merge process...")

    # ---- Step A: Ensure 'www' directory exists for logs and outputs ----
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # ---- Step B: Run pre-builds/npm ----
    run_npm_grab()

    # ---- Step C: Decide which local EPG XML files to merge ----
    epg_end_dir = os.path.join(script_dir, "_epg-end")
    epg_urls = load_local_xml_files(epg_end_dir)

    if not epg_urls:
        log_message("error", "❌ No local EPG XML files found in _epg-end")
        sys.exit(1)

    log_message("info", "EPG XML files to merge:")
    for f in epg_urls:
        log_message("info", f"  - {f}")

    # ---- Step D: Set save path and ensure permissions ----
    save_path = os.path.join(script_dir, "www", "epg.xml")
    ensure_permissions(save_path)

    # ---- Step E: Merge EPG data ----
    merge_epg_data(epg_urls, epg_end_dir, save_path)