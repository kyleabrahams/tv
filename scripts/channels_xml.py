import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time  # Import the time module for elapsed time calculation

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

# Dictionary of channel IDs and their respective names
channel_dict = {
    '404710': 'CP24',
    '404834': 'MSNBC',
    '405039': 'Global (CIII-DT-41) Toronto',
    '405080': 'OMNI Vancouver',
    '404674': 'CBC (CBLT) Toronto',
    '404805': 'CITY Toronto, ON HD',
    '404876': 'CTV (CFTO) Toronto',
    '404781': 'Bravo',
    '404814': 'CHCH Hamilton',
    '405197': 'FX',
    '12783': 'CTV Two London/CFPL (CTV2L)',
    '404741': 'The Weather Network',
    '404709': 'YTV (Youth Television) - East',
    '404780': 'Discovery Velocity/CTV Speed',
    '403831': 'Motor Trend HD',
    '405090': 'Much Music',
    '404739': 'A and E Canada',
    '404729': 'AMC - Canada',
    '404985': 'CNN HD',
    '405157': 'TLC Canada HD',
    '404724': 'Investigation Discovery Canada',
    '404941': 'CTV Life HD',
    '405104': 'CMT Canada',
    '405182': 'Showcase Canada HD',
    '405149': 'CTV Drama HD',
    '405154': 'Slice HD',
    '405015': 'Discovery Channel (CAN) HD',
    '404990': 'History Canada HD East',
    '405023': 'History 2 Canada',
    '405094': 'CTV Comedy - East HD',
    '404884': 'HGTV Canada HD',
    '404989': 'Love Nature',
    '404787': 'Turner Classic Movies Canada HD',
    '405130': 'Discovery Science Canada',
    '404756': 'CTV Sci-Fi HD',
    '405033': 'Family Channel Canada - East HD',
    '405042': 'MTV Canada',
    '404958': 'DTOUR',
    '404904': 'Food Network Canada HD',
    '404661': 'Yes TV (CITS) Burlington, ON HD',
    '404864': 'ABC Spark HD',
    '404789': 'Cooking Channel Canada HD',
    '404713': 'Vision TV Eastern',
    '405151': 'E! Canada HD',
    '404905': 'FXX Canada HD',
    '404898': 'Cartoon Network Canada - East HD',
    '404993': 'Treehouse HD',
    '404815': 'WildBrainTV HD',
    '12901': 'Peachtree TV HDTV (WPCHD)',
    '404778': 'National Geographic Wild Canada',
    '404734': 'Family Jr. HD',
    '404648': 'Nickelodeon Canada HD',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',
    '40': 'DTOUR',

    '404911': 'Makeful'
}

# Record the start time
start_time = time.time()

# Fetch EPG data for all channels and create the combined XML
fetch_multiple_channels_data(channel_dict)

# Calculate the elapsed time
elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
