import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import json  # Import the json module to read from a JSON file

# Load the channels from the JSON file
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
    # Get the current date in YYYYMMDD format
    current_date = datetime.now().strftime("%Y%m%d")
    
    # Create the root <tv> element for the XML
    tv_root = ET.Element("tv")
    
    # String to hold the formatted channel data
    channels_str = ""
    
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
    with open("channels_xml.xml", "w", encoding="utf-8") as f:
        f.write(tv_str)
    
    print("Combined EPG data saved to channels_xml.xml")

# Load the channel dictionary from the JSON file
channel_dict = load_channels_from_file('channels.json')

# Record the start time
start_time = time.time()

# Fetch EPG data for all channels and create the combined XML
fetch_multiple_channels_data(channel_dict)

# Calculate the elapsed time
elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
