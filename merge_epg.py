import requests
import xml.etree.ElementTree as ET
import logging
import os
import gzip
import io
from time import sleep

# See Android TV sheets doc, nginx tab for commands,
# sudo nginx -s reload
# python3 merge_epg.py

# https://i.mjh.nz/
# http://10.0.0.30:8080/epg.xml

# List of EPG source URLs to merge
epg_urls = [
    "https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz",
    "https://www.bevy.be/bevyfiles/canada.xml",
    "https://www.bevy.be/bevyfiles/canadapremium.xml", 
    "https://www.bevy.be/bevyfiles/canadapremium2.xml",
    "https://www.bevy.be/bevyfiles/canadapremium3.xml",
    "https://raw.githubusercontent.com/kyleabrahams/tv/main/dummy.xml",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/SamsungTVPlus/us.xml",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/SamsungTVPlus/ca.xml",
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

# 2. Path to save the merged EPG file
save_path = "/usr/local/var/www/epg.xml"  # Path to be served by Nginx
gz_directory = "/usr/local/var/www/"  # Change this to your .gz files directory

# 3. Set up logging to only log errors (failures)
logging.basicConfig(
    level=logging.ERROR,  # Log only errors and above
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to the console
        logging.FileHandler('merge_epg.log')  # Logs to a file named merge_epg.log
    ]
)

# 4. Function to fetch and merge EPG data
def fetch_epg_data(url, index, total):
    logging.info(f"Fetching {index + 1}/{total} - {url}")
    print(f"Fetching {index + 1}/{total} - {url}")
    response = requests.get(url)
    if response.status_code == 200:
        try:
            if url.endswith('.gz'):
                # Extract the XML content from the gzipped file
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
        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
            print(f"Error processing {url}: {e}")
    else:
        logging.error(f"Error fetching {url}: {response.status_code}")
        print(f"Error fetching {url}: {response.status_code}")
    return None

# 5. Function to extract XML from .gz files
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

# 6. Merge EPG data into a single XML
merged_root = ET.Element("tv")
total_files = len(epg_urls)

# 7. Process each EPG URL
for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress

# 8. Extract XML from .gz files
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

# 9. Save the merged EPG file
try:
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    logging.info(f"EPG file successfully saved to {save_path}")
    print(f"EPG file successfully saved to {save_path}")  # Echo success to console
except Exception as e:
    logging.error(f"Failed to save EPG file - Error: {e}")
    print(f"Failed to save EPG file - Error: {e}")  # Echo error to console
