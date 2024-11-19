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
def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Step 2: Check if `pytz` is installed, otherwise install it
try:
    import pytz
except ImportError:
    print("pytz not found. Installing...")
    try:
        install_package("pytz")
        import pytz  # Import again after installation
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pytz: {e}")
        sys.exit(1)  # Exit if installation fails

# Step 3: Print a message indicating pytz is ready to use
print("pytz is installed and ready to use.")

# Step 4: Function to create the EPG (Electronic Program Guide) XML
def create_epg_xml(num_days=5, programs_per_day=24):
    # Step 4.1: Create the root <tv> element with generator info attributes
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")

    # Step 4.2: Define a dictionary of channels with their IDs and display names
    channels = {
        "City News 24/7 Toronto": "City News 24/7",
        "2": "Channel 2",
        "3": "Channel 3"
    }

    # Step 4.3: Loop through the channel dictionary and create <channel> elements
    for channel_id, channel_name in channels.items():
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name

    # Step 4.4: Get the current UTC time and convert to Eastern Time
    utc_now = datetime.now(pytz.UTC)  # Current time in UTC
    eastern = pytz.timezone('US/Eastern')  # Define Eastern Time zone
    start_time = utc_now.astimezone(eastern)  # Convert UTC to localized Eastern Time

    # Step 4.5: Loop through each day to generate program schedules
    for day in range(num_days):
        for program in range(programs_per_day):
            for channel_id in channels.keys():
                # Step 4.6: Calculate start and end times
                program_start = start_time + timedelta(hours=program + day * programs_per_day)
                rounded_start = program_start.replace(minute=0, second=0, microsecond=0)
                end_time = rounded_start + timedelta(hours=1)

                # Step 4.7: Create <programme> element
                programme_elem = ET.SubElement(tv, "programme",
                                               start=rounded_start.strftime("%Y%m%d%H%M%S %z"),
                                               stop=end_time.strftime("%Y%m%d%H%M%S %z"),
                                               channel=channel_id)
                
                # Step 4.8: Add title, (conditionally add sub-title), and description elements
                title_elem = ET.SubElement(programme_elem, "title")
                title_elem.text = f"{channels[channel_id]} at {rounded_start.strftime('%I').lstrip('0')}"  # Shows the hour without leading zero

                # Conditionally add sub-title for City News 24/7 Toronto
                if channel_id != "City News 24/7 Toronto":  # Only add sub-title for other channels
                    sub_title_elem = ET.SubElement(programme_elem, "sub-title")
                    sub_title_elem.text = channels[channel_id]  # Now shows the channel name, e.g., "City News 24/7"

                # Custom description for City News 24/7 Toronto
                desc_elem = ET.SubElement(programme_elem, "desc")
                if channel_id == "City News 24/7 Toronto":
                    desc_elem.text = "Toronto's breaking news, including the latest updates on weather, traffic, TTC, sports, and stocks."
                else:
                    desc_elem.text = f"Description for {channels[channel_id]}, program {program + 1}"

    # Step 4.9: Convert the XML to a string
    return ET.tostring(tv, encoding='unicode')

# Step 5: Function for pretty printing the XML (to make it more readable)
def pretty_print(xml_string):
    xml_dom = minidom.parseString(xml_string)
    pretty_xml = xml_dom.toprettyxml(indent="  ").strip()
    
    # Remove unwanted newlines from <channel> tags
    pretty_xml = re.sub(r'(<channel[^>]*>)(\n\s*)*(<\/channel>)', r'\1\3', pretty_xml)

    # Remove any additional <?xml ...?> declarations except the first one
    pretty_xml = re.sub(r'(<\?xml.*\?>\n?)+', '', pretty_xml, count=1)
    
    return pretty_xml

# Step 6: Function to save the EPG XML to a file with the XML declaration
def save_epg_to_file(num_days=5, programs_per_day=24):
    # Step 6.1: Generate and pretty-print the EPG XML
    epg_xml = create_epg_xml(num_days=num_days, programs_per_day=programs_per_day)
    pretty_xml = pretty_print(epg_xml)

    # Step 6.2: Add XML declaration manually for utf-8
    pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml

    # Step 6.3: Define the output file path
    output_dir = "/Users/kyleabrahams/Documents/GitHub/tv"
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, "dummy.xml")

    # Step 6.4: Save the XML to the file
    try:
        with open(output_file_path, "w", encoding="UTF-8") as xml_file:
            xml_file.write(pretty_xml)
        print(f"EPG data saved to {output_file_path}")
        return output_file_path
    except Exception as e:
        print(f"Error saving EPG data: {e}")
        sys.exit(1)

# Step 7: Run the function to generate and save the EPG XML
save_epg_to_file(num_days=5, programs_per_day=24)
