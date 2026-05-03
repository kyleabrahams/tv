import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Silence the LibreSSL Warning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
import ffmpeg  # ⚠️ REQUIRES: pip install ffmpeg-python

# ---------------------
# CONFIGURATION
# ---------------------
INPUT_FILE = '/Volumes/Kyle4tb1223/Documents/Github/tv/list/Kodi A-Z.m3u'
OUTPUT_FILE = '/Volumes/Kyle4tb1223/Documents/Github/tv/list/Kodi [Quality].m3u'

# How many channels to probe at the exact same time
MAX_WORKERS = 10 

# ---------------------
# HELPER FUNCTIONS
# ---------------------
def get_quality_tag(height):
    """Maps pixel height to standard resolution tags."""
    if height >= 2160: return " [4K]"
    elif height >= 1080: return " [FHD]"
    elif height >= 720: return " [HD]"
    elif height > 0: return " [SD]"
    return ""

def probe_resolution(url):
    """Pings the stream to extract the video pixel height."""
    try:
        probe = ffmpeg.probe(
            url, 
            v='error', 
            select_streams='v:0', 
            show_entries='stream=height', 
            timeout=5
        )
        height = int(probe['streams']['height'])
        return height
    except Exception:
        return 0

def process_channel(args):
    """Worker thread to probe and rename a channel."""
    extinf, url, name = args
    
    # 1. Skip VOD video files to save execution time
    if url.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
        return {'extinf': extinf, 'url': url, 'name': name, 'height': 0}
        
    print(f"Probing: {url}")
    height = probe_resolution(url)
    
    if height > 0:
        quality_tag = get_quality_tag(height)
        
        if not any(tag in extinf.upper() for tag in [" [SD]", " [HD]", " [FHD]", " [4K]"]):
            extinf_clean = extinf
            if quality_tag == " [HD]":
                extinf_clean = re.sub(r'\bHD\b', '', extinf, flags=re.IGNORECASE).strip()
            elif quality_tag == " [FHD]":
                extinf_clean = re.sub(r'\bFHD\b|\bHD\b', '', extinf, flags=re.IGNORECASE).strip()
            
            extinf_clean = re.sub(r'\s+', ' ', extinf_clean)
            last_space_index = extinf_clean.rfind(" ")
            
            if last_space_index != -1:
                extinf = extinf_clean[:last_space_index] + quality_tag + extinf_clean[last_space_index:]
            else:
                extinf = f"{extinf_clean}{quality_tag}"
                
    return {'extinf': extinf, 'url': url, 'name': name, 'height': height}

# ---------------------
# MAIN RUNNER
# ---------------------
def run_quality_tagger():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found at {INPUT_FILE}")
        return

    print("📖 Reading M3U file...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split("#EXTINF")
    header_block = blocks[0]
    
    candidates = []
    for block in blocks[1:]:
        lines = block.strip().split("\n")
        extinf = f"#EXTINF{lines[0]}"
        
        # Pull channel name for secondary alphabetical fallback sort
        name_match = re.search(r',([^,]*)$', extinf)
        channel_name = name_match.group(1).strip() if name_match else "Unknown"
        
        url = ""
        for potential_url in lines[1:]:
            if potential_url.strip() and not potential_url.startswith("#"):
                url = potential_url.strip()
                break
        
        if extinf and url:
            candidates.append((extinf, url, channel_name))

    print(f"📡 Starting parallel probe for {len(candidates)} channels...")
    
    processed_candidates = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(process_channel, candidates)
        for result in results:
            processed_candidates.append(result)

    # 🎯 HIERARCHY FIX: Negating height flips sort to descending (Highest to Lowest)
    # Secondary condition fallback keeps it sorted alphabetically.
    print("🔀 Sorting by resolution hierarchy...")
    sorted_candidates = sorted(
        processed_candidates, 
        key=lambda x: (-x['height'], x['name'].lower())
    )

    print(f"💾 Saving to {OUTPUT_FILE}...")
    final_output_lines = []
    for item in sorted_candidates:
        final_output_lines.append(f"{item['extinf']}\n{item['url']}\n")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(header_block + "".join(final_output_lines))
        
    print("✅ All done!")

if __name__ == "__main__":
    run_quality_tagger()
