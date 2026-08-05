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
KEYWORDS = ["CTV"] # 2. Keywords to search within the channel name / meta
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
# ENVIRONMENT DEPS UTILITY <-- PLACE IT RIGHT HERE
# ---------------------
def check_ffprobe():
    """Validates availability of local decoding tool dependencies if toggle is active."""
    if not FILTER_VIDEO_LESS:
        print("ℹ️ Skipping ffprobe system path analysis (Deep Video Check is currently disabled).\n", flush=True)
        return

    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path is None:
        print("❌ WARNING: 'ffprobe' execution binary was not located in system search environments.", flush=True)
        print("   Install ffmpeg via Homebrew ('brew install ffmpeg') to filter videoless channels properly.\n", flush=True)
    else:
        print(f"✅ Active stream profile processor mapped at: {ffprobe_path}\n", flush=True)


# ---------------------
# HELPER FUNCTIONS
# ---------------------
def is_channel_live(url):
    if not url or url.startswith("#"):
        return False
        
    custom_headers = {
        "User-Agent": "TiviMate/5.0.4 (Linux; Android 11)",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    # 1️⃣ PHASE 1: HTTP Fast-Response Connectivity Check (Fully Silenced)
    try:
        # Suppress internal thread logging leaks by creating a session context
        with requests.Session() as session:
            # Lower-level loggers can sometimes still push warning text to stderr
            import logging
            logging.getLogger("urllib3").setLevel(logging.ERROR)
            
            response = session.get(
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

    # 3️⃣ PHASE 2: True Video Track Payload Inspection (Completely Muted)
    try:
        result = subprocess.run(
            [
                "ffprobe", 
                "-v", "quiet",                               # 🌟 Mutes internal ffprobe engine logs
                "-user_agent", custom_headers["User-Agent"],
                "-select_streams", "v",                      
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                url
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,                       # 🌟 Safely discards system streaming errors
            timeout=10
        )
        
        if result.returncode == 0 and b"video" in result.stdout:
            return True
            
        return False
    except (subprocess.TimeoutExpired, Exception):
        return False



def process_channel(candidate_dict):
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
    m3u_files = []
    for folder in M3U_FOLDERS:
        if os.path.isdir(folder):
            folder_files = glob.glob(os.path.join(folder, "*.m3u")) + glob.glob(os.path.join(folder, "*.m3u8"))
            m3u_files.extend(folder_files)
            print(f"📂 Found {len(folder_files)} playlists in: {folder}")

    if not m3u_files:
        print("Error: No source .m3u or .m3u8 files located in configured directories.")
        return

    # Prioritise GROUP_KEYWORDS, then KEYWORDS, then fallback
    is_group_search = False
    if GROUP_KEYWORDS:
        targets = GROUP_KEYWORDS
        is_group_search = True
        print("🔍 Mode: Group-Title Extraction")
    elif KEYWORDS:
        targets = KEYWORDS
        print("🔍 Mode: Channel Name Keyword Extraction")
    else:
        targets = ["Channels"]
        print("🔍 Mode: Global Fallback Extraction")

    print(f"DEBUG: All targets found: {targets}\n")

    compiled_blocklist = [item.lower() for item in (BLOCKLIST + PERMANENT_BLOCKLIST)]
    datestamp = datetime.now().strftime("%Y-%m-%d")

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

                    if any(bad in line_lower or bad in url.lower() for bad in compiled_blocklist):
                        continue

                    matched = False
                    
                    # Explicit group-title string matching
                    if is_group_search:
                        group_match = re.search(r'group-title="([^"]+)"', line, re.IGNORECASE)
                        if group_match:
                            group_value_lower = group_match.group(1).lower()
                            if STRICT_MATCH:
                                pattern = rf"(?:^|[^a-zA-Z0-9]){re.escape(target_lower)}(?:$|[^a-zA-Z0-9])"
                                matched = bool(re.search(pattern, group_value_lower))
                            else:
                                matched = target_lower in group_value_lower
                    else:
                        # Standard Channel Name / Global Fallback Match Logic
                        if target == "Channels":  
                            matched = True
                        else:
                            if STRICT_MATCH:
                                pattern = rf"(?:^|[^a-zA-Z0-9]){re.escape(target_lower)}(?:$|[^a-zA-Z0-9])"
                                matched = bool(re.search(pattern, line_lower))
                            else:
                                matched = target_lower in line_lower

                    if matched:
                        domain_match = re.search(r'https?://([^:/\s]+)', url)
                        if domain_match:
                            domain = domain_match.group(1)
                            server_name = domain.split('.')[0]
                            modified_line = f"{line.strip()} ({server_name})"
                        else:
                            modified_line = line.strip()

                        candidates.append({'extinf': modified_line, 'url': url})

        # Safeguard dictionary conversion to static array list
        unique_candidates = list({c['url']: c for c in candidates}.values())
        total_found = len(unique_candidates)
        print(f"Found {total_found} matches. Starting live check...")

        if total_found == 0:
            print(f"⚠️ No matches found for target: {target}\n")
            continue
            
        # 🌟 LIVE CHECK PROCESSING SYSTEM (IDE-COMPATIBLE STATS WRITER)
        live_channels = []
        max_workers = 30  
        
        print(f"Checking {total_found} streams in parallel using {max_workers} threads...", flush=True)
        
        checked_count = 0
        # Print a progress line every N channels to prevent terminal scrolling
        print_interval = max(1, total_found // 20)  # Updates roughly 20 times total (every 5%)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(process_channel, unique_candidates)
            
            for res in results:
                checked_count += 1
                if res:
                    live_channels.append(res)
                
                # Only print a normal line when hitting an interval step, or on the final item
                if checked_count % print_interval == 0 or checked_count == total_found:
                    percent = (checked_count / total_found) * 100
                    print(f" -> [{percent:5.1f}%] Processed {checked_count}/{total_found} channels... (Live found: {len(live_channels)})", flush=True)

        print("Verification complete.")

        # 🌟 STORAGE ENGINE
        if live_channels:
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            # Remove any dangerous punctuation from target to prevent file path generation errors
            safe_target_name = "".join([c for c in target if c.isalnum() or c == ' ']).rstrip()
            output_file = os.path.join(OUTPUT_FOLDER, f"{safe_target_name}_{datestamp}.m3u")
            
            try:
                with open(output_file, 'w', encoding='utf-8') as out_f:
                    out_f.write("#EXTM3U\n")
                    for channel in live_channels:
                        out_f.write(f"{channel['extinf']}\n")
                        out_f.write(f"{channel['url']}\n")
                print(f"💾 File successfully saved to: {output_file}\n", flush=True)
            except Exception as e:
                print(f"❌ Error writing output file: {e}\n", flush=True)
        else:
            print("⚠️ No live streams survived verification. Skipping file save.\n", flush=True)


# ---------------------
# MAIN RUNTIME BLOCK
# ---------------------
if __name__ == "__main__":
    print("Initializing environment dependencies...", flush=True)
    check_ffprobe()
    
    print("M3U Channel Finder active. Starting file batch data ingestion processing...\n", flush=True)
    run_keyword_search()
    
    print("\nBatch data map ingestion processing complete.", flush=True)