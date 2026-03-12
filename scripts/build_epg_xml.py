# build_epg_xml.py starts here
#!/usr/bin/env python3

########## Step 1: Standard library imports
import sys  # Access system-specific parameters and functions (e.g., sys.exit, interpreter path)
import os  # File and directory operations (paths, creating folders, permissions)
import re  # Regular expressions for searching and modifying text patterns
import io  # In-memory streams for handling bytes/text like files
import gzip  # Read and write .gz compressed files
import time  # Basic time functions (timestamps, delays)
import logging  # Logging framework for structured console/file output
import subprocess  # Run external commands or scripts from Python
from datetime import datetime  # Date/time objects (timestamps, formatting)
from time import sleep  # Pause execution for a number of seconds
from xml.etree import ElementTree as ET  # XML parsing and creation (main XMLTV manipulation)
from xml.dom import minidom  # Pretty-printing XML for readability
from logging import StreamHandler  # Sends logging output to console or streams
from typing import Set  # Type hint for sets (improves readability and editor support)
from typing import Optional  # Type hint indicating a value may be None

########## Third-party imports (installed via pip) ##########

import requests  # HTTP library used to download XMLTV EPG files from URLs
from requests.adapters import HTTPAdapter  # Allows custom retry/connection behavior for requests
from urllib3.util.retry import Retry  # Retry strategy for failed HTTP requests
import pytz  # Timezone handling (needed for accurate EPG timestamps)

########## Local imports (your project files) ##########

from build_channels_list import CHANNELS # CHANNELS is your predefined channel list used to filter the EPG
  
# build_epg_xml.py Mar 12 325 p 

# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/build_epg_xml.py
# python3 C:\Users\User\OneDrive\Documents\GitHub\tv\scripts\build_epg_xml.py


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
# BUILD_EPG_SCRIPT = os.path.join(REPO_DIR, "build_epg.py") # WHY EXECUTE?
BUILD_DUMMY_EPG_SCRIPT = os.path.join(REPO_DIR, "build_dummy_epg.py")

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Base directory relative to this script
OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml") # Output path inside scripts/_epg-end
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# Python executable
venv_python = sys.executable

# User-Agent header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

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
        print(f"{timestamp} - {level.upper()} - {message}")

 


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


########## Step 7: Process Root (TVG-ID filtered) ##########
def process_root(root, seen_channels, seen_programmes, tvg_ids):
    """
    Process an XML root element:
    - Remove <icon> elements from channels
    - Deduplicate channels and programmes
    - Filter channels and programmes by TVG IDs
    Yields programmes for appending.
    """
    # Process channels
    for channel in root.findall("channel"):
        cid = channel.get("id")
        if not cid:
            continue
        if cid in seen_channels:
            continue
        if tvg_ids and cid not in tvg_ids:
            continue

        # Remove <icon> elements
        for icon in channel.findall("icon"):
            channel.remove(icon)

        # Mark channel as seen
        seen_channels[cid] = channel

    # Process programmes
    for prog in root.findall("programme"):
        cid = prog.get("channel")
        if not cid:
            continue
        if tvg_ids and cid not in tvg_ids:
            continue

        # Deduplicate programmes by (channel, start, stop)
        key = (cid, prog.get("start"), prog.get("stop"))
        if key in seen_programmes:
            continue
        seen_programmes.add(key)

        yield prog




########## Step 7: Build FAST EPG with removed <icons>
def remove_icons(root):
    """Recursively remove all <icon> elements from an XML tree."""
    for elem in root.findall(".//icon"):
        parent = elem.getparent() if hasattr(elem, "getparent") else root
        try:
            parent.remove(elem)
        except Exception:
            # fallback: try root.remove (already done per-element above)
            pass

def build_fast_epg(tvg_ids: set):
    global CHANNELS  # <-- this makes CHANNELS visible here
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml")
    os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

    XMLTV_URLS = [
        "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz", 
        "https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_CY1.xml.gz",
        "https://raw.githubusercontent.com/BuddyChewChew/xumo-playlist-generator/main/playlists/xumo_epg.xml.gz",
        "https://i.mjh.nz/PlutoTV/all.xml",
        "https://i.mjh.nz/Plex/all.xml",
        "https://i.mjh.nz/Roku/all.xml",
        "https://i.mjh.nz/SamsungTVPlus/all.xml",
        "https://raw.githubusercontent.com/acidjesuz/EPGTalk/refs/heads/master/guide.xml"
    ]

    seen_channels = {}
    seen_programmes = set()
    programmes = []

    total_urls = len(XMLTV_URLS)

    for index, url in enumerate(XMLTV_URLS, start=1):
        log_message(f"🔄 Fetching {index}/{total_urls} - {url}")
        tree = fetch_epg_data(url, index=index, total=total_urls)
        if not tree:
            continue
        root = tree.getroot()

        # --- Channels ---
        for channel in root.findall("channel"):
            cid = channel.get("id")
            if not cid or (tvg_ids and cid not in tvg_ids):
                continue  # Skip channels not in M3U

            if cid not in seen_channels:
                # Remove icons
                for icon in channel.findall("icon"):
                    channel.remove(icon)

                # Add <url> element only once per channel
                url_elem = ET.Element("url")
                url_elem.text = url
                channel.append(url_elem)

                seen_channels[cid] = channel

        # --- Programmes ---
        for prog in root.findall("programme"):
            cid = prog.get("channel")
            if not cid or (tvg_ids and cid not in tvg_ids):
                continue  # Skip programmes not in M3U

            key = (cid, prog.get("start"), prog.get("stop"), prog.findtext("title", ""))
            if key in seen_programmes:
                continue

            seen_programmes.add(key)
            programmes.append(prog)

    # --- Count programmes per channel ---
    prog_count_by_channel = {}
    for prog in programmes:
        cid = prog.get("channel")
        if cid:
            prog_count_by_channel[cid] = prog_count_by_channel.get(cid, 0) + 1

    # --- Sort channels A-Z by display-name ---
    sorted_channels = sorted(
        seen_channels.values(),
        key=lambda ch: (ch.findtext("display-name") or "").lower()
    )

    # Log channels
    logger.info(f"📺 Total channels after TVG filtering: {len(sorted_channels)}")
    for channel in sorted_channels:
        cid = channel.get("id")
        name = channel.findtext("display-name") or "Unknown"
        count = prog_count_by_channel.get(cid, 0)
        logger.info(f"📺 {name} - {cid} ({count} programs)")

    # --- Merge into final XML ---
    merged_root = ET.Element("tv")
    for channel in sorted_channels:
        merged_root.append(channel)
    for prog in programmes:
        merged_root.append(prog)

    # Remove any leftover <icon> tags
    # remove_icons(merged_root)

    # Ensure directory permissions
    ensure_permissions(OUTPUT_XML)

    # Write final XML as single-line
    write_epg_single_line(merged_root, OUTPUT_XML)
    logger.info(f"✅ fast-epg-end.xml created successfully (TVG-filtered)")




########## Step 8: Merge EPG data (with optional TVG-ID filtering) ##########
def build_data(sources, save_path, tvg_ids: Optional[set] = None, folder_path: Optional[str] = None):
    """
    Merge multiple XMLTV sources (local or remote), filter by TVG IDs if provided,
    deduplicate channels and programmes, remove <icon> tags, and save as a single-line epg.xml.

    sources: list of URLs or local file paths
    save_path: path to final XML file
    tvg_ids: optional set of tvg-id strings to filter channels
    folder_path: optional base folder for relative local files
    """
    merged_root = ET.Element("tv")
    seen_channels = {}  # dict: channel_id -> channel element
    seen_programmes = set()  # set of (channel_id, start, stop)

    if not sources:
        log_message("⚠️ No sources provided to merge.", level="warning")
        return

    for idx, src in enumerate(sources, start=1):
        log_message(f"🔄 Processing {idx}/{len(sources)} - {src}")

        # Fetch XML tree (remote or local)
        tree = fetch_epg_data(src, index=idx, total=len(sources), folder_path=folder_path)
        if not tree:
            log_message(f"⚠️ Skipping {src} (failed to fetch/parse)", level="warning")
            continue

        root = tree.getroot()
        log_message(f"📄 {src}: {len(root.findall('channel'))} channels, {len(root.findall('programme'))} programmes found")

        # Process channels & programmes
        for prog in process_root(root, seen_channels, seen_programmes, tvg_ids):
            merged_root.append(prog)

    # Append all unique channels at the start
    for channel in seen_channels.values():
        merged_root.insert(0, channel)

    # Final cleanup & write
    reorder_channels(merged_root)
    ensure_permissions(save_path)
    write_epg_single_line(merged_root, save_path)

    log_message(f"✅ Merged EPG complete: {len(seen_channels)} channels, {len(seen_programmes)} programmes")

    if len(seen_channels) == 0:
        log_message("⚠️ Warning: No channels were merged. Check TVG IDs or source files.", level="warning")
    if len(seen_programmes) == 0:
        log_message("⚠️ Warning: No programmes were merged. Check your EPG sources.", level="warning")    
    """
    Merge multiple XMLTV sources (local or remote), filter by TVG IDs if provided,
    deduplicate, remove <icon> tags, and save as a single-line epg.xml.

    sources: list of URLs or local file paths
    save_path: path to final XML file
    tvg_ids: optional set of tvg-id strings to filter channels
    folder_path: optional base folder for relative local files
    """
    merged_root = ET.Element("tv")
    seen_channels = set()
    seen_programmes = set()

    if not sources:
        log_message("⚠️ No sources provided to merge.", level="warning")
        return

    for idx, src in enumerate(sources, start=1):
        log_message(f"🔄 Processing {idx}/{len(sources)} - {src}")

        # Fetch XML tree (remote or local)
        tree = fetch_epg_data(src, index=idx, total=len(sources), folder_path=folder_path)
        if not tree:
            log_message(f"⚠️ Skipping {src} (failed to fetch/parse)", level="warning")
            continue

        root = tree.getroot()
        channels = root.findall("channel")
        programmes = root.findall("programme")
        log_message(f"📄 {src}: {len(channels)} channels, {len(programmes)} programmes found")

        # Merge channels
        for ch in channels:
            cid = ch.get("id")
            channel_tvg = (ch.get("tvg-id") or "").strip()
            if not cid:
                continue
            if tvg_ids and channel_tvg and channel_tvg not in tvg_ids:
                continue
            if cid in seen_channels:
                continue

            # Remove <icon>
            # for icon in ch.findall("icon"):
            #     ch.remove(icon)

            merged_root.append(ch)
            seen_channels.add(cid)

        # Merge programmes
        for prog in programmes:
            prog_channel = prog.get("channel")
            key = (prog_channel, prog.get("start"), prog.get("stop"))
            if key in seen_programmes:
                continue
            if tvg_ids and prog_channel not in seen_channels:
                continue

            merged_root.append(prog)
            seen_programmes.add(key)

    # Final cleanup & write
    reorder_channels(merged_root)
    # remove_icons(merged_root)
    ensure_permissions(save_path)
    write_epg_single_line(merged_root, save_path)

    log_message(f"✅ Merged EPG complete: {len(seen_channels)} channels, {len(seen_programmes)} programmes")

    if len(seen_channels) == 0:
        log_message("⚠️ Warning: No channels were merged. Check TVG IDs or source files.", level="warning")
    if len(seen_programmes) == 0:
        log_message("⚠️ Warning: No programmes were merged. Check your EPG sources.", level="warning")




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
# logger.info(f"⬇️  EPG file will be saved to: {save_path}")
# logger.info(f"⬇️  .gz files are located in: {gz_directory}")




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
def fetch_epg_data(
    url: str,
    index: int = 0,
    total: int = 1,
    retries: int = 3,
    delay_sec: int = 5,
    folder_path: str = "scripts/_epg-end"
) -> Optional[ET.ElementTree]:
    """
    Fetch XML from a remote URL or local file.
    Supports .gz files and retries for remote requests.
    Logs full URL and returns an ElementTree or None on failure.
    """

    def parse_xml_bytes(xml_bytes: bytes) -> Optional[ET.ElementTree]:
        """Parse XML from bytes and return ElementTree, None if parse fails."""
        try:
            return ET.ElementTree(ET.fromstring(xml_bytes))
        except ET.ParseError as e:
            log_message(f"❌ Failed to parse XML: {e}", level="error")
            return None

    # Log full URL once
    # log_message(f"🔄 Fetching {index}/{total} - {url}")

    is_remote = url.startswith(("http://", "https://"))

    # -------------------------
    # REMOTE URL
    # -------------------------
    if is_remote:
        for attempt in range(1, retries + 1):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code != 200:
                    log_message(f"❌ HTTP {r.status_code} from {url}", level="error")
                    return None

                if not r.content:
                    log_message(f"⚠️ Empty response from {url}", level="warning")
                    return None

                # Handle gzip
                if url.endswith(".gz") or r.content[:2] == b'\x1f\x8b':
                    with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as gz:
                        xml_bytes = gz.read()
                    return parse_xml_bytes(xml_bytes)
                else:
                    return parse_xml_bytes(r.content)

            except requests.RequestException as e:
                log_message(f"⚠️  Attempt {attempt}/{retries} failed for {url}: {e}", level="warning")
                if attempt < retries:
                    log_message(f"⏳ Retrying in {delay_sec}s...", level="info")
                    time.sleep(delay_sec)

        log_message(f"❌ Failed to fetch {url} after {retries} attempts", level="error")
        return None

    # -------------------------
    # LOCAL FILE
    # -------------------------
    else:
        if not os.path.isabs(url):
            url = os.path.join(folder_path, url)

        if not os.path.exists(url):
            log_message(f"❌ Local file does not exist: {url}", level="error")
            return None

        try:
            if url.endswith(".gz"):
                with gzip.open(url, "rb") as f:
                    xml_bytes = f.read()
                if not xml_bytes:
                    log_message(f"⚠️ Empty local file: {url}", level="warning")
                    return None
                return parse_xml_bytes(xml_bytes)
            else:
                return ET.parse(url)
        except ET.ParseError as e:
            log_message(f"❌ Failed to parse local XML file {url}: {e}", level="error")
            return None
        except Exception as e:
            log_message(f"❌ Error reading local file {url}: {e}", level="error")
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

# Assuming XMLTV_URLS contains your XML URLs (remote or local)
folder_path = "scripts/_epg-end"  # Update to your folder path

########## Step 14: XML Elements to single line

from xml.sax.saxutils import escape  # Escape special XML characters (& < > etc.)

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


########## Step 14b: M3U tvg-id helpers ##########

def get_tvg_ids_from_m3u(m3u_file):
    """
    Read a .m3u file and return a set of all tvg-ids found.
    Ignores empty or malformed lines.
    """
    tvg_ids = set()
    with open(m3u_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r'tvg-id="([^"]+)"', line)
            if match:
                tvg_ids.add(match.group(1).strip())
    logger.info(f"✅ Found {len(tvg_ids)} TVG IDs in {m3u_file}")
    return tvg_ids


def filter_epg_by_tvg_ids(root, tvg_ids):
    """
    Keep only channels and programmes whose TVG IDs match the provided set.
    """
    filtered_root = ET.Element(root.tag, root.attrib)
    valid_channels = set()

    # Filter channels
    for channel in root.findall("channel"):
        cid = channel.get("id", "").strip()
        # TVG ID may be in an attribute or child element
        tvg_id = (channel.get("tvg-id") or channel.findtext("tvg-id") or "").strip()

        if tvg_id in tvg_ids:
            filtered_root.append(channel)
            valid_channels.add(cid)

    # Filter programmes
    for prog in root.findall("programme"):
        prog_channel = prog.get("channel", "").strip()
        if prog_channel in valid_channels:
            filtered_root.append(prog)

    return filtered_root



########## Step 15: Save the merged EPG file and log success
try:
    # merged_tree = ET.ElementTree(merged_root)
    # merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)
    write_epg_single_line(merged_root, save_path)
    # logger.info(f"✅ EPG file saved to {save_path}")
    
except Exception as e:
    # Log error if save fails
    error_message = f"❌Failed to save EPG file - Error: {e}"
    logging.error(error_message)
    logger.info(error_message)
  

  

########## Step 16: __main__ block (TVG-ID filtered) ##########
if __name__ == "__main__":
    # -------------------------
    # Paths and directories
    # -------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    epg_end_dir = os.path.join(script_dir, "_epg-end")
    os.makedirs(epg_end_dir, exist_ok=True)

    save_path = os.path.join(script_dir, "www", "epg.xml")
    ensure_permissions(save_path)

    # Load TVG IDs from M3U
    m3u_file = os.path.join(script_dir, "..", "list", "list.m3u")
    tvg_ids = get_tvg_ids_from_m3u(m3u_file) if os.path.exists(m3u_file) else set()
    logger.info(f"📋 Loaded {len(tvg_ids)} TVG IDs from M3U" if tvg_ids else "⚠️ No TVG IDs loaded")

    # -------------------------
    # Step 1: Build fast EPG
    # -------------------------
    if run_build_fast_epg:
        logger.info("▶️ Building fast-epg-end.xml (TVG filtered)...")
        try:
            build_fast_epg(tvg_ids)
        except Exception as e:
            logger.error(f"❌ Failed to build fast-epg-end.xml: {e}")

    # -------------------------
    # Step 2: Build dummy EPG
    # -------------------------
    if run_build_dummy_epg:
        logger.info("▶️ Running build_dummy_epg.py...")
        try:
            subprocess.run([sys.executable, BUILD_DUMMY_EPG_SCRIPT], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ build_dummy_epg.py failed: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error running build_dummy_epg.py: {e}")

    # -------------------------
    # Step 3: Collect all EPG files in _epg-end
    # -------------------------
    epg_files = [
        os.path.join(epg_end_dir, f)
        for f in os.listdir(epg_end_dir)
        if not f.startswith("._") and (f.endswith(".xml") or f.endswith(".gz"))
    ]
    logger.info(f"📂 Found {len(epg_files)} EPG files in _epg-end: {epg_files}")

    if not epg_files:
        logger.error("❌ No EPG files were generated. Check build_fast_epg and build_dummy_epg.py")
        sys.exit(1)

    # -------------------------
    # Step 4: Merge all EPG files (with TVG filtering)
    # -------------------------
    logger.info(f"🔄 Merging {len(epg_files)} EPG files...")
    try:
        build_data(epg_files, save_path, tvg_ids=tvg_ids, folder_path=epg_end_dir)
    except Exception as e:
        logger.error(f"❌ Failed to merge EPG files: {e}")
        sys.exit(1)

    # -------------------------
    # Step 5: Final sanity check
    # -------------------------
    try:
        tree = ET.parse(save_path)
        root = tree.getroot()
        if not root.findall("channel"):
            logger.warning("⚠️ epg.xml has no channels after merge")
        if not root.findall("programme"):
            logger.warning("⚠️ epg.xml has no programmes after merge")
    except Exception as e:
        logger.error(f"❌ Failed to read final epg.xml for sanity check: {e}")

    logger.info(f"✅ epg.xml successfully created at: {save_path}")
