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

GROUP_KEYWORDS = [] # 1. Standalone search purely for the group-title tag
KEYWORDS = ["WUTV"] # 2. Keywords to search within the channel name / meta
SERVER_KEYWORDS = []

KEYWORDS_MAP = {
    "South Africa": ["South Africa", "ZA", "SA", "SouthAfrica"],
    "USA": ["USA", "US", "United States"],
    "Canada": ["Canada", "CA", "CAN"],
    "UK": ["UK", "United Kingdom", "Great Britain", "BBC"],
    "HBO": ["HBO"],
    "Food": ["Food", "Cooking", "Kitchen"]
}

STRICT_MATCH = False  

# 🛑 BLOCKLIST CONFIGURATION
USE_BLOCKLIST = False  
BLOCKLIST = ["S01", "E01", "SEASON", "EP.", ".MP4", ".MKV", ".AVI", ".MOV"]

# 🔒 PERMANENT BLOCKLIST (Always active)
PERMANENT_BLOCKLIST = ["RADIO", "mycamtv", "adultiptv", "Anal", "Gay", "(2002)", "WrestleMania", "Return of Xander Cage", "State of the Union", "Reactivated", "Reactivado", "The Next Level", "Madonna"]

# ---------------------
# 🛡️ VPN CONFIGURATION
# ---------------------
ENABLE_VPN_TOGGLE = False  

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
        # stream=True ensures we disconnect as soon as headers are received
        # timeout=7 gives slow IPTV handshakes a fighting chance
        # We enforce a TiviMate/Android user-agent directly to avoid server blocks
        response = requests.get(
            url, 
            stream=True, 
            timeout=7, 
            headers={"User-Agent": "TiviMate/5.0.4 (Linux; Android 11)"}
        )
        return response.status_code == 200
    except:
        return False

def process_channel(args):
    """Worker function for threads to process and check a channel."""
    # We now receive a mapped dictionary payload from the loop
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

    all_targets = GROUP_KEYWORDS + KEYWORDS + SERVER_KEYWORDS
    print(f"DEBUG: All targets found: {all_targets}")

    for target_k in all_targets:
        print(f"\n🎯 TARGET: {target_k}")
        
        url_map = {}
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
                    if not url: 
                        continue
                    
                    group_match = re.search(r'group-title="([^"]+)"', header)
                    group_name = group_match.group(1).strip() if group_match else "Other"
                    
                    name_match = re.search(r',([^,]*)$', header)
                    channel_name = name_match.group(1).strip() if name_match else "Unknown"
                    
                    server_match = re.search(r'https?://([^./:]+)', url)
                    server_prefix = server_match.group(1).upper() if server_match else "SERVER"
                    
                    id_str = ""
                    id_found = False
                    if KEEP_TVG_ID:
                        id_match = re.search(r'tvg-id="([^"]+)"', header)
                        if id_match:
                            id_str = f' tvg-id="{id_match.group(1)}"'
                            id_found = True
                    
                    logo_str = ""
                    logo_found = False
                    logo_match = re.search(r'tvg-logo="([^"]+)"', header)
                    if logo_match:
                        logo_str = f' tvg-logo="{logo_match.group(1)}"'
                        logo_found = True
                    
                    clean_header = f'#EXTINF:-1 group-title="{group_name}"{id_str}{logo_str},{channel_name} {server_prefix.lower()}.'
                    meta_for_search = re.sub(r'tvg-logo="[^"]*"', '', header).upper()
                    
                    if any(b.upper() in meta_for_search for b in PERMANENT_BLOCKLIST) or \
                       any(b.upper() in url.upper() for b in PERMANENT_BLOCKLIST):
                        continue
                    
                    if USE_BLOCKLIST:
                        if any(b.upper() in meta_for_search for b in BLOCKLIST) or \
                           any(b.upper() in url.upper() for b in BLOCKLIST) or \
                           EPISODE_PATTERN.search(meta_for_search):
                            continue

                    is_match = False
                    
                    if target_k in SERVER_KEYWORDS:
                        for var in search_terms:
                            if var.upper() == server_prefix:
                                is_match = True
                                break
                    elif target_k in GROUP_KEYWORDS:
                        for var in search_terms:
                            if STRICT_MATCH:
                                pattern = re.compile(rf'\b{re.escape(var.upper())}\b')
                                if pattern.search(group_name.upper()):
                                    is_match = True
                                    break
                            else:
                                if var.upper() in group_name.upper():
                                    is_match = True
                                    break
                    else:
                        for var in search_terms:
                            if STRICT_MATCH:
                                pattern = re.compile(rf'\b{re.escape(var.upper())}\b')
                                if pattern.search(meta_for_search):
                                    is_match = True
                                    break
                            else:
                                if var.upper() in meta_for_search:
                                    is_match = True
                                    break

                    if is_match:
                        score = 0
                        if id_found: score += 1
                        if logo_found: score += 1

                        # 🛡️ FIX A: Advanced extraction for PHP and slash styles
                        creds_match = re.search(r'(?:get\.php\?username=([^&]+)&password=([^&]+)|/([^/]+)/([^/]+)/)', url)
                        
                        user_pass_slug = "Unknown_Account"
                        if creds_match:
                            if creds_match.group(1) and creds_match.group(2):
                                user_pass_slug = f"{creds_match.group(1)}/{creds_match.group(2)}"
                            elif creds_match.group(3) and creds_match.group(4):
                                user_pass_slug = f"{creds_match.group(3)}/{creds_match.group(4)}"

                        # 🛡️ FIX B: Group by Account + Channel Name 
                        unique_key = f"{server_prefix}_{user_pass_slug}_{channel_name.strip().upper()}"
                        
                        # 🛡️ FIX C: Store as a standard dict rather than a tuple to prevent index crashes
                        if unique_key not in url_map:
                            url_map[unique_key] = {
                                'name': channel_name, 
                                'header': clean_header, 
                                'url': url,
                                'score': score
                            }
                        else:
                            if score > url_map[unique_key]['score']:
                                url_map[unique_key] = {
                                    'name': channel_name, 
                                    'header': clean_header, 
                                    'url': url,
                                    'score': score
                                }
                                
            except Exception as e: 
                continue

        # 🛡️ FIX D: Extract dict objects safely
        candidates = [val for val in url_map.values()]
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
            safe_name = target_k.replace("/", "_").replace("\\", "_").replace(" ", "_")
            
            if target_k in SERVER_KEYWORDS:
                out_filename = f"{safe_name}-server-{date_str}.m3u"
            elif target_k in GROUP_KEYWORDS:
                out_filename = f"{safe_name}-group-title-{date_str}.m3u"
            else:
                out_filename = f"{safe_name}-{date_str}.m3u"
                
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            
            def sort_by_actual_name(candidate):
                name = candidate['name']
                is_video = candidate['url'].upper().endswith(VIDEO_EXTENSIONS) or candidate['url'].lower().endswith('.ts')
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
