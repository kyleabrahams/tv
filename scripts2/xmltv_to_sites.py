import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/xmltv_to_sites.py

# Function to sanitize filenames (remove invalid characters)
def sanitize_filename(name):
    return re.sub(r'[^\w\.-]', '_', name)  # Replace special characters with "_"

# Function to process all XML files and group channels by site
def process_all_xml_files(input_dir, output_dir):
    site_channels = defaultdict(list)  # Dictionary to collect channels by site

    # Iterate through all XML files in the directory
    for root_dir, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()

                    # Extract <channel> elements and store them by site
                    for channel in root.findall("channel"):
                        # Set xmltv_id to an empty string if it exists
                        if "xmltv_id" in channel.attrib:
                            channel.set("xmltv_id", "")

                        site = channel.get("site", "unknown")  # Default to "unknown" if missing
                        site_channels[site].append(channel)

                except ET.ParseError:
                    print(f"Error parsing XML file: {file_path}")

    if not site_channels:
        print("No channels found in any XML files. Exiting.")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create separate XML files for each site
    for site, channels in site_channels.items():
        clean_site = sanitize_filename(site)  # Make filename safe
        output_file_path = os.path.join(output_dir, f"{clean_site}_channels.xml")

        # Create the new root element <channels>
        new_root = ET.Element("channels")
        new_root.extend(channels)  # Append all <channel> elements

        # Save the file with the proper XML declaration
        new_tree = ET.ElementTree(new_root)
        new_tree.write(output_file_path, encoding="utf-8", xml_declaration=True)
        print(f"Saved {len(channels)} channels to {output_file_path}")

# Main function
def main():
    input_dir = "./_Search_Results/_Channels-english"  # Folder containing XML files
    output_dir = "./_Search_Results/_Channels-grouped-to-sites"  # Folder to save new XML files

    process_all_xml_files(input_dir, output_dir)
    print("Processing complete. Separated XML files saved to:", output_dir)

if __name__ == "__main__":
    main()
