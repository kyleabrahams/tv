import requests
import xml.etree.ElementTree as ET
import logging
from bs4 import BeautifulSoup  # Import BeautifulSoup for potential HTML parsing

# Set up logging
logging.basicConfig(level=logging.INFO)

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
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdom.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium3.xml"
]

# Path to save the merged EPG file
save_path = "epg.xml"  # Save in the current directory

# Function to fetch and parse each EPG file
def fetch_epg_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        logging.info(f"Fetched content from {url}: {response.content[:100]}... (Length: {len(response.content)})")  # Log first 100 characters

        # Check if the response is empty
        if not response.content.strip():
            logging.warning(f"Empty response from {url}, skipping this URL.")
            return None

        # Check content type
        if "xml" not in response.headers.get("Content-Type", ""):
            logging.warning(f"Response from {url} is not XML. Content-Type: {response.headers.get('Content-Type')}, skipping this URL.")
            return None

        # Attempt to parse the XML content
        try:
            return ET.ElementTree(ET.fromstring(response.content))
        except ET.ParseError as e:
            logging.error(f"Failed to parse EPG from {url} - Error: {e}")
            return None
    except requests.RequestException as e:
        logging.error(f"Failed to fetch EPG from {url} - Error: {e}")
        return None

# Create root element for the merged EPG
merged_root = ET.Element("tv")

# Fetch and merge EPG data
for url in epg_urls:
    epg_tree = fetch_epg_data(url)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    else:
        logging.info(f"Skipping URL: {url} due to previous errors.")

# Save merged EPG to file
try:
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    logging.info(f"Merged EPG successfully saved to {save_path}")
except Exception as e:
    logging.error(f"Failed to save merged EPG - Error: {e}")