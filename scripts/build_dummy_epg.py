# build_dummy_epg.py
import xml.etree.ElementTree as ET  # For creating XML elements
from datetime import datetime, timedelta  # For date and time handling
from xml.dom import minidom  # For pretty-printing XML
import os  # For handling file operations
import subprocess  # For installing packages
import sys  # For system operations
import pytz  # For timezone handling
import re  # For regular expressions
import logging
from logging import StreamHandler


# build_dummy_epg.py Mar 7 1230 a 

# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/build_dummy_epg.py

########## Step 0: Set up Logging
LOGGING_ENABLED = True

if LOGGING_ENABLED:
    logger = logging.getLogger("epg_logger")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(message)s", "%b %d %Y %H:%M:%S")  # no level
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Optional: reduce noise from urllib3, etc.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
else:
    class DummyLogger:
        def info(self, msg): logger.info(msg)
        def error(self, msg): logger.info(msg)
        def warning(self, msg): logger.info(msg)
    logger = DummyLogger()

# -------------------------
# Unified logging function
# -------------------------
def log_message(message: str, level: str = "info"):
    """
    Unified logging function.
    - Uses logger if LOGGING_ENABLED is True.
    - Falls back to timestamped print if logging is disabled.
    - Supports levels: 'info', 'error', 'warning'.
    """
    timestamp = datetime.now().strftime("%b %d %Y %H:%M:%S")

    if 'LOGGING_ENABLED' in globals() and LOGGING_ENABLED:
        level_lower = level.lower()
        if level_lower == "info":
            logger.info(message)
        elif level_lower == "error":
            logger.error(message)
        else:
            logger.warning(message)
    else:
        # fallback to print
        logger.info(f"{timestamp} - {level.upper()} - {message}")

# Step 1: Function to install packages
def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Step 2: Check if `pytz` is installed, otherwise install it
try:
    import pytz
except ImportError:
    logger.info("▶️ pytz not found. Installing...")
    try:
        install_package("pytz")
        import pytz  # Import again after installation
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to install pytz: {e}")
        sys.exit(1)  # Exit if installation fails

# Step 3: Print a message indicating pytz is ready to use
logger.info("🟢 pytz is installed and ready to use.")

# Step 4: Function to create the EPG (Electronic Program Guide) XML
def create_epg_xml(num_days=5, programs_per_day=24):
    """
    Generate a dummy EPG XML with DST-aware times for Toronto.
    """
    # Step 1: Create root <tv> element
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")

    # Step 2: Define channels
    channels = {
        "CityNews247Toronto.ca": "City News 24/7",
        # add other channels here if needed
    }

    # Step 3: Create <channel> elements
    for channel_id, channel_name in channels.items():
        channel_elem = ET.SubElement(tv, "channel", id=channel_id)
        display_name_elem = ET.SubElement(channel_elem, "display-name", lang="en")
        display_name_elem.text = channel_name

    # Step 4: Get current time in Toronto (DST-aware)
    import pytz
    from datetime import datetime, timedelta

    toronto_tz = pytz.timezone("America/Toronto")
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    start_time = utc_now.astimezone(toronto_tz)  # Toronto local time with DST applied

    # Step 5: Generate program schedule
    for day in range(num_days):
        for program_index in range(programs_per_day):
            for channel_id in channels.keys():
                # Calculate start and end times for each program
                program_start = start_time + timedelta(hours=program_index + day * programs_per_day)
                program_start = program_start.replace(minute=0, second=0, microsecond=0)
                program_end = program_start + timedelta(hours=1)

                # Step 5.1: Create <programme> element with DST-aware times
                programme_elem = ET.SubElement(tv, "programme",
                                               start=program_start.strftime("%Y%m%d%H%M%S %z"),
                                               stop=program_end.strftime("%Y%m%d%H%M%S %z"),
                                               channel=channel_id)

                # Step 5.2: Add <title>
                title_elem = ET.SubElement(programme_elem, "title")
                title_elem.text = f"{channels[channel_id]} at {program_start.strftime('%I').lstrip('0')}"

                # Step 5.3: Optionally add <sub-title> for other channels
                if channel_id != "CityNews247Toronto.ca":
                    sub_title_elem = ET.SubElement(programme_elem, "sub-title")
                    sub_title_elem.text = channels[channel_id]

                # Step 5.4: Add <desc> element
                desc_elem = ET.SubElement(programme_elem, "desc")
                if channel_id == "CityNews247Toronto.ca":
                    desc_elem.text = "Toronto's breaking news, including the latest updates on weather, traffic, transit, sports, and stocks."
                else:
                    desc_elem.text = f"Description for {channels[channel_id]}, program {program_index + 1}"

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
                        logger.info(f"✅ Deleted old EPG file: {file_path}")
    except Exception as e:
        logger.info(f"Error deleting old files: {e}")

# Get your repository path (update it if needed)
repo_directory = "/Users/kyleabrahams/Documents/GitHub/tv"

# Save the latest EPG XML file and delete older ones from the repo
if __name__ == "__main__":
    latest_file_path = save_epg_to_file(num_days=5, programs_per_day=24)
    delete_old_epg_files(repo_directory, latest_file_path)
    logger.info("✅ dummy--epg---end.xml created successfully.")