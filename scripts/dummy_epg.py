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
# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/dummy_epg.py

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
        "CityNews247Toronto.ca": "City News 24/7",
        # "2": "Channel 2",
        # "3": "Channel 3"
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

                # Conditionally add sub-title for CityNews247Toronto.ca
                if channel_id != "CityNews247Toronto.ca":  # Only add sub-title for other channels
                    sub_title_elem = ET.SubElement(programme_elem, "sub-title")
                    sub_title_elem.text = channels[channel_id]  # Now shows the channel name, e.g., "City News 24/7"

                # Custom description for CityNews247Toronto.ca
                desc_elem = ET.SubElement(programme_elem, "desc")
                if channel_id == "CityNews247Toronto.ca":
                    desc_elem.text = "Toronto's breaking news, including the latest updates on weather, traffic, TTC, sports, and stocks."
                else:
                    desc_elem.text = f"Description for {channels[channel_id]}, program {program + 1}"

    # Step 4.9: Convert the XML to a string
    return ET.tostring(tv, encoding='unicode')

# Step 5: Function for pretty printing the XML (to make it more readable)
def pretty_print(xml_string):
    # First, use minidom to prettify the XML
    xml_dom = minidom.parseString(xml_string)
    pretty_xml = xml_dom.toprettyxml(indent="  ").strip()

    # Remove unwanted newlines from <channel> tags to keep them on one line
    pretty_xml = re.sub(r'(<channel[^>]*>)(\n\s*)(<display-name[^>]*>.*?</display-name>)\s*(</channel>)', r'\1\3\4', pretty_xml)

    # Adjust <programme> tags to be on a single line with appropriate formatting for children
    pretty_xml = re.sub(r'(<programme[^>]*>)\s*(.*?)\s*(</programme>)', r'\1\n\2\n\3', pretty_xml, flags=re.DOTALL)
    
    # Ensure that <title>, <desc>, and other elements inside <programme> are indented
    pretty_xml = re.sub(r'(<programme[^>]*>)\s*(<title>.*?)\s*(<desc>.*?)\s*(</programme>)', r'\1\2\3\4', pretty_xml, flags=re.DOTALL)

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

    # Step 6.3: Define the output file path relative to the current working directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(script_dir, "_epg-end")
    os.makedirs(output_dir, exist_ok=True)

    # Get current date and time in 'YYYY-MM-DD-hh-mm-ss AM/PM' format
    # et_tz = pytz.timezone("America/Toronto")
    # current_datetime = datetime.now(et_tz).strftime("%Y-%m-%d-%I-%M-%S %p")
    # output_file_path = os.path.join(output_dir, f"dummy--epg---{current_datetime}.xml")

    # Define the output file path with current date and time
    output_file_path = os.path.join(output_dir, f"dummy--epg---end.xml")

    # Save the pretty XML to the file
    with open(output_file_path, "w") as f:
        f.write(pretty_xml)

    # Return the path of the generated file
    return output_file_path

# Step 6.4: Delete all older files except the latest one
def delete_old_epg_files(repo_dir, latest_file):
    """
    # Delete all older 'dummy--epg---*.xml' files from the repository except the latest one.
    Delete all older 'dummy--epg---end.xml' files from the repository except the latest one.

    
    :param repo_dir: The root directory of the repository
    :param latest_file: The latest generated EPG file
    """
    try:
        for root, _, files in os.walk(repo_dir):
            for file_name in files:
                if file_name.startswith("dummy--epg---") and file_name.endswith(".xml"):
                    file_path = os.path.join(root, file_name)
                    if file_name != os.path.basename(latest_file):  # Keep the latest file
                        os.remove(file_path)
                        print(f"Deleted old EPG file: {file_path}")
    except Exception as e:
        print(f"Error deleting old files: {e}")

# Get your repository path (update it if needed)
repo_directory = "/Users/kyleabrahams/Documents/GitHub/tv"

# Save the latest EPG XML file and delete older ones from the repo
latest_file_path = save_epg_to_file(num_days=5, programs_per_day=24)
delete_old_epg_files(repo_directory, latest_file_path)

print("Process completed successfully.")
