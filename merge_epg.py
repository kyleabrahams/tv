import requests
import xml.etree.ElementTree as ET
import logging
import os

# List of EPG sources to merge run it 
# python3 merge_epg.py
# sudo chown -R $(whoami):admin /opt/homebrew/var/log/nginx
# sudo chmod -R 755 /opt/homebrew/var/log/nginx
# brew services restart nginx

# List of EPG source URLs to merge
epg_urls = [
    "https://www.bevy.be/bevyfiles/canadapremium.xml", 
    "https://www.bevy.be/bevyfiles/canadapremium2.xml",
    "https://www.bevy.be/bevyfiles/canadapremium3.xml",
    "https://www.bevy.be/bevyfiles/canada.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium3.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium4.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium5.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium6.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium7.xml",
    "https://i.mjh.nz/SamsungTVPlus/all.xml",
    "https://i.mjh.nz/PlutoTV/ca.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdom.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium3.xml"
]

# Path to save the merged EPG file (Adjust this to a valid directory on your macOS)
save_path = os.path.expanduser("~/Desktop/epg.xml")  # Save in the Documents folder

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch and parse each EPG file
def fetch_epg_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        if response.content.strip():
            try:
                epg_tree = ET.ElementTree(ET.fromstring(response.content))
                return epg_tree
            except ET.ParseError as e:
                logging.error(f"XML parse error for {url}: {e}")
                return None
        else:
            logging.warning(f"No content fetched from {url}")
            return None
    else:
        logging.error(f"Error fetching {url}: {response.status_code}")
        return None

# Create root element for the merged EPG
merged_root = ET.Element("tv")

# Fetch and merge EPG data
seen_channels = set()
for url in epg_urls:
    logging.info(f"Fetching EPG data from {url}")
    epg_tree = fetch_epg_data(url)
    if epg_tree:
        for element in epg_tree.getroot():
            if element.tag == "channel" and element.attrib['id'] not in seen_channels:
                merged_root.append(element)
                seen_channels.add(element.attrib['id'])

# Save merged EPG to file
try:
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    logging.info(f"Merged EPG successfully saved to {save_path}")
except Exception as e:
    logging.error(f"Failed to save merged EPG - Error: {e}")
