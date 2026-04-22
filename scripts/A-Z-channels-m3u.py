# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/A-Z-channels-m3u.py

import re
import os
from tqdm import tqdm

# File paths
input_file = '/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched/trytv-Canada_playlist_96066144 A-Z.m3u'
output_dir = os.path.dirname(input_file)
base_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join(output_dir, f"{base_name} A-Z.m3u")

# Group priorities
group_priority = {"Canada": 1, "USA": 2, "UK": 3, "Other": 99}

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
        
        # Skip if the next line is a tag instead of a URL
        if url.startswith("#"):
            i += 1
            continue

        match = extinf_pattern.search(line)
        if match:
            group, desc = match.groups()
            group, desc = group.strip(), desc.strip()
        else:
            desc_match = re.match(r'#EXTINF:-1,([^#\n]+)', line)
            desc = desc_match.group(1).strip() if desc_match else "Unknown"
            if desc.startswith("US:"): group = "USA"
            elif desc.startswith("UK:"): group = "UK"
            elif desc.startswith("CA:"): group = "Canada"
            else: group = "Other"
            line = f'#EXTINF:-1 group-title="{group}",{desc}'

        if url:
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

# Build output WITHOUT empty spacers
output_lines = ["#EXTM3U"]
for group, desc, url, extinf in sorted_entries:
    output_lines.append(extinf)
    output_lines.append(url)

# Write to file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines) + "\n")

print(f"✅ Processed {len(sorted_entries)} channels without gaps.")
