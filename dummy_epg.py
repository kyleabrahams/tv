import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from xml.dom import minidom
import os  # Import the os module
import pytz  # Import the pytz library


# Run script
# chmod +x dummy_epg.sh
# python3 dummy_epg.py

# Step 1: Function to create the EPG XML
def create_epg_xml(num_days=1, programs_per_day=5):
    # Step 1.1: Create the root element with attributes
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")
    
    # Step 1.2: Define channels
    channels = {
        "CITYNEWS247": "City News 24/7",
        "2": "Channel 2",
        "3": "Channel 3"
    }
    
    # Step 1.3: Create channel elements with display-name
    for channel_id, channel_name in channels.items():
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name

    # Step 1.4: Set the starting time for programs in UTC
    utc_now = datetime.utcnow()  # Use UTC time for starting point
    eastern = pytz.timezone('US/Eastern')  # Define the Eastern Time zone
    start_time = eastern.localize(utc_now).astimezone(eastern)  # Convert UTC to Eastern Time
    
    # Step 1.5: Loop through each day
    for day in range(num_days):
        # Step 1.6: Loop through each program of the day, including 5 hours before the first program
        for program in range(programs_per_day + 5):  # Create 5 extra programs
            # Step 1.7: Calculate the intended start time
            intended_start = start_time + timedelta(hours=program + day * programs_per_day - 5)  # Shifted back 5 hours

            # Step 1.8: Round the start time to the nearest hour
            rounded_start = intended_start.replace(minute=0, second=0, microsecond=0)
            if intended_start.minute >= 30:
                rounded_start += timedelta(hours=1)

            # Step 1.9: Calculate the end time based on the rounded start time
            end = rounded_start + timedelta(hours=1)  # Each program lasts 1 hour

            # Step 1.10: Format the start time for the title
            current_time = rounded_start.strftime("%I:%M %p")  # 12-hour format with AM/PM
            
            # Step 1.11: Create the programme element with start and stop attributes
            programme_elem = ET.SubElement(tv, "programme", 
                                            start=rounded_start.strftime("%Y%m%d%H%M%S -0500"),  # Adjust for EST (UTC-5)
                                            stop=end.strftime("%Y%m%d%H%M%S -0500"),
                                            channel="CITYNEWS247")  # Channel ID

            # Step 1.12: Add title element with lang attribute
            title_elem = ET.SubElement(programme_elem, "title", lang="en")

            # Step 1.13: Set the title text to include the hour in the desired format
            hour = rounded_start.strftime("%I").lstrip('0')  # Get the hour in 12-hour format, remove leading zero
            title_elem.text = f"City News 24/7 at {hour}"  # Format the title
            
            # Step 1.14: Add description element for the program
            description_elem = ET.SubElement(programme_elem, "description")
            # Step 1.15: Set the description text
            description_elem.text = f"Show Description {program + 1 + day * programs_per_day}"

    # Step 1.16: Convert the XML tree to a string and return it
    return ET.tostring(tv, encoding='unicode')

# Function for pretty printing the XML
def pretty_print(xml_string):
    xml_dom = minidom.parseString(xml_string)
    return xml_dom.toprettyxml(indent="  ").strip()  # Remove leading/trailing whitespace

# Generate EPG XML
def save_epg_to_file(num_days=1, programs_per_day=5):
    epg_xml = create_epg_xml(num_days=num_days, programs_per_day=programs_per_day)
    pretty_xml = pretty_print(epg_xml)

    # Define output directory and file name
    output_dir = "/usr/local/var/www"  # Change this to your desired directory
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    output_file_path = os.path.join(output_dir, "dummy.xml")

    # Save to the specified directory with XML declaration
    try:
        with open(output_file_path, "w") as xml_file:
            xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')  # Add XML declaration
            xml_file.write(pretty_xml.replace('<?xml version="1.0" ?>', ''))  # Remove extra declaration
        print(f"EPG data saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving EPG data: {e}")

# Run the function to generate and save the EPG XML
save_epg_to_file(num_days=3, programs_per_day=5)  # You can adjust num_days and programs_per_day as needed