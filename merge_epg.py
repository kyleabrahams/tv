import requests
import xml.etree.ElementTree as ET
import logging
import os
import gzip
import io
import subprocess  # Add this import to resolve the error
from time import sleep
import sys # Used for venv_python


# See Android TV sheets doc, nginx tab for commands,
# sudo nginx -s reload
# python3 merge_epg.py

# Below used to grab xumo.tv (5.1 mb xml file) and other sites https://github.com/iptv-org/epg
# npm run grab -- --site=xumo.tv

# https://i.mjh.nz/
# http://10.0.0.30:8080/epg.xml

# Relative path from the script to the virtual environment
venv_python = sys.executable
print(venv_python)
import os

# Get the directory of the current script of dummy_epg.py
script_dir = os.path.dirname(os.path.realpath(__file__))
# Construct the relative path
dummy_epg_path = os.path.join(script_dir, "dummy_epg.py")
print(dummy_epg_path)  # To verify the constructed path

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
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the current script
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
    return None  # Return None after all attempts fail    

# Step 6: Function to extract XML from .gz files
def extract_gz_files(gz_directory):
    extracted_files = []
    for filename in os.listdir(gz_directory):
        if filename.endswith('.gz'):
            gz_file_path = os.path.join(gz_directory, filename)
            with gzip.open(gz_file_path, 'rb') as f:
                content = f.read()
                extracted_file = gz_file_path[:-3]  # Remove .gz extension
                with open(extracted_file, 'wb') as output_file:
                    output_file.write(content)
                extracted_files.append(extracted_file)
    return extracted_files


# Step 7: Merge EPG data into a single XML
merged_root = ET.Element("tv")
total_files = len(epg_urls)


# Step 8: Process each EPG URL
for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress


# Step 9: Extract XML from .gz files
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


# Step 10: Save the merged EPG file and log success
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
