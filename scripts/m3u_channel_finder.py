# python3 m3u_channel_finder.py

import os
import glob
import re
import sys
import time
import shutil
import subprocess
import warnings
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import NotOpenSSLWarning

# Silence the LibreSSL Warning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
import requests

# ---------------------
# CONFIGURATION
# ---------------------
M3U_FOLDERS = [
    "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched",
    "/Volumes/Kyle4tb1223/Documents/Github/tv/list/Active2"
]
OUTPUT_FOLDER = "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched/Channels"

GROUP_KEYWORDS = [] # 1. Standalone search purely for the group-title tag
KEYWORDS = ["Slice"] # 2. Keywords to search within the channel name / meta
SERVER_KEYWORDS = []

KEYWORDS_MAP = {
    "South Africa": ["South Africa", "ZA", "SA", "SouthAfrica"],
    "USA": ["USA", "US", "United States"],
    "Canada": ["Canada", "CA", "CAN"],
    "UK": ["UK", "United Kingdom", "Great Britain", "BBC"],
    "HBO": ["HBO"],
    "Food": ["Food", "Cooking", "Kitchen"]
}

STRICT_MATCH = False # True / False    

# 🛑 BLOCKLIST CONFIGURATION
USE_BLOCKLIST = True # True / False   
BLOCKLIST = ["S01", "E01", "SEASON", "EP.", ".MP4", ".MKV", ".AVI", ".MOV"]

# 🔒 PERMANENT BLOCKLIST (Always active)
PERMANENT_BLOCKLIST = ["RADIO", "mycamtv", "adultiptv", "Anal", "Gay", "(2002)", "WrestleMania", "Return of Xander Cage", "State of the Union", "Reactivated", "Reactivado", "The Next Level", "Madonna"]

ENABLE_VPN_TOGGLE = True # True / False 

FILTER_VIDEO_LESS = True  # True / False (True Filters out Radio Feeds)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# 🏷️ TAG EXTRACTION TOGGLES
KEEP_TVG_ID = True # True / False   

# ---------------------
# HELPER FUNCTIONS
# ---------------------
def is_channel_live(url):
    """
    Two-Phase channel stream verification module with toggle support:
    Phase 1: Validates server connectivity via fast HTTP response headers.
    Phase 2 (Optional): Verifies that an active video track exists via ffprobe.
    """
    if not url or url.startswith("#"):
        return False
        
    custom_headers = {
        "User-Agent": "TiviMate/5.0.4 (Linux; Android 11)",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    # 1️⃣ PHASE 1: HTTP Fast-Response Connectivity Check
    try:
        response = requests.get(
            url, 
            stream=True, 
            timeout=5, 
            headers=custom_headers,
            allow_redirects=True
        )
        is_accessible = response.status_code in (200, 206)
        response.close()
        
        if not is_accessible:
            return False
            
    except Exception:
        return False

    # 2️⃣ Bypasses Phase 2 entirely if deep validation is toggled off
    if not FILTER_VIDEO_LESS:
        return True

    # 3️⃣ PHASE 2: True Video Track Payload Inspection (Blocks audio-only / dead data loops)
    try:
        result = subprocess.run(
            [
                "ffprobe", 
                "-v", "error", 
                "-user_agent", custom_headers["User-Agent"],
                "-select_streams", "v",                      # Track video containers exclusively
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                url
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=10
        )
        
        if result.returncode == 0 and b"video" in result.stdout:
            return True
            
        return False
    except (subprocess.TimeoutExpired, Exception):
        return False


def process_channel(candidate_dict):
    """Bridge runner worker target for the concurrent ThreadPoolExecutor map."""
    if not candidate_dict or 'url' not in candidate_dict:
        return None
        
    url = candidate_dict.get('url')
    if is_channel_live(url):
        return candidate_dict  
        
    return None


# ---------------------
# PARSING & MATCHING ENGINE
# ---------------------
def run_keyword_search():
    """Scans folders, batches extraction targets, and loops validation queues sequentially."""
    m3u_files = []
    for folder in M3U_FOLDERS:
        if os.path.isdir(folder):
            folder_files = glob.glob(os.path.join(folder, "*.m3u")) + glob.glob(os.path.join(folder, "*.m3u8"))
            m3u_files.extend(folder_files)
            print(f"📂 Found {len(folder_files)} playlists in: {folder}")

    if not m3u_files:
        print("Error: No source .m3u or .m3u8 files located in configured directories.")
        return

    # Fallback default target if your primary keywords tracking array is blank
    targets = KEYWORDS if KEYWORDS else ["Channels"]
    print(f"DEBUG: All targets found: {targets}\n")

    compiled_blocklist = [item.lower() for item in (BLOCKLIST + PERMANENT_BLOCKLIST)]
    datestamp = datetime.now().strftime("%Y-%m-%d")

    # Loop through each individual keyword sequentially as a separate run target
    for target in targets:
        print(f"🎯 TARGET: {target}")
        print("Parsing local files...")
        
        candidates = []
        target_lower = target.lower()

        for file_path in m3u_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue

            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF"):
                    url = lines[i + 1].strip() if (i + 1 < len(lines) and not lines[i + 1].startswith("#")) else None
                    if not url:
                        continue

                    line_lower = line.lower()

                    # Drop blocklist violations instantly
                    if any(bad in line_lower or bad in url.lower() for bad in compiled_blocklist):
                        continue

                    # Search matching constraints
                    matched = False
                    if target == "Channels":  # Check everything if default fallback is active
                        matched = True
                    else:
                        if STRICT_MATCH:
                            matched = bool(re.search(rf"\b{re.escape(target_lower)}\b", line_lower))
                        else:
                            matched = target_lower in line_lower

                    if matched:
                        candidates.append({'extinf': line.strip(), 'url': url})

        # Deduplicate streams matching identical streaming links
        unique_candidates = {c['url']: c for c in candidates}.values()
        total_found = len(unique_candidates)
        print(f"Found {total_found} keyword matches. Starting live check...")

        if total_found == 0:
            print(f"⚠️ No matches found for target: {target}\n")
            continue

        # Execute parallel network processing pools
        live_channels = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(process_channel, unique_candidates))
            live_channels = [r for r in results if r is not None]

        print(f"Progress: {total_found}/{total_found} channels verified.")

        # Save and write structured out streams using your preferred formatting standard
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        file_prefix = re.sub(r'[^\w\-_]', '', target.replace(" ", "_"))
        output_file_name = f"{file_prefix}-{datestamp}.m3u"
        output_path = os.path.join(OUTPUT_FOLDER, output_file_name)

        try:
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write("#EXTM3U\n")
                for ch in live_channels:
                    out_f.write(f"{ch['extinf']}\n")
                    out_f.write(f"{ch['url']}\n")
            print(f"✅ Saved {len(live_channels)} live channels to {output_path}\n")
        except Exception as e:
            print(f"❌ Error writing output target file: {e}\n")

def check_ffprobe():
    """Validates availability of local decoding tool dependencies if toggle is active."""
    if not FILTER_VIDEO_LESS:
        print("Skipping ffprobe system path analysis (Deep Video Check is currently disabled).\n")
        return

    if shutil.which("ffprobe") is None:
        print("WARNING: 'ffprobe' execution binary was not located in system search environments.")
        print("Install ffmpeg via Homebrew ('brew install ffmpeg') to filter videoless channels properly.\n")
    else:
        print(f"Active stream profile processor mapped at: {shutil.which('ffprobe')}\n")


# ---------------------
# MAIN RUNTIME BLOCK
# ---------------------
if __name__ == "__main__":
    print("Initializing environment dependencies...", flush=True)
    check_ffprobe()
    
    print("M3U Channel Finder active. Starting file batch data ingestion processing...\n", flush=True)
    run_keyword_search()
    
    print("\nBatch data map ingestion processing complete.", flush=True)