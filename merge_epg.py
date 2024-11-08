import requests
import xml.etree.ElementTree as ET
import logging
import os
from time import sleep

# See Android TV sheets doc, nginx tab for commands,
# sudo nginx -s reload
# python3 merge_epg.py

# List of EPG source URLs to merge
epg_urls = [
    "https://www.bevy.be/bevyfiles/canadapremium.xml", 
    "https://www.bevy.be/bevyfiles/canadapremium2.xml",
    "https://www.bevy.be/bevyfiles/canadapremium3.xml",
    "https://www.bevy.be/bevyfiles/canada.xml",
    "https://i.mjh.nz/SamsungTVPlus/us.xml",
    "https://i.mjh.nz/SamsungTVPlus/ca.xml",
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://i.mjh.nz/Stirr/all.xml",
    "https://i.mjh.nz/PBS/all.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium3.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium4.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium5.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium6.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium7.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdom.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium3.xml"
]

# Path to save the merged EPG file
save_path = "/usr/local/var/www/epg.xml"  # Path to be served by Nginx

# Set up logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to the console
        logging.FileHandler('merge_epg.log')  # Logs to a file named merge_epg.log
    ]
)
# Function to fetch and merge EPG data
def fetch_epg_data(url, index, total):
    logging.info(f"Fetching {index + 1}/{total} - {url}")
    response = requests.get(url)
    if response.status_code == 200:
        try:
            epg_tree = ET.ElementTree(ET.fromstring(response.content))
            logging.info(f"Successfully fetched {index + 1}/{total}")
            return epg_tree
        except ET.ParseError as e:
            logging.error(f"XML parse error for {url}: {e}")
    else:
        logging.error(f"Error fetching {url}: {response.status_code}")
    return None

# Merge EPG data into a single XML
merged_root = ET.Element("tv")
total_files = len(epg_urls)

for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress

# Save the merged EPG file
try:
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    logging.info(f"EPG file successfully saved to {save_path}")
except Exception as e:
    logging.error(f"Failed to save EPG file - Error: {e}")