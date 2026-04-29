# python3 m3u_channel_finder.py

import os
import glob
import re
import sys
from datetime import datetime

# ---------------------
# CONFIGURATION
# ---------------------
M3U_FOLDER = "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched"
OUTPUT_FOLDER = "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched/Channels"

# 1. Keywords to find
KEYWORDS = ["CTV"]

# 2. Countries to filter by (Matches group-title="USA", etc.)
# Set to [] if you want to search ALL countries.
KEYWORDS_MAP = {
    "South Africa": ["South Africa", "ZA", "SA", "SouthAfrica"],
    "USA": ["USA", "US", "United States"],
    "Canada": ["Canada", "CA", "CAN"],
    "UK": ["UK", "United Kingdom", "Great Britain", "BBC"],
    "HBO": ["HBO"],
    "Food": ["Food", "Cooking", "Kitchen"]
}

# True = Match whole word only ("Food" matches "Food Network")
# False = Match anywhere ("Food" matches "FoodNetworkHD")
STRICT_MATCH = True  

# BLOCKLIST: Aggressive filter to remove Radio, Episodes, and Video Files
BLOCKLIST = ["S01", "E01", "SEASON", "RADIO", "EP.", ".MP4", ".MKV", ".AVI", ".MOV"]

def print_progress(iteration, total, prefix='', suffix='', length=30, fill='█'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()

def run_keyword_search():
    date_str = datetime.now().strftime('%Y-%m-%d')
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Catch S04E08 and similar patterns
    EPISODE_PATTERN = re.compile(r's\d{1,3}e\d{1,3}', re.IGNORECASE)
    
    files = glob.glob(os.path.join(M3U_FOLDER, "*.m3u"))
    if not files:
        print(f"❌ No .m3u files found in {M3U_FOLDER}")
        return

    for target_k in KEYWORDS:
        print(f"\n🎯 TARGET: {target_k}")
        found_content = []
        found_urls = set()
        search_terms = KEYWORDS_MAP.get(target_k, [target_k])

        for i, f_path in enumerate(files):
            print_progress(i + 1, len(files), prefix='Progress:', suffix=f'Searching...')
            
            try:
                with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                blocks = content.split("#EXTINF")
                for block in blocks[1:]:
                    lines = block.strip().split("\n")
                    header = lines[0]
                    
                    # 1. FIND URL
                    url = ""
                    for potential_url in lines[1:]:
                        if potential_url.strip() and not potential_url.startswith("#"):
                            url = potential_url.strip()
                            break
                    if not url: continue
                    
                    # 2. EXTRACT GROUP, CHANNEL NAME, AND SERVER
                    # Get group-title
                    group_match = re.search(r'group-title="([^"]+)"', header)
                    group_name = group_match.group(1).strip() if group_match else "Other"
                    
                    # Get channel name (everything after the last comma)
                    name_match = re.search(r',([^,]*)$', header)
                    channel_name = name_match.group(1).strip() if name_match else "Unknown"
                    
                    # EXTRACT SERVER NAME FROM URL
                    # This grabs 'bgdc' from 'http://bgdc.live:25461/...'
                    server_match = re.search(r'https?://([^./:]+)', url)
                    server_prefix = server_match.group(1).upper() if server_match else "SERVER"
                    
                    # Create the clean tag-free header with SERVER prefix
                    clean_header = f'#EXTINF:-1 group-title="{group_name}",{server_prefix}-{channel_name}'
                    
                    # Use original header for keyword searching
                    full_meta = header.upper()
                    
                    # 3. THE VOD/EPISODE KILLER
                    if any(b.upper() in full_meta for b in BLOCKLIST) or \
                       any(b.upper() in url.upper() for b in BLOCKLIST) or \
                       EPISODE_PATTERN.search(full_meta):
                        continue

                    # 4. KEYWORD SEARCH
                    for var in search_terms:
                        if var.upper() in full_meta:
                            if url not in found_urls:
                                # Save the CLEAN header instead of the original
                                found_content.append(f"{clean_header}\n{url}\n")
                                found_urls.add(url)
                                break
            except: continue

        # 5. OUTPUT
        if found_content:
            safe_name = target_k.replace(" ", "_")
            out_filename = f"{safe_name}-{date_str}.m3u"
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            
            # SORTING LOGIC:
            # We split by the comma, then split the second part by the first hyphen 
            # to isolate the actual channel name from the SERVER prefix.
            def sort_by_actual_name(entry):
                try:
                    # Get the part after the comma: "SERVER-Channel Name"
                    after_comma = entry.split(",")[-1]
                    # Split at the first hyphen and take what's after it
                    # if no hyphen exists, it just takes the whole string
                    actual_name = after_comma.split("-", 1)[-1]
                    return actual_name.strip().lower()
                except:
                    return entry.lower()

            sorted_content = sorted(found_content, key=sort_by_actual_name)
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n" + "".join(sorted_content))
            print(f"\n📂 Created: {out_filename} ({len(found_content)} channels)")

if __name__ == "__main__":
    run_keyword_search()