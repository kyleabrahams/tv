import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from xml.dom import minidom
import os  # Import the os module


# Run script
# chmod +x dummy_epg.sh
# ./dummy_epg.sh

# Step 1: Function to create the EPG XML
def create_epg_xml(num_days=1, programs_per_day=5):
    # Step 1.1: Create the root element with attributes
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")
    
    # Step 1.2: Define channels
    channels = {
        "CITYNEWS247": "City New 24/7",
        "2": "Channel 2",
        "3": "Channel 3"
    }
    
 # Step 1.3: Create channel elements with display-name
    for channel_id, channel_name in channels.items():
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name

    # Step 1.4: Create programme elements
    start_time = datetime.utcnow()  # Use UTC time for start times
    for day in range(num_days):
        for program in range(programs_per_day):
            # Step 1.5: Increment the start time by 1 hour for each program
            start = start_time + timedelta(hours=program + day * programs_per_day)
            end = start + timedelta(hours=1)  # Each program lasts 1 hour
            
            # Step 1.6: Create the programme element with attributes
            programme_elem = ET.SubElement(tv, "programme", 
                                            start=start.strftime("%Y%m%d%H%M%S +0000"), 
                                            stop=end.strftime("%Y%m%d%H%M%S +0000"),
                                            channel="CITYNEWS247")  # Change channel as needed
            
            # Step 1.7: Add title element with lang attribute
            title_elem = ET.SubElement(programme_elem, "title", lang="en")
            title_elem.text = f"Show Title {program + 1 + day * programs_per_day}"
            
            # Step 1.8: Add description element
            description_elem = ET.SubElement(programme_elem, "description")
            description_elem.text = f"Show Description {program + 1 + day * programs_per_day}"

    # Step 1.9: Convert the XML tree to a string and return it
    return ET.tostring(tv, encoding='unicode')

# Step 2: Function to pretty print the XML
def pretty_print(xml_string):
    # Step 2.1: Format the XML string for pretty printing
    xml_dom = minidom.parseString(xml_string)
    return xml_dom.toprettyxml(indent="  ").strip()  # Remove leading/trailing whitespace

# Step 3: Generate EPG XML
epg_xml = create_epg_xml(num_days=3, programs_per_day=5)
pretty_xml = pretty_print(epg_xml)

# Step 4: Define output directory and file name
output_dir = "/usr/local/var/www"  # Change this to your desired directory
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
output_file_path = os.path.join(output_dir, "dummy.xml")

# Step 5: Save to the specified directory with XML declaration
try:
    with open(output_file_path, "w") as xml_file:
        xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')  # Add XML declaration
        xml_file.write(pretty_xml.replace('<?xml version="1.0" ?>', ''))  # Remove extra declaration
    print(f"EPG data saved to {output_file_path}")
except Exception as e:
    print(f"Error saving EPG data: {e}")