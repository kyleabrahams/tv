import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from xml.dom import minidom
import os  # Import the os module
import subprocess
import sys
import pytz  # Import the pytz library


# Run script
# chmod +x dummy_epg.sh
# python3 dummy_epg.py

# Step 1: Function to install packages
# This function installs the required Python packages using pip
def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Step 2: Check if `pytz` is installed, otherwise install it
try:
    import pytz
except ImportError:
    print("pytz not found. Installing...")
    try:
        install_package("pytz")  # Attempt to install `pytz`
        import pytz  # Import again after installation
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pytz: {e}")
        sys.exit(1)  # Exit if installation fails

# Step 3: Print a message indicating pytz is ready to use
print("pytz is installed and ready to use.")

# Step 4: Function to create the EPG (Electronic Program Guide) XML
def create_epg_xml(num_days=1, programs_per_day=5):
    # Step 4.1: Create the root XML element for TV guide
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")
    
    # Step 4.2: Define a dictionary for channel IDs and their names
    channels = {
        "CITYNEWS247": "City News 24/7",
        "2": "Channel 2",
        "3": "Channel 3"
    }
    
    # Step 4.3: Loop through the channels and create XML elements for each
    for channel_id, channel_name in channels.items():
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name

    # Step 4.4: Set the starting time for programs in UTC, then convert to Eastern Time
    utc_now = datetime.utcnow()  # Use UTC time as the starting point
    eastern = pytz.timezone('US/Eastern')  # Define the Eastern Time zone
    start_time = eastern.localize(utc_now)  # Convert UTC to Eastern Time

    # Step 4.5: Loop through each day in the schedule
    for day in range(num_days):
        # Step 4.6: Loop through each program of the day, including 5 extra programs before the first one
        for program in range(programs_per_day + 5):  # Create 5 extra programs
            # Step 4.7: Calculate the intended start time for each program
            intended_start = start_time + timedelta(hours=program + day * programs_per_day - 5)

            # Step 4.8: Round the start time to the nearest hour
            rounded_start = intended_start.replace(minute=0, second=0, microsecond=0)
            if intended_start.minute >= 30:
                rounded_start += timedelta(hours=1)

            # Step 4.9: Calculate the end time for each program (1 hour duration)
            end = rounded_start + timedelta(hours=1)

            # Step 4.10: Format the start time for the program title
            current_time = rounded_start.strftime("%I:%M %p")  # 12-hour format with AM/PM
            
            # Step 4.11: Create the "programme" XML element for each program
            programme_elem = ET.SubElement(tv, "programme", 
                                            start=rounded_start.strftime("%Y%m%d%H%M%S -0500"),
                                            stop=end.strftime("%Y%m%d%H%M%S -0500"),
                                            channel="CITYNEWS247")  # Use channel ID

            # Step 4.12: Add the title element for the program
            title_elem = ET.SubElement(programme_elem, "title", lang="en")
            hour = rounded_start.strftime("%I").lstrip('0')  # Get the hour in 12-hour format, remove leading zero
            title_elem.text = f"City News 24/7 at {hour}"  # Format the title
            
            # Step 4.13: Add a description element for the program
            description_elem = ET.SubElement(programme_elem, "description")
            description_elem.text = f"Show Description {program + 1 + day * programs_per_day}"

    # Step 4.14: Return the generated XML as a string
    return ET.tostring(tv, encoding='unicode')

# Step 5: Function for pretty printing the XML (to make it more readable)
def pretty_print(xml_string):
    xml_dom = minidom.parseString(xml_string)
    return xml_dom.toprettyxml(indent="  ").strip()  # Remove leading/trailing whitespace

# Step 6: Function to save the generated EPG XML to a file
def save_epg_to_file(num_days=3, programs_per_day=5):
    # Step 6.1: Generate the EPG XML string using the `create_epg_xml` function
    epg_xml = create_epg_xml(num_days=num_days, programs_per_day=programs_per_day)
    
    # Step 6.2: Pretty print the XML to make it more human-readable
    pretty_xml = pretty_print(epg_xml)

    # Step 6.3: Define the output directory and file name for the XML file
    output_dir = "/Users/kyleabrahams/Documents/GitHub/tv"  # Change this path as needed
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    
    output_file_path = os.path.join(output_dir, "dummy.xml")

    # Step 6.4: Try to save the XML to the file
    try:
        with open(output_file_path, "w") as xml_file:
            xml_file.write(pretty_xml)  # Write the pretty XML to the file
        print(f"EPG data saved to {output_file_path}")  # Print success message
        return output_file_path  # Return the file path for confirmation
    except Exception as e:
        print(f"Error saving EPG data: {e}")  # Print error message
        sys.exit(1)  # Exit if there's an error

# Step 7: Run the function to generate and save the EPG XML
save_epg_to_file(num_days=3, programs_per_day=5)  # You can adjust num_days and programs_per_day as needed