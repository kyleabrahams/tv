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
KEYWORDS = ["CTV Nature"]

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
STRICT_MATCH = False  

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
                    
                    url = ""
                    for potential_url in lines[1:]:
                        if potential_url.strip() and not potential_url.startswith("#"):
                            url = potential_url.strip()
                            break
                    
                    if not url: continue
                    
                    full_meta = header.upper()
                    
                    # 1. THE VOD/EPISODE KILLER
                    if any(b.upper() in full_meta for b in BLOCKLIST) or \
                       any(b.upper() in url.upper() for b in BLOCKLIST) or \
                       EPISODE_PATTERN.search(full_meta):
                        continue

                    # 2. KEYWORD SEARCH
                    match_found = False
                    for var in search_terms:
                        if var.upper() in full_meta:
                            if url not in found_urls:
                                found_content.append(f"#EXTINF{header}\n{url}\n")
                                found_urls.add(url)
                                match_found = True
                                break
            except: continue

        # 3. OUTPUT - Using the keyword name in the message
        if found_content:
            safe_name = target_k.replace(" ", "_")
            out_filename = f"{safe_name}-{date_str}.m3u"
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            
            sorted_content = sorted(found_content, key=lambda x: x.split(",")[-1].lower())
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n" + "".join(sorted_content))
            print(f"\n📂 Created: {out_filename} ({len(found_content)} channels)")
        else:
            # THIS IS THE FIX: It now reports the specific keyword that failed
            print(f"\nℹ️ No channels found for keyword: '{target_k}'")

if __name__ == "__main__":
    run_keyword_search()