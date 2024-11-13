import xml.etree.ElementTree as ET  # For creating XML elements
from datetime import datetime, timedelta  # For date and time handling
from xml.dom import minidom  # For pretty-printing XML
import os  # For handling file operations
import subprocess  # For installing packages
import sys  # For system operations
import pytz  # For timezone handling
import re  # For regular expressions



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
    # Step 4.1: Create the root <tv> element with generator info attributes
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")

    # Step 4.2: Define a dictionary of channels with their IDs and display names
    channels = {
        "CITYNEWS247": "City News 24/7",
        "2": "Channel 2",
        "3": "Channel 3"
    }
    
    # Step 4.3: Loop through the channel dictionary and create <channel> elements in a single line
    for channel_id, channel_name in channels.items():
        # Step 4.3.1: Create <channel> element with the channel's ID in one line
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        # Step 4.3.2: Create <display-name> element inside <channel> for channel name
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name

    # Step 4.4: Get the current UTC time and convert to Eastern Time
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)  # Current time in UTC
    eastern = pytz.timezone('US/Eastern')  # Define Eastern Time zone
    start_time = utc_now.astimezone(eastern)  # Convert UTC to localized Eastern Time

    # Step 4.5: Loop through each day to generate program schedules
    for day in range(num_days):
        # Step 4.6: Loop through each program slot for the day
        for program in range(programs_per_day):
            # Step 4.6.1: Assign programs to all channels
            for channel_id in channels.keys():
                # Step 4.7: Calculate the start time for each program
                program_start = start_time + timedelta(hours=program + day * programs_per_day)
                
                # Step 4.8: Round the start time to the nearest hour
                rounded_start = program_start.replace(minute=0, second=0, microsecond=0)
                
                # Step 4.9: Calculate the end time as 1 hour after the rounded start time
                end_time = rounded_start + timedelta(hours=1)

                # Step 4.10: Create <programme> element for each program with time attributes
                programme_elem = ET.SubElement(tv, "programme",
                                               start=rounded_start.strftime("%Y%m%d%H%M%S %z"),
                                               stop=end_time.strftime("%Y%m%d%H%M%S %z"),
                                               channel=channel_id)
                
                # Step 4.11: Add a <title> element to the program
                title_elem = ET.SubElement(programme_elem, "title", lang="en")
                title_elem.text = f"{channels[channel_id]} at {rounded_start.strftime('%I %p').lstrip('0')}"

                # Step 4.12: Add a <description> element with program details
                description_elem = ET.SubElement(programme_elem, "description")
                description_elem.text = f"Program Description for {channel_id}"

    # Step 4.13: Convert the generated XML structure to a string and return it
    return ET.tostring(tv, encoding='unicode')

# Step 5: Function for pretty printing the XML (to make it more readable)
def pretty_print(xml_string):
    xml_dom = minidom.parseString(xml_string)
    pretty_xml = xml_dom.toprettyxml(indent="  ").strip()
    
    # Step 5.1: Remove unwanted newlines from <channel> tags explicitly
    pretty_xml = re.sub(r'(<channel[^>]*>)(\n\s*)*(<\/channel>)', r'\1\3', pretty_xml)
    
    return pretty_xml

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