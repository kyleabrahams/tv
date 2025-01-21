import os
import shutil
import xml.etree.ElementTree as ET

# python3 search_xml_files.py

# Function to search for a word in an XML file
def search_word_in_xml(file_path, search_word):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Search for the word in text within the XML structure
        for elem in root.iter():
            if elem.text and search_word.lower() in elem.text.lower():
                return True
    except ET.ParseError:
        print(f"Error parsing XML file: {file_path}")
    return False

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
                    # Copy the file to the destination folder
                    shutil.copy(file_path, os.path.join(dest_dir, file_name))

# Main function to drive the search and duplication
def main():
    # Define your source directory and search word
    src_dir = '../sites'  # Replace with the directory you want to search
    search_word = 'hbo pop'  # Replace with the word you're searching for
    
    # Create a destination directory based on the search word
    search_word_safe = search_word.replace(' ', '_').replace('/', '_')
    dest_dir = f'./_Search_Results/{search_word_safe}'
    
    search_xml_in_directory(src_dir, dest_dir, search_word)

if __name__ == "__main__":
    main()