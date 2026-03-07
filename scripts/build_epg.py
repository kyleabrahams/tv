# build_epg.py starts here

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Base directory relative to this script
OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml") # Output path inside scripts/_epg-end
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# XML URLs to fetch
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

# User-Agent header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}


# -------------------------
# Unified logging function
# -------------------------
def log_message(message: str):
    """
    Prints message to console with timestamp. No duplicates.
    """
    timestamp = datetime.now().strftime("%b %d %Y %H:%M:%S")
    print(f"{timestamp} - {message}")

# -------------------------
# Fetch and parse XML
# -------------------------
def fetch_xml(url: str, retries: int = 3, delay: int = 5) -> ET.Element:
    log_message(f"⬇️ Fetching {url}")
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            content = r.content

            # Handle .gz files
            if content[:2] == b'\x1f\x8b':  # gzip magic bytes
                with gzip.open(BytesIO(content), "rt", encoding="utf-8", errors="ignore") as f:
                    return ET.parse(f).getroot()
            else:
                return ET.parse(BytesIO(content)).getroot()

        except Exception as e:
            log_message(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                log_message(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)

    log_message(f"❌ Skipping {url} after {retries} failed attempts")
    return None

# -------------------------
# Build flat XML string
# -------------------------
def build_flat_xml(channels, programmes):
    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>', '<tv>']

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

    for prog in programmes:
        attribs = " ".join(f'{k}="{v}"' for k, v in prog.attrib.items())
        children_str = ""
        for child in prog:
            children_str += f"<{child.tag}>{escape(child.text or '')}</{child.tag}>"
        line = f'<programme {attribs}>{children_str}</programme>'
        xml_lines.append(line)

    xml_lines.append("</tv>")
    return "\n".join(xml_lines)

# -------------------------
# Main EPG builder
# -------------------------
def main():
    seen_channels = {}
    programmes_to_add = []

    # Fetch XML from all sources
    for url in XMLTV_URLS:
        root = fetch_xml(url)
        if root is None:
            continue

        # Channels
        for channel in root.findall("channel"):
            cid = channel.get("id")
            if not cid or (CHANNELS and cid not in CHANNELS) or cid in seen_channels:
                continue

            # Remove <icon>
            for icon in channel.findall("icon"):
                channel.remove(icon)

            # Add <url>
            url_elem = ET.Element("url")
            url_elem.text = url
            channel.append(url_elem)

            seen_channels[cid] = channel

        # Programmes
        for prog in root.findall("programme"):
            cid = prog.get("channel")
            if not cid or (CHANNELS and cid not in CHANNELS):
                continue
            programmes_to_add.append(prog)

    # Sort channels alphabetically
    sorted_channel_ids = sorted(
        seen_channels.keys(),
        key=lambda cid: CHANNELS.get(cid, cid).lower()
    )

    # Build merged_root
    merged_root = ET.Element("tv")
    for cid in sorted_channel_ids:
        merged_root.append(seen_channels[cid])
    for prog in programmes_to_add:
        merged_root.append(prog)

    # Save flat XML
    flat_xml = build_flat_xml([seen_channels[cid] for cid in sorted_channel_ids], programmes_to_add)
    with open(OUTPUT_XML, "w", encoding="utf-8") as f:
        f.write(flat_xml)

    log_message(f"✅Fast EPG XML saved: {OUTPUT_XML}")
    log_message(f"📺 Total channels: {len(seen_channels)}")

    # Count programmes per channel (future only, deduplicated)
    now = datetime.now()
    program_counts = {cid: 0 for cid in seen_channels}
    seen_programmes: Set[tuple] = set()

    for prog in programmes_to_add:
        cid = prog.get("channel")
        if cid not in seen_channels:
            continue
        start_str = prog.get("start")
        if not start_str:
            continue
        start_dt = datetime.strptime(start_str[:14], "%Y%m%d%H%M%S")
        if start_dt < now:
            continue

        key = (cid, start_str[:14], prog.findtext("title", "").strip())
        if key in seen_programmes:
            continue

        seen_programmes.add(key)
        program_counts[cid] += 1

    for cid in sorted_channel_ids:
        log_message(f" - {CHANNELS.get(cid, 'Unknown')} ({cid}): {program_counts[cid]} future programmes")


if __name__ == "__main__":
    main()

