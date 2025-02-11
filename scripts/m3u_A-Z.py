import re

# Define input and output file paths
input_file = "/Volumes/Kyle4tb1223/_Android/_M3U/___Servers/_Canada/ca_newlife3_CANADA-SORTED.m3u"
output_file = "/Volumes/Kyle4tb1223/_Android/_M3U/___Servers/_Canada/ca_newlife3_CANADA-SORTED2.m3u"

# Read the content of the input .m3u file
with open(input_file, "r", encoding="utf-8") as file:
    playlist = file.read()

# Regex to capture: group-title, description, and URL
pattern = re.compile(r'#EXTINF:-1 group-title="([^"]+)",([^\n]+)\n(http[^\n]+)')

# Extract matches (group-title, description, URL)
matches = pattern.findall(playlist)

# If no matches are found, exit
if not matches:
    print("No matches found. Check the .m3u file format.")
    exit()

# Remove duplicates while preserving exact group-title and description
unique_matches = []
seen = set()
for group, desc, url in matches:
    unique_key = (group, desc)
    if unique_key not in seen:
        unique_matches.append((group, desc, url))
        seen.add(unique_key)

# Define priority for group names
group_priority = {"Canada": 1, "USA": 2, "UK": 3}
default_priority = 99  # Lower priority for unknown groups

def get_group_priority(group):
    for key in group_priority:
        if key in group:
            return group_priority[key]
    return default_priority

# Sorting by group priority, then alphabetically within each group
sorted_matches = sorted(unique_matches, key=lambda x: (get_group_priority(x[0]), x[0], x[1]))

# Build the sorted playlist with proper formatting
sorted_playlist = "#EXTM3U\n"
for group, desc, url in sorted_matches:
    sorted_playlist += f'#EXTINF:-1 group-title="{group}",{desc}\n{url}\n'

# Write the sorted playlist to the output file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(sorted_playlist)

print(f"Sorted and de-duplicated playlist saved to {output_file}")
