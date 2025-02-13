import os
import xml.etree.ElementTree as ET

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/search_xmltv_eng.py

# Function to filter only <channel> elements with lang="en" and save to an output directory
def filter_english_channels(file_path, output_dir):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Collect only channels with lang="en"
        filtered_channels = [channel for channel in root.findall("channel") if channel.get("lang") == "en"]

        if not filtered_channels:
            print(f"No English channels found in {file_path}. Skipping file.")
            return
        
        # Create a new root element
        new_root = ET.Element("tv")
        
        # Copy over all other elements (programs, etc.) and replace <channel> with filtered ones
        for elem in root:
            if elem.tag == "channel":
                continue  # Skip all channels (we will add only the filtered ones)
            new_root.append(elem)

        # Append filtered <channel> elements
        new_root.extend(filtered_channels)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Get the filename from the original path
        file_name = os.path.basename(file_path)
        output_file_path = os.path.join(output_dir, file_name)

        # Write filtered data to the new file
        tree = ET.ElementTree(new_root)
        tree.write(output_file_path, encoding="utf-8", xml_declaration=True)
        print(f"Saved filtered XML to {output_file_path}")

    except ET.ParseError:
        print(f"Error parsing XML file: {file_path}")

# Function to process all XML files in a directory and save to an output directory
def process_all_xml_files(input_dir, output_dir):
    for root_dir, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                filter_english_channels(file_path, output_dir)

# Main function
def main():
    input_dir = "./_Search_Results"  # Directory containing XML files
    output_dir = "./_Search_Results/_Channels-english"  # Directory to save filtered XML files

    process_all_xml_files(input_dir, output_dir)
    print("Processing complete. Filtered XML files saved to:", output_dir)

if __name__ == "__main__":
    main()
