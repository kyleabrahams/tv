# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/A-Z-channels-m3u.py

import re
import os

# File paths
input_file = '/Volumes/Kyle4tb1223/Documents/Github/tv/list/Kodi.m3u'
output_dir = os.path.dirname(input_file)
base_name = os.path.splitext(os.path.basename(input_file))[0]

# Sequential Numbering Logic
output_file = os.path.join(output_dir, f"{base_name} A-Z.m3u")
counter = 1
while os.path.exists(output_file):
    output_file = os.path.join(output_dir, f"{base_name} A-Z_{counter}.m3u")
    counter += 1

# Group priorities
group_priority = {"Canada": 1, "US": 2, "United Kingdom": 3}

# Toggles
REMOVE_RADIO = True
REMOVE_VIDEO_FILES = True
REMOVE_DUPLICATE_URLS = True  
KEEP_TVG_LOGO = True  # 🖼️ Set to False to strip all logos from the list

RADIO_KEYWORDS = ['radio', 'fm', 'music']
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov')

def get_priority(group_name):
    # FORCE XXX TO THE VERY BOTTOM
    if group_name.upper() == "XXX":
        return 999
        
    for key, val in group_priority.items():
        if key.lower() == group_name.lower():
            return val
    return 99

# Regex to match #EXTINF line with group-title
extinf_pattern = re.compile(r'#EXTINF:-1[^#]*?group-title="([^"]+)",([^#\n]+)')

entries = []

if not os.path.exists(input_file):
    print(f"❌ Error: File not found at {input_file}")
    exit()

with open(input_file, 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file if line.strip()]

i = 0
while i < len(lines):
    line = lines[i]

    if line.startswith("#EXTINF:"):
        original_header = line  # Save the raw line to extract attributes later
        
        # Pull URL
        url = lines[i + 1] if i + 1 < len(lines) else ""
        if url.startswith("#"):
            i += 1
            continue

        # 1. Determine Group and Description
        match = extinf_pattern.search(line)
        if match:
            group, desc = match.groups()
            group, desc = group.strip(), desc.strip()
        else:
            desc_match = re.match(r'#EXTINF:-1,([^#\n]+)', line)
            desc = desc_match.group(1).strip() if desc_match else "Unknown"
            
            if desc.lower().startswith("us:"): group = "US"
            elif desc.lower().startswith("uk:"): group = "UK"
            elif desc.lower().startswith("ca:"): group = "Canada"
            else: group = "Other"

        # --- FIX NAMES & FORMATTING ---
        # Normalize Group Names
        group_lower = group.lower()
        if group_lower == "canada": group = "Canada"
        elif group_lower in ["us", "usa"]: group = "US"
        elif group_lower in ["uk", "gb"]: group = "UK"
        # PROTECT XXX FROM BECOMING Xxx:
        elif group_lower == "xxx": group = "XXX"
        else: group = group.title()

        # Clean Description Prefixes (CA, US, UK, USA)
        desc = re.sub(r'^USA[:\s]*', 'US ', desc, flags=re.IGNORECASE)
        desc = re.sub(r'^(CA|US|UK)[:\s]*', r'\1 ', desc, flags=re.IGNORECASE)
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        # 🆔 HANDLE TVG-ID (FORCED POSITIONING FIRST)
        id_match = re.search(r'tvg-id="([^"]+)"', original_header)
        if id_match:
            id_str = f'tvg-id="{id_match.group(1)}" '
        else:
            # 🛠️ Autocreated fallback ID if it doesn't exist
            id_str = 'tvg-id="EMPTY" '
        
        # 🖼️ HANDLE TVG-LOGO (FORCED POSITIONING SECOND)
        logo_str = ""
        if KEEP_TVG_LOGO:
            logo_match = re.search(r'tvg-logo="([^"]+)"', original_header)
            if logo_match:
                logo_str = f'tvg-logo="{logo_match.group(1)}" '
            else:
                logo_str = 'tvg-logo="https://placeholder.com" '
        
        # Re-build final line forced in requested sequence
        line = f'#EXTINF:-1 {id_str}{logo_str}group-title="{group}",{desc}'

        # 2. Filter Logic
        skip_entry = False
        if REMOVE_RADIO:
            if any(k.lower() in group.lower() or k.lower() in desc.lower() for k in RADIO_KEYWORDS):
                skip_entry = True
        if REMOVE_VIDEO_FILES:
            if url.lower().endswith(VIDEO_EXTENSIONS):
                skip_entry = True

        if url and not skip_entry:
            entries.append((group, desc, url, line))
        i += 2
    else:
        i += 1

# 3. Deduplicate
seen = set()
unique_entries = []
for entry in entries:
    # Check toggle to lock onto just the URL or full channel triplet
    if REMOVE_DUPLICATE_URLS:
        key = entry[2].lower()
    else:
        key = (entry[0].lower(), entry[1].lower(), entry[2].lower())
        
    if key not in seen:
        seen.add(key)
        unique_entries.append(entry)

# 4. SORTING
sorted_entries = sorted(
    unique_entries, 
    key=lambda x: (get_priority(x[0]), x[0].lower(), x[1].lower())
)

# 5. Build output
output_lines = ["#EXTM3U"]
for group, desc, url, extinf in sorted_entries:
    output_lines.append(extinf)
    output_lines.append(url)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines) + "\n")

print(f"✅ Processed {len(sorted_entries)} channels.")
print(f"📂 Formatting fixed: {output_file}")
