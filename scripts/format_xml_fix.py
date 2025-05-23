import os
import shutil
import xml.etree.ElementTree as ET
from tkinter import Tk
from tkinter.filedialog import askdirectory
from xml.dom import minidom

# brew install tcl-tk
# python3 format_xml_fix.py


# Function to search for a word in an XML file
def search_word_in_xml(file_path, search_word):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for elem in root.iter():
            if elem.text and search_word.lower() in elem.text.lower():
                return True
    except ET.ParseError:
        print(f"Error parsing XML file: {file_path}")
    return False

# Function to pretty print and fix XML formatting
def pretty_print_xml(xml_string):
    try:
        # Parse the XML string into a DOM object and pretty print it
        xml_dom = minidom.parseString(xml_string)
        return xml_dom.toprettyxml(indent="  ")
    except Exception as e:
        print(f"Error pretty printing XML: {e}")
        return xml_string

# Function to search through all XML files in a directory and its subdirectories
def search_xml_in_directory(src_dir, dest_dir, search_word):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for root_dir, dirs, files in os.walk(src_dir):
        for file_name in files:
            if file_name.endswith('.xml'):
                file_path = os.path.join(root_dir, file_name)
                if search_word_in_xml(file_path, search_word):
                    print(f"Found '{search_word}' in {file_name}. Copying...")
                    
                    # Read the XML file content
                    with open(file_path, 'r', encoding='utf-8') as file:
                        xml_content = file.read()
                    
                    # Pretty print the XML content to ensure consistent formatting
                    formatted_xml = pretty_print_xml(xml_content)
                    
                    # Write the formatted XML to the destination folder
                    dest_file_path = os.path.join(dest_dir, file_name)
                    with open(dest_file_path, 'w', encoding='utf-8') as dest_file:
                        dest_file.write(formatted_xml)

# Main function to select directories and perform the search
def main():
    # Create a GUI root window (hidden)
    Tk().withdraw()

    # Ask the user to select the source directory
    print("Select the source directory containing XML files:")
    src_dir = askdirectory(title="'/Users/kyleabrahams/Documents/GitHub/tv/scripts/www/epg copy.xml'")
    if not src_dir:
        print("No source directory selected. Exiting.")
        return
    
    # Ask the user to select the destination directory
    print("Select the destination directory to save results:")
    dest_dir = askdirectory(title="'/Users/kyleabrahams/Documents/GitHub/tv/scripts/www/epg.xml'")
    if not dest_dir:
        print("No destination directory selected. Exiting.")
        return

    # Ask the user to input the search word
    search_word = input("Enter the word to search in XML files: ").strip()
    if not search_word:
        print("No search word entered. Exiting.")
        return

    # Perform the search
    search_xml_in_directory(src_dir, dest_dir, search_word)
    print(f"Search completed! Results saved to {dest_dir}")

if __name__ == "__main__":
    main()