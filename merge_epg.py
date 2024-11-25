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

# Relative path from the script to the virtual environment
venv_python = sys.executable
print(venv_python)

# Get the directory of the current script of dummy_epg.py
script_dir = os.path.dirname(os.path.realpath(__file__))
# Construct the relative path
dummy_epg_path = os.path.join(script_dir, "dummy_epg.py")
print(dummy_epg_path)  # To verify the constructed path

# Function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # This connects to a remote server, but doesn't actually establish a connection
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Fallback to localhost if unable to get the IP
    finally:
        s.close()
    return ip

local_ip = get_local_ip()

# Function to run dummy_epg.py script
def run_dummy_epg():
    try:
        # Use the virtual environment's Python interpreter
        result = subprocess.run([venv_python, dummy_epg_path], check=True, capture_output=True, text=True)
        print("dummy_epg.py executed successfully")
        print(result.stdout)  # Output from dummy_epg.py
    except subprocess.CalledProcessError as e:
        print(f"Error while running dummy_epg.py: {e}")
        print(e.stderr)

# Main merge_epg function
def merge_epg_data():
    # Run dummy_epg.py first
    run_dummy_epg()

    # Proceed with your merge EPG logic...
    print("Merging EPG data...")
    # Your existing code for merging EPG data goes here...
    
# Run the entire process
merge_epg_data()

# Step 1.1: Define the npm command and arguments (requires npm install)
command = ["npm", "run", "grab", "--", "--site=xumo.tv"]

try:
    # Run the command and stream its output in real-time
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Read and display progress from stdout
    for line in process.stdout:
        print(f"Progress: {line.strip()}")  # Echo progress

    # Wait for the process to finish
    process.wait()

    if process.returncode == 0:
        print("Command completed successfully.")
        print("success")
    else:
        print("Command failed.")
        print("Error:", process.stderr.read())

except Exception as e:
    print(f"An error occurred: {e}")


# Step 2: List of EPG source URLs to merge
epg_urls = [
    "dummy.xml",  # Local file to merge
    "xumo.xml",   
    # "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/SamsungTVPlus/us.xml",
    # "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/SamsungTVPlus/ca.xml",
    "https://github.com/matthuisman/i.mjh.nz/raw/master/SamsungTVPlus/all.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz",
    "https://www.bevy.be/bevyfiles/canada.xml",
    "https://www.bevy.be/bevyfiles/canadapremium.xml",
    "https://www.bevy.be/bevyfiles/canadapremium2.xml",
    "https://www.bevy.be/bevyfiles/canadapremium3.xml",
    # "https://i.mjh.nz/SamsungTVPlus/ca.xml",
    # "https://i.mjh.nz/SamsungTVPlus/us.xml",
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://i.mjh.nz/Stirr/all.xml",
    "https://i.mjh.nz/PBS/all.xml",
    "https://www.bevy.be/bevyfiles/unitedstates1.xml",
    "https://www.bevy.be/bevyfiles/unitedstates2.xml",
    "https://www.bevy.be/bevyfiles/unitedstates3.xml",
    "https://www.bevy.be/bevyfiles/unitedstates4.xml",
    "https://www.bevy.be/bevyfiles/unitedstates5.xml",
    "https://www.bevy.be/bevyfiles/unitedstates6.xml",
    "https://www.bevy.be/bevyfiles/unitedstates7.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdom.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium3.xml"
]

# Step 3: Path to save the merged EPG file
save_path = "/usr/local/var/www/epg.xml"  # Path to be served by Nginx
gz_directory = "/usr/local/var/www/"  # Change this to your .gz files directory


# Step 4: Set up logging with relative path
log_dir = os.path.join(script_dir, "log")  # Construct the relative log directory path
log_file = os.path.join(log_dir, "merge_epg.log")  # Construct the relative log file path

# Ensure the log directory exists, create it if it doesn't
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

class SuccessFilter(logging.Filter):
    def filter(self, record):
        return "EPG file successfully saved" in record.getMessage()

logger = logging.getLogger()
file_handler = logging.FileHandler(log_file)  # Use the relative log file path
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.addFilter(SuccessFilter())
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

logger.info("Starting EPG merge process...")

# Step 5: Function to fetch and merge EPG data
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

    logging.error(f"Failed to fetch {url} after {retries} attempts.")
    print(f"Failed to fetch {url} after {retries} attempts.")
    return None

# Fetch and merge all EPG data
merged_root = None

for i, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, i, len(epg_urls))
    if epg_tree is not None:
        if merged_root is None:
            merged_root = epg_tree.getroot()
        else:
            merged_root.extend(epg_tree.getroot())  # Merge EPG data

if merged_root is not None:
    try:
        # Step 6: Save the merged XML as a .gz file
        save_file_path = os.path.join(gz_directory, "epg.xml.gz")  # Saving to the directory
        with gzip.open(save_file_path, 'wb') as f:
            merged_tree = ET.ElementTree(merged_root)
            merged_tree.write(f)
        logger.info(f"EPG file successfully saved to {save_file_path}")
        print(f"EPG file successfully saved to {save_file_path}")
    except Exception as e:
        logger.error(f"Error saving merged EPG file: {e}")
        print(f"Error saving merged EPG file: {e}")
else:
    print("No EPG data to merge.")