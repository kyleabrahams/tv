# merge_build_epg.py starts here
#!/usr/bin/env python3

########## Step 1: Standard library imports
import sys
import re
import logging
import subprocess
from datetime import datetime
from time import sleep
from xml.dom import minidom
from logging import StreamHandler
# from build_dummy_epg import build_dummy_epg

# Third-party imports
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pytz
import os, gzip, io, xml.etree.ElementTree as ET, time


# Local imports
from build_channels_list import CHANNELS


# merge_epg.py Mar 6 2026 807 p 
# python3 -m venv myenv
# source myenv/bin/activate
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/merge_build_epg.py


########## Step 2: === Configuration ===

# Detect if running in GitHub Actions
CI_SAFE = os.getenv("GITHUB_ACTIONS") == "true"
delay = 5
sleep_time = 1 if CI_SAFE else delay

# Base directory of the repo
REPO_DIR = os.path.abspath(os.path.dirname(__file__))

# EPG file paths (absolute)
FAST_EPG_FILE = os.path.join(REPO_DIR, "scripts", "_epg-end", "fast-epg-end.xml")
DUMMY_EPG_FILE = os.path.join(REPO_DIR, "scripts", "_epg-end", "dummy--epg---end.xml")
BUILD_EPG_SCRIPT = os.path.join(REPO_DIR, "build_epg.py")
BUILD_DUMMY_EPG_SCRIPT = os.path.join(REPO_DIR, "build_dummy_epg.py")

# Python executable
venv_python = sys.executable

# -------------------------

########## Step 3: Global toggles
# -------------------------
run_build_fast_epg = True  
run_build_dummy_epg = True
run_channels_custom = False
run_channels_custom_date = False  
run_channels_test = False
run_channels_test_copy = False    



########## Step 4: Set up Logging
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


########## Step 5: Unified log function
def log_message(message, level="info"):
    """
    Single logging entry point. Timestamp handled by logging formatter.
    """
    if not LOGGING_ENABLED:
        logger.info(message)
        return

    level_lower = level.lower()

    if level_lower == "info":
        logger.info(message)
    elif level_lower == "error":
        logger.error(message)
    else:
        logger.warning(message)

 


########## Step 6: Function to run dummy_epg.py script
def run_npm_grab():
    global run_build_dummy_epg
    global run_build_fast_epg
    global run_channels_custom
    global run_channels_custom_date
    global run_channels_test
    global run_channels_test_copy

    # rest of your function...

    # -------------------------
    # DIRECTORIES
    # -------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    epg_end_dir = os.path.join(script_dir, "_epg-end")
    os.makedirs(epg_end_dir, exist_ok=True)  # ensure output folder exists

    # -------------------------
    # PRE-SCRIPTS
    # -------------------------

    pre_scripts = [
        (True, "/Volumes/Kyle4tb1223/Documents/Github/tv/scripts/build_dummy_epg.py"),
        (False, "/Volumes/Kyle4tb1223/Documents/Github/tv/scripts/build_epg.py"),
    ]

    for toggle, script_path in pre_scripts:
        script_name = os.path.basename(script_path)

        if not toggle:
            logger.info(f"🔴Skipping {script_name} (toggle is False)")
            continue

        if not os.path.exists(script_path):
            logger.info(f"❌ {script_name} not found, skipping")
            continue

        logger.info(f"▶️ Running {script_name}...")

        # Run Python subprocess in unbuffered mode, streaming output live
        with subprocess.Popen(
            [sys.executable, "-u", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        ) as proc:
            for line in proc.stdout:
                logger.info(line.rstrip())  # global timestamp

            proc.wait()
            if proc.returncode == 0:
                logger.info(f"✅{script_name} finished successfully")
            else:
                logger.info(f"❌{script_name} finished with errors (code {proc.returncode})")

    # -------------------------
    # TIMESTAMP
    # -------------------------
    current_datetime = datetime.now().strftime("%m-%d-%I-%M-%S %p")

    # -------------------------
    # NPM GRAB COMMANDS
    # -------------------------
    commands = []

    if run_channels_custom_date:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-custom-start.xml')}",
            f"--output={os.path.join(epg_end_dir, f'channels-custom-{current_datetime}.xml')}"
        ])

    if run_channels_custom:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-custom-start.xml')}",
            f"--output={os.path.join(epg_end_dir, 'channels-custom-end.xml')}"
        ])

    if run_channels_test:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-test-start.xml')}",
            f"--output={os.path.join(epg_end_dir, 'channels-test-end.xml')}"
        ])

    if run_channels_test_copy:
        commands.append([
            "npm", "run", "grab", "--", "--continue-on-error",
            f"--channels={os.path.join(script_dir, '_epg-start/channels-test-start-copy.xml')}",
            f"--output={os.path.join(epg_end_dir, f'channels-test-copy-{current_datetime}.xml')}"
        ])

    # -------------------------
    # CLEAN OLD TIMESTAMPED FILES
    # -------------------------
    try:
        for file_name in os.listdir(epg_end_dir):
            file_path = os.path.join(epg_end_dir, file_name)
            if file_name.startswith("channels-") and file_name.endswith(".xml") and not file_name.endswith("-end.xml"):
                os.remove(file_path)
                logger.info(f"🧹 Deleted old timestamped file: {file_path}")
    except Exception as e:
        logger.info(f"❌Error deleting old files: {e}")

    # -------------------------
    # RUN NPM COMMANDS
    # -------------------------
    for command in commands:
        command_str = " ".join(command)
        logger.info(f"▶️Running command: {command_str}")
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            # Output stdout
            for line in process.stdout.splitlines():
                logger.info(f"STDOUT: {line}")

            # Output stderr
            for line in process.stderr.splitlines():
                logger.info(f"STDERR: {line}")

            if process.returncode == 0:
                logger.info(f"✅Command executed successfully: {command_str}")
                # Optional: detect number of channels
                channel_count_pattern = r"found (\d+) channel\(s\)"
                for line in process.stdout.splitlines():
                    match = re.search(channel_count_pattern, line)
                    if match:
                        logger.info(f"✅{match.group(1)} channel(s) in output")
                        break
            else:
                logger.info(f"⚠️Command failed (continuing anyway): {command_str}, return code: {process.returncode}")

        except Exception as e:
            logger.info(f"❌Exception running command {command_str}: {e}")



########## Step 7: Build FAST EPG
def build_fast_epg():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml")

    XMLTV_URLS = [
        # "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_CY1.xml.gz",
        "https://i.mjh.nz/PlutoTV/all.xml",
        "https://i.mjh.nz/Plex/all.xml",
        "https://i.mjh.nz/Roku/all.xml",
        "https://raw.githubusercontent.com/acidjesuz/EPGTalk/refs/heads/master/guide.xml",
        "https://i.mjh.nz/SamsungTVPlus/all.xml"
    ]

    logger.info("▶️ Building FAST EPG")

    seen_channels = {}
    programmes = []

    for url in XMLTV_URLS:

        root = fetch_epg_data(url, 0, 0)

        if not root:
            continue

        root = root.getroot()

        for channel in root.findall("channel"):

            cid = channel.get("id")

            if not cid or (CHANNELS and cid not in CHANNELS) or cid in seen_channels:
                continue

            for icon in channel.findall("icon"):
                channel.remove(icon)

            url_elem = ET.Element("url")
            url_elem.text = url
            channel.append(url_elem)

            seen_channels[cid] = channel

        for prog in root.findall("programme"):

            cid = prog.get("channel")

            if not cid or (CHANNELS and cid not in CHANNELS):
                continue

            programmes.append(prog)

    merged_root = ET.Element("tv")

    for cid in sorted(seen_channels.keys()):
        merged_root.append(seen_channels[cid])

    for prog in programmes:
        merged_root.append(prog)

    tree = ET.ElementTree(merged_root)

    ensure_permissions(OUTPUT_XML)

    tree.write(OUTPUT_XML, encoding="utf-8", xml_declaration=True)

    logger.info(f"✅ FAST EPG built: {OUTPUT_XML}")
    logger.info(f"📺 Channels: {len(seen_channels)}")




########## Step 8: Merge EPG data
def merge_epg_data(epg_urls, epg_end_dir, save_path):
    """
    Merge multiple EPG XML files into a single XML and remove duplicates.
    """
    logger.info("▶️ Merging EPG data...")

    merged_root = ET.Element("tv")
    total = len(epg_urls)

    seen_channels = set()
    seen_programmes = set()

    # Convert merged_root to string
    xml_bytes = ET.tostring(merged_root, encoding="utf-8", xml_declaration=True)
    xml_str = xml_bytes.decode()

    # Collapse <channel> elements to single line
    xml_str = re.sub(
        r'(<channel[^>]*>)(.*?)(</channel>)',
        lambda m: m.group(1) + re.sub(r'\s+', ' ', m.group(2).strip()) + m.group(3),
        xml_str,
        flags=re.DOTALL
    )

    # Collapse <programme> elements to single line
    xml_str = re.sub(
        r'(<programme[^>]*>)(.*?)(</programme>)',
        lambda m: m.group(1) + re.sub(r'\s+', ' ', m.group(2).strip()) + m.group(3),
        xml_str,
        flags=re.DOTALL
    )

    # Save final XML
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    for index, url in enumerate(epg_urls, start=1):  # add start=1 for human-friendly numbering
        # 🔄 Progress log
        logger.info(f"🔄 Fetching {index}/{total} - {url}")

        tree = fetch_epg_data(url, index, total, folder_path=epg_end_dir)

        if not tree:
            continue

        for el in tree.getroot():

            # CHANNEL
            if el.tag == "channel":
                cid = el.get("id")

                if cid in seen_channels:
                    continue

                seen_channels.add(cid)

                for icon in el.findall("icon"):
                    el.remove(icon)

                merged_root.append(el)

            # PROGRAMME
            elif el.tag == "programme":

                key = (
                    el.get("channel"),
                    el.get("start"),
                    el.get("stop")
                )

                if key in seen_programmes:
                    continue

                seen_programmes.add(key)

                merged_root.append(el)

    reorder_channels(merged_root)

    ensure_permissions(save_path)

    write_epg_single_line(merged_root, save_path)
    logger.info(f"✅ EPG file saved to {save_path} (single-line <programme> & <channel>)")

    logger.info(f"✅ EPG file saved to {save_path}")
    logger.info(f"📺 Channels: {len(seen_channels)}")
    logger.info(f"📡 Programmes: {len(seen_programmes)}")




########## Step 9: Check for XML files if no URLs are found
def load_local_xml_files(directory):
    """
    Look for XML files in the directory if no EPG URLs are found.
    Returns a list of absolute paths to XML files.
    """
    xml_files = []
    try:
        # Scan the directory
        log_message(f"🔄Scanning directory: {directory}", level="info")
        files_in_directory = os.listdir(directory)
        log_message(f"⬇️ Files in directory: {files_in_directory}", level="info")
        
        # Filter for .xml files, skip macOS hidden files
        for filename in files_in_directory:
            if filename.endswith(".xml") and not filename.startswith("._"):
                file_path = os.path.join(directory, filename)
                log_message(f"🟢Found XML file: {file_path}", level="info")
                xml_files.append(file_path)
        
        log_message(f"🔍 XML files found: {xml_files}", level="info")
        return xml_files

    except Exception as e:
        # Log errors as 'error' level
        log_message(f"❌Error loading XML files from {directory}: {e}", level="error")
        return []




########## Step 10: Path to save the merged EPG file
REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # Assuming the script is part of the repository
save_path = os.path.join(REPO_DIR, "www", "epg.xml")  # Path where the EPG file will be saved
# save_path = os.path.join(REPO_DIR, "www", "epg-test.xml")  # Path where the EPG file will be saved

# Define the directory for .gz files
gz_directory = os.path.join(REPO_DIR, "www")  # Directory where .gz files are located

# You can now process files within the gz_directory or save to save_path
logger.info(f"⬇️ EPG file will be saved to: {save_path}")
logger.info(f"⬇️ .gz files are located in: {gz_directory}")




########## Step 11: Function to ensure directory and file permissions
def ensure_permissions(file_path):
    # Ensure the directory exists
    directory = os.path.dirname(file_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        logger.info(f"Directory {directory} does not exist. Creating it...")
        os.makedirs(directory, exist_ok=True)

    # Check if we have write permissions on the directory, and if not, set it
    if not os.access(directory, os.W_OK):
        logger.info(f"Directory {directory} does not have write permissions. Updating permissions...")
        os.chmod(directory, 0o755)  # Set write permission for the directory owner

    # If the file already exists, check and ensure it has write permissions
    if os.path.exists(file_path):
        if not os.access(file_path, os.W_OK):
            logger.info(f"File {file_path} does not have write permissions. Updating permissions...")
            os.chmod(file_path, 0o644)  # Set write permission for the file owner
    else:
        logger.info(f"File {file_path} does not exist. It will be created.")

# Ensure permissions for the save path
ensure_permissions(save_path)




########## Step 12: Function to fetch and merge EPG data
def fetch_epg_data(url, index, total, retries=3, delay=5, folder_path="scripts/_epg-end"):

    is_remote = url.startswith("http://") or url.startswith("https://")
    logger.info(f"🔄Fetching {index + 1}/{total} - {url}")

    if is_remote:
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    if not response.content or not isinstance(response.content, (bytes, str)):
                        logger.info(f"⚠️Empty response from site: {url}")
                        return None

                    try:
                        # Handle .gz files
                        if url.endswith(".gz"):
                            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                                xml_content = gz.read()
                            return ET.ElementTree(ET.fromstring(xml_content))
                        else:
                            return ET.ElementTree(ET.fromstring(response.content))
                    except ET.ParseError as e:
                        logger.info(f"⚠️Invalid XML from site {url}: {e}")
                        return None
                else:
                    logger.info(f"❌HTTP error {response.status_code} from site {url}")
                    return None
            except requests.RequestException as e:
                logger.info(f"⚠️Attempt {attempt+1}/{retries} failed for site {url}: {e}")
                attempt += 1
                if attempt < retries:
                    time.sleep(delay)
        logger.info(f"❌Failed to fetch from site {url} after {retries} attempts.")
        return None

    else:
        # Local file path
        if not os.path.isabs(url):
            url = os.path.join(folder_path, url)

        if not os.path.exists(url):
            logger.info(f"❌Local file does not exist: {url}")
            return None

        try:
            if url.endswith(".gz"):
                with gzip.open(url, "rb") as f:
                    xml_content = f.read()
                if not xml_content:
                    logger.info(f"⚠️Empty local file: {url}")
                    return None
                return ET.ElementTree(ET.fromstring(xml_content))
            else:
                tree = ET.parse(url)
                if tree is None:
                    logger.info(f"⚠️Empty local file: {url}")
                    return None
                return tree
        except ET.ParseError as e:
            logger.info(f"❌Failed to parse local XML file {url}: {e}")
            return None
        except Exception as e:
            logger.info(f"❌Error processing local file {url}: {e}")
            return None




########## Step 13: Function to reorder channels to the top of the XML
def reorder_channels(merged_root):
    # Extract all <channel> elements
    channels = [el for el in merged_root.findall('channel')]

    # Extract all <programme> elements
    programmes = [el for el in merged_root.findall('programme')]

    # Clear the current root (we'll rebuild it)
    merged_root.clear()

    # Append the channels first
    for channel in channels:
        # Remove any <icon> elements
        for icon in channel.findall("icon"):
            channel.remove(icon)
        merged_root.append(channel)

    # Then append the programmes
    for programme in programmes:
        merged_root.append(programme)


# Assuming merged_root is your root element containing XML data
merged_root = ET.Element("tv")

# Reorder channels to be at the top
reorder_channels(merged_root)

# Pretty print the merged and reordered XML
# pretty_xml = pretty_print_xml(ET.ElementTree(merged_root))

# Assuming epg_urls contains your XML URLs (remote or local)
folder_path = "scripts/_epg-end"  # Update to your folder path

########## Step 14: XML Elements to single line

from xml.sax.saxutils import escape

def element_to_single_line(el):
    parts = []
    # Build attributes
    attrs = " ".join(f'{k}="{escape(v)}"' for k, v in el.attrib.items())
    start_tag = f"<{el.tag}" + (f" {attrs}" if attrs else "") + ">"
    parts.append(start_tag)

    # Escape text content
    if el.text and el.text.strip():
        parts.append(escape(el.text.strip()))

    # Process children recursively
    for child in el:
        parts.append(element_to_single_line(child))

    parts.append(f"</{el.tag}>")
    return "".join(parts)


from xml.sax.saxutils import escape

def element_to_single_line(el):
    """Serialize a <channel> or <programme> element to a single line with escaped content."""
    attrs = " ".join(f'{k}="{escape(v)}"' for k, v in el.attrib.items())
    start_tag = f"<{el.tag}" + (f" {attrs}" if attrs else "") + ">"

    # Element text
    text_content = escape(el.text.strip()) if el.text else ""

    # Children (flattened)
    children_content = "".join(element_to_single_line(child) for child in el)

    return f"{start_tag}{text_content}{children_content}</{el.tag}>"

def write_epg_single_line(root, save_path):
    """Write full XML tree with <channel> and <programme> as single lines."""
    with open(save_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write("<tv>\n")
        for el in root:
            if el.tag in ("channel", "programme"):
                f.write(element_to_single_line(el) + "\n")
            else:
                f.write(ET.tostring(el, encoding="utf-8").decode("utf-8") + "\n")
        f.write("</tv>\n")



########## Step 15: Save the merged EPG file and log success
try:
    # merged_tree = ET.ElementTree(merged_root)
    # merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    write_epg_single_line(merged_root, save_path)
    logger.info(f"✅ EPG file saved to {save_path}")
    
except Exception as e:
    # Log error if save fails
    error_message = f"❌Failed to save EPG file - Error: {e}"
    logging.error(error_message)
    logger.info(error_message)
  

  

########## Step 16: __main__ block
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    epg_end_dir = os.path.join(script_dir, "_epg-end")
    os.makedirs(epg_end_dir, exist_ok=True)

    # -------------------------
    # Step 1: Run dummy + npm grab
    # -------------------------
    run_npm_grab()

    # -------------------------
    # Step 2: Build FAST EPG
    # -------------------------
    if run_build_fast_epg:
        logger.info("▶️ Running build_fast_epg via subprocess...")
        subprocess.run([sys.executable, BUILD_EPG_SCRIPT], check=True)
        logger.info("✅ build_fast_epg finished")

    # -------------------------
    # Step 2b: Build Dummy EPG
    # -------------------------
    if run_build_dummy_epg:
        logger.info("▶️ Running build_dummy_epg.py via subprocess...")
        subprocess.run([sys.executable, BUILD_DUMMY_EPG_SCRIPT], check=True)
        logger.info("✅ build_dummy_epg.py finished")

    # -------------------------
    # Step 3: Collect XML files for merge (only enabled toggles)
    # -------------------------
    epg_urls = []
    seen_files = set()  # to avoid duplicates

    for f in os.listdir(epg_end_dir):
        if f.endswith(".xml") and not f.startswith("._"):  # ignore hidden macOS files
            file_path = os.path.join(epg_end_dir, f)
            if file_path not in seen_files:
                epg_urls.append(file_path)
                seen_files.add(file_path)
                logger.info(f"🟢 Added EPG file for merge: {file_path}")

    # Sort files if you want FAST EPG first, Dummy EPG second
    epg_urls.sort(key=lambda x: ("fast-epg" not in x, "dummy--epg" not in x))

    # -------------------------
    # Step 4: Ensure save directory & permissions
    # -------------------------
    save_path = os.path.join(script_dir, "www", "epg.xml")
    ensure_permissions(save_path)

    # -------------------------
    # Step 5: Merge files
    # -------------------------
    if epg_urls:
        merge_epg_data(epg_urls, epg_end_dir, save_path)
        logger.info(f"🏁 EPG build complete. Merged {len(epg_urls)} file(s) into {save_path}")
    else:
        logger.warning("⚠️ No EPG files found to merge. Nothing was saved.")