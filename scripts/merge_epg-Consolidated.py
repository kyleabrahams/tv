#!/usr/bin/env python3
"""
merge_epg.py
Feb 28, 2026 - Consolidated version
"""

import os
import sys
import gzip
import io
import time
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# ------------------------ CONFIG ------------------------
LOGGING_ENABLED = True
CI_SAFE = os.getenv("GITHUB_ACTIONS") == "true"
REPO_DIR = os.path.abspath(os.path.dirname(__file__))
EPG_START_DIR = os.path.join(REPO_DIR, "_epg-start")
EPG_END_DIR = os.path.join(REPO_DIR, "_epg-end")
WWW_DIR = os.path.join(REPO_DIR, "www")
SAVE_PATH = os.path.join(WWW_DIR, "epg.xml")
GZ_DIR = WWW_DIR
DELAY = 1 if CI_SAFE else 5

os.makedirs(EPG_END_DIR, exist_ok=True)
os.makedirs(WWW_DIR, exist_ok=True)

# ------------------------ LOGGING ------------------------
if LOGGING_ENABLED:
    log_file_path = os.path.join(WWW_DIR, "merge_epg.log")
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%b %d %Y %H:%M:%S"
    )
    logger = logging.getLogger(__name__)
else:
    logger = None

def log_message(level, message):
    if LOGGING_ENABLED and logger:
        if level.lower() == "info":
            logger.info(message)
        elif level.lower() == "error":
            logger.error(message)
    print(message)

# ------------------------ UTILS ------------------------
def ensure_permissions(file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    if not os.access(directory, os.W_OK):
        os.chmod(directory, 0o755)
    if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
        os.chmod(file_path, 0o644)

def pretty_print_xml(xml_tree):
    xml_str = ET.tostring(xml_tree.getroot(), encoding="utf-8", xml_declaration=True)
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent="  ")

def reorder_channels(root):
    channels = [el for el in root.findall('channel')]
    programmes = [el for el in root.findall('programme')]
    root.clear()
    for ch in channels: root.append(ch)
    for pg in programmes: root.append(pg)

# ------------------------ LOAD EPG URLs ------------------------
def load_epg_urls(file_path):
    urls = []
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        log_message("error", f"❌ Error reading {file_path}: {e}")
    return urls

def load_local_xml_files(directory):
    files = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                files.append(os.path.join(directory, filename))
    except Exception as e:
        log_message("error", f"❌ Error scanning {directory}: {e}")
    return files

# ------------------------ FETCH EPG ------------------------
def fetch_epg_data(url, index, total, folder_path=EPG_END_DIR, retries=3, delay=5):
    # Resolve local path
    local_path = os.path.join(folder_path, url) if not os.path.isabs(url) else url
    log_message("info", f"Fetching {index+1}/{total}: {local_path}")

    # Try local file first
    if os.path.exists(local_path):
        try:
            if local_path.endswith(".gz"):
                with gzip.open(local_path, 'rb') as f:
                    xml_content = f.read()
                tree = ET.ElementTree(ET.fromstring(xml_content))
            else:
                tree = ET.parse(local_path)
            return tree
        except ET.ParseError as e:
            log_message("error", f"❌ XML parse error: {local_path} → {e}")
            return None

    # If remote URL
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.content
                if url.endswith(".gz"):
                    with gzip.GzipFile(fileobj=io.BytesIO(content)) as gz:
                        content = gz.read()
                tree = ET.ElementTree(ET.fromstring(content))
                return tree
            else:
                log_message("error", f"❌ HTTP {response.status_code} for {url}")
        except requests.RequestException as e:
            log_message("error", f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)
            attempt += 1
    return None

# ------------------------ EXTRACT .GZ FILES ------------------------
def extract_gz_files(directory):
    extracted = []
    for filename in os.listdir(directory):
        if filename.endswith(".gz"):
            gz_path = os.path.join(directory, filename)
            xml_path = gz_path[:-3]
            try:
                with gzip.open(gz_path, 'rb') as f_in, open(xml_path, 'wb') as f_out:
                    f_out.write(f_in.read())
                log_message("info", f"Extracted {gz_path} → {xml_path}")
                extracted.append(xml_path)
            except Exception as e:
                log_message("error", f"❌ Failed to extract {gz_path}: {e}")
    return extracted

# ------------------------ MAIN MERGE ------------------------
def merge_epg():
    log_message("info", "Starting EPG merge process...")

    # Load URLs
    epg_urls_file = os.path.join(EPG_START_DIR, "epg_urls.txt")
    epg_urls = load_epg_urls(epg_urls_file)
    if not epg_urls:
        epg_urls = load_local_xml_files(EPG_END_DIR)
        log_message("info", f"No URLs found, scanning local XMLs: {EPG_END_DIR}")

    merged_root = ET.Element("tv")
    total_files = len(epg_urls)
    for idx, url in enumerate(epg_urls):
        tree = fetch_epg_data(url, idx, total_files)
        if tree:
            for el in tree.getroot():
                merged_root.append(el)
        time.sleep(DELAY)

    # Extract .gz files
    gz_files = extract_gz_files(GZ_DIR)
    for xml_file in gz_files:
        try:
            tree = ET.parse(xml_file)
            for el in tree.getroot():
                merged_root.append(el)
        except Exception as e:
            log_message("error", f"❌ Failed parsing {xml_file}: {e}")

    # Reorder channels to the top
    reorder_channels(merged_root)

    # Save merged XML
    ensure_permissions(SAVE_PATH)
    pretty_xml = pretty_print_xml(ET.ElementTree(merged_root))
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    log_message("info", f"✅ EPG file successfully saved to {SAVE_PATH}")

# ------------------------ RUN ------------------------
if __name__ == "__main__":
    merge_epg()
