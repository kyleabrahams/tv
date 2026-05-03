# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/A-Z-channels-m3u.py

import re
import os

# --- CONFIG ---
input_file = '/Volumes/Kyle4tb1223/Documents/Github/tv/list/Kodi.m3u'
output_dir = os.path.dirname(input_file)
base_name = os.path.splitext(os.path.basename(input_file))[0]

output_file = os.path.join(output_dir, f"{base_name} A-Z.m3u")
counter = 1
while os.path.exists(output_file):
    output_file = os.path.join(output_dir, f"{base_name} A-Z_{counter}.m3u")
    counter += 1

group_priority = {"Canada": 1, "US": 2, "United Kingdom": 3}

REMOVE_RADIO = False
REMOVE_VIDEO_FILES = False
REMOVE_DUPLICATE_URLS = True
KEEP_TVG_LOGO = True
PURE_AZ_SORT = True

VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov')
RADIO_KEYWORDS = ['radio', 'fm', 'music']

def get_priority(group_name):
    if group_name.upper() == "XXX": return 999
    for key, val in group_priority.items():
        if key.lower() == group_name.lower(): return val
    return 99

if not os.path.exists(input_file):
    print(f"❌ Error: File not found at {input_file}"); exit()

with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
    lines = [line.strip() for line in file if line.strip()]

# --- STEP 2: COLLECTION ---
entries = []
current_header = None

for line in lines:
    if line.startswith("#EXTM3U"): continue
    if line.startswith("#EXTINF:"):
        current_header = line
        continue
    
    if current_header and not line.startswith("#"):
        header, url = current_header, line
        current_header = None 
        
        # 1. EXTRACTION
        group_match = re.search(r'group-title="([^"]+)"', header)
        group_raw = group_match.group(1).strip() if group_match else "Other"
        name_match = re.search(r',([^,]*)$', header)
        desc_raw = name_match.group(1).strip() if name_match else "Unknown"

        # 2. AGGRESSIVE CLEANUP
        # Strips any trailing " word." tags (like " jack." or " luna.")
        clean_name = re.sub(r'\s[a-z0-9-]+\.\s*$', '', desc_raw, flags=re.IGNORECASE).strip()

        # 3. GENERATE NEW TAG (From the actual URL)
        server_match = re.search(r'https?://([^./:]+)', url)
        server_prefix = server_match.group(1).lower() if server_match else "serv"
        new_tag = f"{server_prefix[:4]}."

        # 4. UNIFIED CASING (Force Title Case on EVERY channel)
        # This turns "BLACK" into "Black" and "A GIRL KNOWS" into "A Girl Knows"
        desc = f"{clean_name.title()} {new_tag}"
        
        # Group name still gets Title Case unless it's strictly XXX
        group = "XXX" if group_raw.upper() == "XXX" else group_raw.title()

        # 5. METADATA
        id_match = re.search(r'tvg-id="([^"]+)"', header)
        id_str = f'tvg-id="{id_match.group(1)}" ' if id_match else 'tvg-id="EMPTY" '
        logo_match = re.search(r'tvg-logo="([^"]+)"', header)
        logo_str = f'tvg-logo="{logo_match.group(1)}" ' if logo_match else 'tvg-logo="EMPTY" '
        
        final_extinf = f'#EXTINF:-1 {id_str}{logo_str}group-title="{group}",{desc}'
        entries.append((group, desc, url, final_extinf))

# --- STEP 3: DEDUPLICATION ---
url_map = {}
for entry in entries:
    g, d, u, h = entry
    key = u.lower() if REMOVE_DUPLICATE_URLS else (g.lower(), d.lower(), u.lower())
    
    score = (0 if 'id="EMPTY"' in h else 1) + (0 if 'logo="EMPTY"' in h else 1)
    if key not in url_map or score > url_map[key][1]:
        url_map[key] = (entry, score)

unique_entries = [val[0] for val in url_map.values()]

# --- STEP 4: SORTING ---
if PURE_AZ_SORT:
    print(f"🔤 Sorting {len(unique_entries)} channels alphabetically...")
    sorted_entries = sorted(unique_entries, key=lambda x: (x[2].lower().endswith(VIDEO_EXTENSIONS), x[1].lower()))
else:
    print(f"🗂️ Sorting {len(unique_entries)} channels by priority...")
    sorted_entries = sorted(unique_entries, key=lambda x: (get_priority(x[0]), x[2].lower().endswith(VIDEO_EXTENSIONS), x[0].lower(), x[1].lower()))

# --- STEP 5: WRITE ---
output_lines = ['#EXTM3U url-tvg="https://githubusercontent.com"']
for g, d, u, h in sorted_entries:
    output_lines.extend([h, u])

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines) + "\n")

print(f"✅ Processed {len(sorted_entries)} unique channels.")
