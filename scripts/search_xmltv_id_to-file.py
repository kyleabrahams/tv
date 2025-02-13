import os
import xml.etree.ElementTree as ET

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/search_xmltv_id_to-file.py

# Toggle options
empty_xmltv_id = True   # Set to True to empty xmltv_id=""
filter_english = True   # Set to True to filter channels with lang="en"

# Function to search for a word in an XML file and collect <channel> elements
def search_word_in_xml(file_path, search_word, collected_channels):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for elem in root.iter("channel"):
            if elem.text and search_word.lower() in elem.text.lower():
                # Filter by lang="en" if enabled
                if not filter_english or (elem.get("lang", "").lower() == "en"):
                    # Empty xmltv_id if enabled
                    if empty_xmltv_id and "xmltv_id" in elem.attrib:
                        elem.set("xmltv_id", "")

                    collected_channels.append(elem)

    except ET.ParseError:
        print(f"Error parsing XML file: {file_path}")

# Function to search through all XML files in a directory and its subdirectories
def search_xml_in_directory(src_dir, search_words):
    results = {word: [] for word in search_words}  # Dictionary to hold results for each word

    for root_dir, _, files in os.walk(src_dir):
        for file_name in files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                for word in search_words:
                    search_word_in_xml(file_path, word, results[word])  # Search for each word separately

    return results

# Function to write the collected <channel> elements to a new XML file
def write_channels_to_new_xml(collected_channels, output_file):
    if not collected_channels:
        print(f"No results found for {output_file}. Skipping file creation.")
        return

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Create a new XML tree with <channels> as the root
    root = ET.Element("channels")
    root.extend(collected_channels)

    # Write to file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Saved {len(collected_channels)} channels to {output_file}")

# Main function
def main():
    src_dir = "../sites"  # Folder with XML files
    search_words = ["check", "this", "out"]  # Words to search for
    output_dir = "./_Search_Results"

    search_results = search_xml_in_directory(src_dir, search_words)

    # Write results for each search word
    for word, channels in search_results.items():
        output_file = os.path.join(output_dir, f"{word}_channels.xml")
        write_channels_to_new_xml(channels, output_file)

if __name__ == "__main__":
    main()
