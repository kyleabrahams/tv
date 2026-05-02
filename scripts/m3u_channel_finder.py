# python3 m3u_channel_finder.py

import os
import glob
import re
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Silence the LibreSSL Warning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
import requests

# ---------------------
# CONFIGURATION
# ---------------------
M3U_FOLDER = "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched"
OUTPUT_FOLDER = "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched/Channels"

KEYWORDS = ["Redlight"]

KEYWORDS_MAP = {
    "South Africa": ["South Africa", "ZA", "SA", "SouthAfrica"],
    "USA": ["USA", "US", "United States"],
    "Canada": ["Canada", "CA", "CAN"],
    "UK": ["UK", "United Kingdom", "Great Britain", "BBC"],
    "HBO": ["HBO"],
    "Food": ["Food", "Cooking", "Kitchen"]
}

STRICT_MATCH = True  
BLOCKLIST = ["S01", "E01", "SEASON", "RADIO", "EP.", ".MP4", ".MKV", ".AVI", ".MOV"]

# ---------------------
# 🛡️ VPN CONFIGURATION
# ---------------------
# ⚠️ Turn on Proton VPN in your desktop app before running!
ENABLE_VPN_TOGGLE = False  

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# ---------------------
# HELPER FUNCTIONS
# ---------------------
def is_channel_live(url):
    """Sends a fast request to see if the stream is online."""
    try:
        response = requests.get(url, stream=True, timeout=3, headers=HEADERS)
        return response.status_code == 200
    except:
        return False

def process_channel(args):
    """Worker function for threads to process and check a channel."""
    clean_header, url = args
    if is_channel_live(url):
        return f"{clean_header}\n{url}\n"
    return None

# ---------------------
# MAIN RUNNER
# ---------------------
def run_keyword_search():
    date_str = datetime.now().strftime('%Y-%m-%d')
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    EPISODE_PATTERN = re.compile(r's\d{1,3}e\d{1,3}', re.IGNORECASE)
    
    files = glob.glob(os.path.join(M3U_FOLDER, "*.m3u"))
    if not files:
        print(f"❌ No .m3u files found in {M3U_FOLDER}")
        return

    for target_k in KEYWORDS:
        print(f"\n🎯 TARGET: {target_k}")
        found_urls = set()
        candidates = []  
        search_terms = KEYWORDS_MAP.get(target_k, [target_k])

        print("Parsing local files...")
        for f_path in files:
            try:
                with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                blocks = content.split("#EXTINF")
                for block in blocks[1:]:
                    lines = block.strip().split("\n")
                    header = lines[0]
                    
                    url = ""
                    for potential_url in lines[1:]:
                        if potential_url.strip() and not potential_url.startswith("#"):
                            url = potential_url.strip()
                            break
                    if not url or url in found_urls: 
                        continue
                    
                    # EXTRACT METADATA
                    group_match = re.search(r'group-title="([^"]+)"', header)
                    group_name = group_match.group(1).strip() if group_match else "Other"
                    
                    name_match = re.search(r',([^,]*)$', header)
                    channel_name = name_match.group(1).strip() if name_match else "Unknown"
                    
                    server_match = re.search(r'https?://([^./:]+)', url)
                    server_prefix = server_match.group(1).upper() if server_match else "SERVER"
                    
                    # 🖼️ EXTRACT TVG-LOGO (if it exists)
                    logo_match = re.search(r'tvg-logo="([^"]+)"', header)
                    logo_str = f' tvg-logo="{logo_match.group(1)}"' if logo_match else ""
                    
                    # Inject the logo back into the clean tag block
                    clean_header = f'#EXTINF:-1 group-title="{group_name}"{logo_str},{server_prefix}-{channel_name}'
                    full_meta = header.upper()
                    
                    # BLOCKLIST CHECK
                    if any(b.upper() in full_meta for b in BLOCKLIST) or \
                       any(b.upper() in url.upper() for b in BLOCKLIST) or \
                       EPISODE_PATTERN.search(full_meta):
                        continue

                    # KEYWORD CHECK
                    for var in search_terms:
                        if var.upper() in full_meta:
                            candidates.append((clean_header, url))
                            found_urls.add(url)
                            break
            except: 
                continue

        print(f"Found {len(candidates)} keyword matches. Starting live check...")

        live_content = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(process_channel, candidates)
            
            for i, result in enumerate(results):
                if result:
                    live_content.append(result)
                sys.stdout.write(f"\rProgress: {i+1}/{len(candidates)} channels verified.")
                sys.stdout.flush()

        if live_content:
            safe_name = target_k.replace(" ", "_")
            out_filename = f"{safe_name}-{date_str}.m3u"
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            
            def sort_by_actual_name(entry):
                try:
                    after_comma = entry.split(",")[-1]
                    actual_name = after_comma.split("-", 1)[-1]
                    return actual_name.strip().lower()
                except:
                    return entry.lower()

            sorted_content = sorted(live_content, key=sort_by_actual_name)
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n" + "".join(sorted_content))
            print(f"\n📂 Created: {out_filename} ({len(live_content)} LIVE channels generated!)")

if __name__ == "__main__":
    run_keyword_search()
