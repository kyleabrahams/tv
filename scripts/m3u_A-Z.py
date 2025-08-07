import re
from tqdm import tqdm

# File paths
input_file = '/Volumes/Kyle4tb1223/_Android/_M3U/SportsAZ.m3u'
output_file = '/Volumes/Kyle4tb1223/_Android/_M3U/SportsAZ SORTED.m3u'

# Group priorities
group_priority = {"Canada": 1, "USA": 2, "UK": 3, "Other": 99}

def get_priority(group):
    return group_priority.get(group, 99)

# Regex to match #EXTINF line with group-title
extinf_pattern = re.compile(r'#EXTINF:-1[^#]*?group-title="([^"]+)",([^#\n]+)')

entries = []
non_extinf_lines = []

# Read file
with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()

    if line.startswith("#EXTINF:"):
        url = lines[i + 1].strip() if i + 1 < len(lines) else ""

        match = extinf_pattern.search(line)
        if match:
            group, desc = match.groups()
            group = group.strip()
        else:
            # Try to extract description only
            desc_match = re.match(r'#EXTINF:-1,([^#\n]+)', line)
            desc = desc_match.group(1).strip() if desc_match else "Unknown"
            # Infer group based on prefix in description
            if desc.startswith("US:"):
                group = "USA"
            elif desc.startswith("UK:"):
                group = "UK"
            elif desc.startswith("CA:"):
                group = "Canada"
            else:
                group = "Other"
            # Rebuild EXTINF line with group-title
            line = f'#EXTINF:-1 group-title="{group}",{desc}'

        if url:
            entries.append((group, desc, url, line))
        i += 2
    else:
        non_extinf_lines.append(line)
        i += 1

print(f"Matched {len(entries)} channel entries.")
print(f"Preserved {len(non_extinf_lines)} other lines.")

# Deduplicate by (group, desc)
seen = set()
unique_entries = []
for group, desc, url, extinf in tqdm(entries, desc="Removing duplicates", unit="entry"):
    key = (group, desc)
    if key not in seen:
        seen.add(key)
        unique_entries.append((group, desc, url, extinf))

# Sort by group priority, group name, then description
sorted_entries = sorted(
    unique_entries,
    key=lambda x: (get_priority(x[0]), x[0].lower(), x[1].lower())
)

# Build output
output_lines = ["#EXTM3U"]
output_lines.extend(non_extinf_lines)

for group, desc, url, extinf in tqdm(sorted_entries, desc="Building output", unit="entry"):
    output_lines.append(extinf)
    output_lines.append(url)

# Write to file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines) + "\n")

print(f"Saved sorted playlist to {output_file}")
