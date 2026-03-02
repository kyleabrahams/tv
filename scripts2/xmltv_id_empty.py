import os
import xml.etree.ElementTree as ET

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/xmltv_id_empty.py

# Function to process XML files and set xmltv_id=""
def process_xml_file(input_file, output_file):
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Update all <channel> elements to have xmltv_id=""
        for channel in root.findall("channel"):
            if "xmltv_id" in channel.attrib:
                channel.set("xmltv_id", "")

        # Save modified XML to output folder
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"Processed: {input_file} → {output_file}")

    except ET.ParseError:
        print(f"Error parsing: {input_file}")

# Function to process all XML files in input_dir and save to output_dir
def process_all_xml_files(input_dir, output_dir):
    for root_dir, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith(".xml"):
                input_file = os.path.join(root_dir, file_name)
                output_file = os.path.join(output_dir, os.path.relpath(input_file, input_dir))

                process_xml_file(input_file, output_file)

# Main function
def main():
    input_dir = "./_Search_Results/_Channels-english"  # Folder with XML files
    output_dir = "./_Search_Results/_Channels-xmltv-cleared"  # Output folder

    process_all_xml_files(input_dir, output_dir)
    print("Processing complete. Updated XML files saved to:", output_dir)

if __name__ == "__main__":
    main()