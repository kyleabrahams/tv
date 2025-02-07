import re

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/m3u_A-Z.py

# Define input and output file paths
input_file = "/Volumes/Kyle4tb1223/_Android/_M3U/___Servers/_Active/ca_newlife3_Jan 16 2028_D12m2770.m3u"
output_file = "/Volumes/Kyle4tb1223/_Android/_M3U/___Servers/_Active/ca_newlife3_Jan 16 2028_SORTED.m3u"

# Read the content of the input .m3u file
with open(input_file, "r") as file:
    playlist = file.read()

# Print the first 500 characters to debug
print("First 500 characters of playlist:\n", playlist[:500])

# Regex to match the country code, description, and URL
pattern = re.compile(r"#EXTINF:-1,.*\|([A-Za-z]+)\|([^,]*)\n(http[^\n]+)")

# Extract the country code, description, and URL pairs
country_desc_urls = pattern.findall(playlist)

# Print out the extracted country_desc_urls to check if anything is matched
print("Extracted country_desc_urls:", country_desc_urls)

# If matches are found, proceed with sorting
if country_desc_urls:
    # Sort the country_desc_urls list by country code (first item in tuple)
    sorted_country_desc_urls = sorted(country_desc_urls, key=lambda x: x[0])

    # Create a new playlist string with sorted items
    sorted_playlist = "#EXTM3U\n" + "\n".join([f"#EXTINF:-1,|{country}| {desc if desc else 'No Description'}\n{url}" for country, desc, url in sorted_country_desc_urls])

    # Write the sorted playlist to the output .m3u file
    with open(output_file, "w") as file:
        file.write(sorted_playlist)

    print(f"Sorted playlist saved to {output_file}")
else:
    print("No matches found. Please check the regex or the format of the .m3u file.")