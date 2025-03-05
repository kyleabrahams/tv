import re
from tqdm import tqdm  # Progress bar library

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/m3u_A-Z.py


# Define input and output file paths
input_file = '/Volumes/Kyle4tb1223/_Android/_M3U/___New/Mar 5/tvhomesmart_Jan_30_2026_35661061_plus.m3u'
output_file = '/Volumes/Kyle4tb1223/_Android/_M3U/___New/Mar 5/tvhomesmart_Jan_30_2026_SORTED.m3u'

# Read the content of the input .m3u file
with open(input_file, "r", encoding="utf-8") as file:
    playlist = file.read()

# Updated regex to properly capture group-title, description, and URL
pattern = re.compile(r'#EXTINF:-1[^#]*?group-title="([^"]+)",([^#\n]+)\n(http[^\n]+)')

# Extract matches (group-title, description, URL)
matches = pattern.findall(playlist)

# Debugging: Check how many matches were found
print(f"Found {len(matches)} matches.")

# If no matches are found, exit
if not matches:
    print("No matches found. Check the .m3u file format.")
    exit()

# Remove duplicates while preserving exact group-title and description
unique_matches = []
seen = set()
for group, desc, url in tqdm(matches, desc="Removing duplicates", unit="entry"):
    unique_key = (group, desc)
    if unique_key not in seen:
        unique_matches.append((group, desc, url))
        seen.add(unique_key)

# Define priority for group names
group_priority = {"Canada": 1, "USA": 2, "UK": 3}
default_priority = 99  # Lower priority for unknown groups

def get_group_priority(group):
    return group_priority.get(group, default_priority)

# Sorting by group priority, then alphabetically within each group
sorted_matches = sorted(unique_matches, key=lambda x: (get_group_priority(x[0]), x[0], x[1]))

# Build the sorted playlist with proper formatting
sorted_playlist = "#EXTM3U\n"
for group, desc, url in tqdm(sorted_matches, desc="Building playlist", unit="entry"):
    sorted_playlist += f'#EXTINF:-1 group-title="{group}",{desc}\n{url}\n'

# Write the sorted playlist to the output file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(sorted_playlist)

print(f"Sorted and de-duplicated playlist saved to {output_file}")
