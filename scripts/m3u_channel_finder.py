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

KEYWORDS = ["XXX"]

KEYWORDS_MAP = {
    "South Africa": ["South Africa", "ZA", "SA", "SouthAfrica"],
    "USA": ["USA", "US", "United States"],
    "Canada": ["Canada", "CA", "CAN"],
    "UK": ["UK", "United Kingdom", "Great Britain", "BBC"],
    "HBO": ["HBO"],
    "Food": ["Food", "Cooking", "Kitchen"]
}

STRICT_MATCH = True  

# 🛑 BLOCKLIST CONFIGURATION
USE_BLOCKLIST = False  
BLOCKLIST = ["S01", "E01", "SEASON", "EP.", ".MP4", ".MKV", ".AVI", ".MOV"]

# 🔒 PERMANENT BLOCKLIST (Always active)
PERMANENT_BLOCKLIST = ["RADIO", "Anal", "Gay", "(2002)" "WrestleMania", "Return of Xander Cage", "State of the Union", "Reactivated", "Reactivado", "The Next Level", "Madonna"]

# ---------------------
# 🛡️ VPN CONFIGURATION
# ---------------------
ENABLE_VPN_TOGGLE = True  

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# 🏷️ TAG EXTRACTION TOGGLES
KEEP_TVG_ID = True  

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
    candidate = args
    if is_channel_live(candidate['url']):
        return candidate
    return None

# ---------------------
# MAIN RUNNER
# ---------------------
def run_keyword_search():
    date_str = datetime.now().strftime('%Y-%m-%d')
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    EPISODE_PATTERN = re.compile(r's\d{1,3}e\d{1,3}', re.IGNORECASE)
    VIDEO_EXTENSIONS = (".MP4", ".MKV", ".AVI", ".MOV")
    
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
                    
                    # EXTRACT TVG-ID
                    id_str = ""
                    if KEEP_TVG_ID:
                        id_match = re.search(r'tvg-id="([^"]+)"', header)
                        if id_match:
                            id_str = f' tvg-id="{id_match.group(1)}"'
                    
                    # EXTRACT TVG-LOGO
                    logo_match = re.search(r'tvg-logo="([^"]+)"', header)
                    logo_str = f' tvg-logo="{logo_match.group(1)}"' if logo_match else ""
                    
                    # Create header (Places lowercase server prefix at the very end)
                    clean_header = f'#EXTINF:-1 group-title="{group_name}"{id_str}{logo_str},{channel_name} {server_prefix.lower()}.'
                    
                    # Strip logo URL
                    meta_for_search = re.sub(r'tvg-logo="[^"]*"', '', header).upper()
                    
                    # 🛑 1. Permanent Blocklist (Excludes Madonna, Wrestlemania, etc.)
                    if any(b.upper() in meta_for_search for b in PERMANENT_BLOCKLIST) or \
                       any(b.upper() in url.upper() for b in PERMANENT_BLOCKLIST):
                        continue
                    
                    if USE_BLOCKLIST:
                        if any(b.upper() in meta_for_search for b in BLOCKLIST) or \
                           any(b.upper() in url.upper() for b in BLOCKLIST) or \
                           EPISODE_PATTERN.search(meta_for_search):
                            continue

                    # 🎯 2. KEYWORD CHECK (Modified for strict word boundaries)
                    for var in search_terms:
                        if STRICT_MATCH:
                            pattern = re.compile(rf'\b{re.escape(var.upper())}\b')
                            is_match = pattern.search(meta_for_search)
                        else:
                            is_match = var.upper() in meta_for_search

                        if is_match:
                            candidates.append({
                                'name': channel_name, 
                                'header': clean_header, 
                                'url': url
                            })
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
            
            def sort_by_actual_name(candidate):
                name = candidate['name']
                is_video = candidate['url'].upper().endswith(VIDEO_EXTENSIONS)
                
                # False puts live channels up top, True drops .mp4s to the absolute bottom.
                # It then sorts alphabetically by the true channel name.
                return (is_video, name.lower())

            sorted_content = sorted(live_content, key=sort_by_actual_name)
            
            final_output_lines = []
            for item in sorted_content:
                final_output_lines.append(f"{item['header']}\n{item['url']}\n")
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n" + "".join(final_output_lines))
            print(f"\n📂 Created: {out_filename} ({len(live_content)} LIVE channels generated!)")

if __name__ == "__main__":
    run_keyword_search()
