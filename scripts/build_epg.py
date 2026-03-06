import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from io import BytesIO
import os
import time
import re
import gzip
from xml.sax.saxutils import escape
from datetime import datetime
from typing import Set
from build_channels_list import CHANNELS # Channels @ build_channels_list.py


# build_epg.py Mar 6 1154 a
# python3 -m venv myenv
# source myenv/bin/activate
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/build_epg.py


# Base directory relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Output path inside scripts/_epg-end
OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml")
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# XML URLs to fetch
XMLTV_URLS = [
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://i.mjh.nz/Roku/all.xml",
    "https://raw.githubusercontent.com/acidjesuz/EPGTalk/refs/heads/master/guide.xml",
    "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CY1.xml.gz",
    "https://i.mjh.nz/SamsungTVPlus/all.xml"
]

# Optional: only include these channels (empty = all channels)


# User-Agent header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}


# -------------------------
# PROCESS
# -------------------------
new_root = ET.Element("tv")
seen_channels = {}
programmes_to_add = []

for url in XMLTV_URLS:
    print(f"⬇️ Fetching {url}")

    # Retry logic
    r = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < 2:
                print("⏳ Retrying in 5 seconds...")
                time.sleep(5)

    if not r:
        print(f"❌ Skipping {url} after 3 failed attempts")
        continue

    # Parse XML safely (.xml or .xml.gz)
    content = r.content
    if content[:2] == b'\x1f\x8b':  # gzip magic bytes
        with gzip.open(BytesIO(content), "rt", encoding="utf-8", errors="ignore") as f:
            root = ET.parse(f).getroot()
    else:
        root = ET.parse(BytesIO(content)).getroot()

    # ---- Channels ----
    for channel in root.findall("channel"):
        cid = channel.get("id")
        if not cid or (CHANNELS and cid not in CHANNELS) or cid in seen_channels:
            continue

        # Remove <icon> from the channel before storing
        for icon in channel.findall("icon"):
            channel.remove(icon)

        # Add <url> tag pointing to the source XML
        url_elem = ET.Element("url")
        url_elem.text = url  # source URL
        channel.append(url_elem)

        seen_channels[cid] = channel  # store cleaned element

    # ---- Programmes ----
    for programme in root.findall("programme"):
        cid = programme.get("channel")
        if not cid or (CHANNELS and cid not in CHANNELS):
            continue
        programmes_to_add.append(programme)

# -------------------------
# SORT AND BUILD XML
# -------------------------
# Sort channels alphabetically by name
sorted_channel_ids = sorted(
    seen_channels.keys(),
    key=lambda cid: CHANNELS.get(cid, cid).lower()
)

# Append channels first
for cid in sorted_channel_ids:
    new_root.append(seen_channels[cid])

# Then append all programmes
for prog in programmes_to_add:
    new_root.append(prog)

# -------------------------
# Function to pretty-print XML
# -------------------------
# -------------------------
# Step 1: Build merged_root
# -------------------------
merged_root = ET.Element("tv")

# Add channels
for cid in sorted_channel_ids:
    merged_root.append(seen_channels[cid])

# Add programmes
for prog in programmes_to_add:
    merged_root.append(prog)

# -------------------------
# Step 2: Pretty-print XML
# -------------------------
def build_flat_xml(channels, programmes):
    """
    Build single-line XML string:
    - One line per channel
    - One line per programme
    - Removes <icon>, keeps <url> if present
    """
    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>', '<tv>']

    # Channels
    for channel in channels:
        cid = channel.get("id")
        display_name = escape(channel.findtext("display-name", default=""))
        url_elem = channel.find("url")
        url = escape(url_elem.text) if url_elem is not None and url_elem.text else ""

        line = f'<channel id="{cid}"><display-name>{display_name}</display-name>'
        if url:
            line += f'<url>{url}</url>'
        line += '</channel>'
        xml_lines.append(line)

    # Programmes
    for prog in programmes:
        attribs = " ".join(f'{k}="{v}"' for k, v in prog.attrib.items())

        children_str = ""
        for child in prog:
            tag = child.tag
            text = escape(child.text or "")
            children_str += f"<{tag}>{text}</{tag}>"

        line = f'<programme {attribs}>{children_str}</programme>'
        xml_lines.append(line)

    xml_lines.append("</tv>")

    return "\n".join(xml_lines)

# Example usage:
flat_xml = build_flat_xml(
    [seen_channels[cid] for cid in sorted_channel_ids],
    programmes_to_add
)

with open(OUTPUT_XML, "w", encoding="utf-8") as f:
    f.write(flat_xml)

print("✅ Fast EPG XML saved with one-line channels and one-line programmes")

# -------------------------
# SUMMARY
# -------------------------
print(f"✅ Generated {OUTPUT_XML}")
print(f"📺 Total channels added: {len(seen_channels)}")
print("Channels and number of programs:")


# Current time for comparison
now = datetime.now()

# 1️⃣ Count programmes per channel
program_counts = {cid: 0 for cid in seen_channels}

# Track seen programmes to avoid duplicates (channel + start + title)
seen_programmes: Set[tuple] = set()

# 2️⃣ Loop through all programmes
for prog in programmes_to_add:
    cid = prog.get("channel")
    if cid not in seen_channels:
        continue

    start_str = prog.get("start")  # e.g., '20260306053000 -0500'
    if not start_str:
        continue

    # 3️⃣ Filter for future programmes only
    # Convert first 14 digits (YYYYMMDDHHMMSS) to datetime
    start_dt = datetime.strptime(start_str[:14], "%Y%m%d%H%M%S")

    # Skip past programmes
    if start_dt < now:
        continue

    # Deduplicate using (channel, start, title)
    title = prog.findtext("title", default="").strip()
    # 4️⃣ Deduplicate programmes
    key = (cid, start_str[:14], title)
    if key in seen_programmes:
        continue

    seen_programmes.add(key)
    # 5️⃣ Increment the count
    program_counts[cid] += 1

# 6️⃣ Print a summary in alphabetical order
for cid in sorted_channel_ids:
    channel_name = CHANNELS.get(cid, "Unknown")
    print(f" - {channel_name} ({cid}): {program_counts[cid]} future programmes")