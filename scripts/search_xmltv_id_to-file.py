import os
import shutil
import xml.etree.ElementTree as ET

# python3 search_xmltv_id_to-file.py
# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/search_xmltv_id_to-file.py


# Function to search for a word in an XML file and collect <channel> elements
def search_word_in_xml(file_path, search_word, collected_channels):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Search for the word in text within the XML structure
        for elem in root.iter():
            if elem.tag == 'channel' and elem.text and search_word.lower() in elem.text.lower():
                collected_channels.append(elem)
    except ET.ParseError:
        print(f"Error parsing XML file: {file_path}")

# Function to search through all XML files in a directory and its subdirectories
def search_xml_in_directory(src_dir, search_word):
    collected_channels = []  # List to hold the <channel> elements
    for root_dir, dirs, files in os.walk(src_dir):
        for file_name in files:
            if file_name.endswith('.xml'):
                file_path = os.path.join(root_dir, file_name)
                search_word_in_xml(file_path, search_word, collected_channels)
    return collected_channels

# Function to write the collected <channel> elements to a new XML file
def write_channels_to_new_xml(collected_channels, output_file):
    # Create a new XML tree with a root element
    root = ET.Element('channels')
    for channel in collected_channels:
        root.append(channel)

    # Create a new ElementTree and write it to the output file
    tree = ET.ElementTree(root)
    tree.write(output_file)

# Main function to drive the search and duplication
def main():
    # Define your source directory and search word
    src_dir = '../sites'  # Replace with the directory you want to search
    search_word = 'London'  # Replace with the word you're searching for

    # python3 search_xmltv_id_to-file.py
    
    # Search for the channels
    collected_channels = search_xml_in_directory(src_dir, search_word)
    
    # Write the collected channels to a new XML file
    output_file = f'./_Search_Results/{search_word}_channels.xml'
    write_channels_to_new_xml(collected_channels, output_file)
    print(f"Found {len(collected_channels)} <channel> elements and saved to {output_file}")

if __name__ == "__main__":
    main()
