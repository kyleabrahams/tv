import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
import os

# Define the function to create the EPG XML
def create_xumo_epg(num_days=1, programs_per_day=5):
    # Step 1: Create the root element with attributes
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")
    
    # Step 2: Define channels (you can extend this with actual Xumo channels)
    channels = {
        "CITYNEWS247": "City News 24/7",
        "NBCNEWSNOW": "NBC News NOW",
        "WEATHERCHANNEL": "The Weather Channel",
        "FOXSPORTS": "Fox Sports",
    }
    
    # Step 3: Create channel elements with display-name
    for channel_id, channel_name in channels.items():
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name
    
    # Step 4: Set the starting time for programs in Eastern Time (adjust to your needs)
    utc_now = datetime.utcnow()  # Use UTC time for starting point
    eastern = pytz.timezone('US/Eastern')  # Define the Eastern Time zone
    start_time = eastern.localize(utc_now).astimezone(eastern)  # Convert UTC to Eastern Time
    
    # Step 5: Loop through each day
    for day in range(num_days):
        # Step 6: Loop through each program of the day
        for program in range(programs_per_day):
            # Step 7: Calculate the intended start time
            intended_start = start_time + timedelta(hours=program + day * programs_per_day)

            # Step 8: Round the start time to the nearest hour
            rounded_start = intended_start.replace(minute=0, second=0, microsecond=0)
            if intended_start.minute >= 30:
                rounded_start += timedelta(hours=1)

            # Step 9: Calculate the end time based on the rounded start time
            end = rounded_start + timedelta(hours=1)  # Each program lasts 1 hour

            # Step 10: Format the start time for the title (e.g., 11:00 PM)
            current_time = rounded_start.strftime("%I:%M %p")  # 12-hour format with AM/PM

            # Step 11: Create the programme element with start and stop attributes
            programme_elem = ET.SubElement(tv, "programme", 
                                            start=rounded_start.strftime("%Y%m%d%H%M%S -0500"),  # Adjust for EST (UTC-5)
                                            stop=end.strftime("%Y%m%d%H%M%S -0500"),
                                            channel="CITYNEWS247")  # Channel ID
            
            # Step 12: Add title element with lang attribute
            title_elem = ET.SubElement(programme_elem, "title", lang="en")
            
            # Step 13: Set the title text to include the hour in the desired format
            hour = rounded_start.strftime("%I").lstrip('0')  # Get the hour in 12-hour format, remove leading zero
            title_elem.text = f"City News 24/7 at {hour}"  # Format the title
            
            # Step 14: Add description element for the program
            description_elem = ET.SubElement(programme_elem, "description")
            description_elem.text = f"Show Description {program + 1 + day * programs_per_day}"

    # Step 15: Convert the XML tree to a string and return it
    return ET.tostring(tv, encoding='unicode')

# Function to pretty print the XML
def pretty_print(xml_string):
    from xml.dom import minidom
    xml_dom = minidom.parseString(xml_string)
    return xml_dom.toprettyxml(indent="  ").strip()  # Remove leading/trailing whitespace

# Generate EPG XML
epg_xml = create_xumo_epg(num_days=1, programs_per_day=5)  # Set num_days to 1 for a single day
pretty_xml = pretty_print(epg_xml)

# Define output directory and file name
output_dir = "/usr/local/var/www"  # Change this to your desired directory
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
output_file_path = os.path.join(output_dir, "xumo_epg.xml")

# Save the XML to the specified directory with XML declaration
try:
    with open(output_file_path, "w") as xml_file:
        xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')  # Add XML declaration
        xml_file.write(pretty_xml.replace('<?xml version="1.0" ?>', ''))  # Remove extra declaration
    print(f"EPG data saved to {output_file_path}")
except Exception as e:
    print(f"Error saving EPG data: {e}")
