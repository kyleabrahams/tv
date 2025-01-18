import xml.etree.ElementTree as ET
from xml.dom import minidom


# python3 xmltv_id.py

# Function to sort channels while preserving comments
def sort_channels_in_file(input_file, output_file):
    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Separate out comments and non-commented channels
        channels = []
        comments = []

        for elem in root:
            if isinstance(elem, ET.Element) and elem.tag == 'channel':
                channels.append(elem)
            elif isinstance(elem, ET.Comment):
                comments.append(elem)

        # Sort the channels by xmltv_id and name
        channels.sort(key=lambda x: (x.attrib['xmltv_id'], x.text))

        # Create a new XML structure with the root <channels>
        sorted_tv = ET.Element('channels')

        # Add comments back into the sorted XML structure
        for comment in comments:
            sorted_tv.append(comment)

        # Add sorted channels to the root element
        for channel in channels:
            sorted_tv.append(channel)

        # Write the sorted XML tree back to the output file
        tree = ET.ElementTree(sorted_tv)
        tree.write(output_file, encoding='unicode', xml_declaration=True)

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
input_file = '/Users/nada/Documents/GitHub/tv/scripts/_epg-start/channels_custom_start.xml'   # Replace with your input XML file path
output_file = '/Users/nada/Documents/GitHub/tv/scripts/_epg-start/channels_custom_start_output.xml'  # Replace with your desired output XML file path

sort_channels_in_file(input_file, output_file)
print(f"Sorted channels have been written to {output_file}")
