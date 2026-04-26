# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/A-Z-channels-m3u.py

import re
import os

# File paths
input_file = '/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched/Active/NoExp-xxip9-streatj87@gmail.com A-Z.m3u'
output_dir = os.path.dirname(input_file)
base_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join(output_dir, f"{base_name} A-Z.m3u")

# Group priorities
group_priority = {"Canada": 1, "USA": 2, "UK": 3, "Other": 99}

# Toggles
REMOVE_RADIO = True
REMOVE_VIDEO_FILES = True

# Define what to look for
RADIO_KEYWORDS = ['radio', 'fm', 'music']  # Keywords found in group or description
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov') # Extensions at the end of the URL

def get_priority(group):
    return group_priority.get(group, 99)

# Regex to match #EXTINF line with group-title
extinf_pattern = re.compile(r'#EXTINF:-1[^#]*?group-title="([^"]+)",([^#\n]+)')

entries = []

# Read file and strip whitespace/empty lines immediately
with open(input_file, 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file if line.strip()]

i = 0
while i < len(lines):
    line = lines[i]

    if line.startswith("#EXTINF:"):
        url = lines[i + 1] if i + 1 < len(lines) else ""
        
        if url.startswith("#"):
            i += 1
            continue

        # --- 1. Determine Group and Description ---
        match = extinf_pattern.search(line)
        if match:
            group, desc = match.groups()
            group, desc = group.strip(), desc.strip()
        else:
            desc_match = re.match(r'#EXTINF:-1,([^#\n]+)', line)
            desc = desc_match.group(1).strip() if desc_match else "Unknown"
            
            # FIXED: Explicitly assigning group here
            if desc.startswith("US:"): group = "USA"
            elif desc.startswith("UK:"): group = "UK"
            elif desc.startswith("CA:"): group = "Canada"
            else: group = "Other"
            
            # Rebuild line to include the inferred group
            line = f'#EXTINF:-1 group-title="{group}",{desc}'

        # --- 2. NEW FILTERING LOGIC ---
        skip_entry = False

        if REMOVE_RADIO:
            if any(k in group.lower() or k in desc.lower() for k in RADIO_KEYWORDS):
                skip_entry = True

        if REMOVE_VIDEO_FILES:
            if url.lower().endswith(VIDEO_EXTENSIONS):
                skip_entry = True

        if url and not skip_entry:
            entries.append((group, desc, url, line))
        
        i += 2
    else:
        i += 1

# Deduplicate
seen = set()
unique_entries = []
for entry in entries:
    key = (entry[0], entry[1], entry[2])
    if key not in seen:
        seen.add(key)
        unique_entries.append(entry)

# Sort: Priority Group then A-Z Name
sorted_entries = sorted(unique_entries, key=lambda x: (get_priority(x[0]), x[1].lower()))

# Build output
output_lines = ["#EXTM3U"]
for group, desc, url, extinf in sorted_entries:
    output_lines.append(extinf)
    output_lines.append(url)

# Write to file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines) + "\n")

print(f"✅ Processed {len(sorted_entries)} channels without gaps.")
