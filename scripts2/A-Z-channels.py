import xml.etree.ElementTree as ET
from xml.dom import minidom


# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/A-Z-channels.py

# Function to sort channels while preserving comments
def sort_channels_in_file(input_file, output_file):
    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Ensure the root is <channels>
        if root.tag != 'channels':
            print(f"Error: Expected root element <channels>, but found <{root.tag}>.")
            return

        channels = []
        comments = []
        other_elements = []

        for elem in list(root):
            if elem.tag == 'channel':
                channels.append(elem)
            elif isinstance(elem, ET.Comment):
                comments.append(elem)
            else:
                other_elements.append(elem)  # Keep other elements if present

        # Sort channels by their text content (name), then xmltv_id (case-insensitive)
        channels.sort(key=lambda x: ((x.text or '').strip().lower(), x.attrib.get('xmltv_id', '').lower()))

        # Clear the root and re-add elements in sorted order
        root.clear()

        for comment in comments:
            root.append(comment)

        for channel in channels:
            root.append(channel)

        for element in other_elements:
            root.append(element)

        # Convert XML to a pretty string
        xml_string = ET.tostring(root, encoding='unicode')
        pretty_xml = "\n".join([line for line in minidom.parseString(xml_string).toprettyxml(indent="  ").split("\n") if line.strip()])

        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        print(f"Sorted channels have been written to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except ET.ParseError:
        print(f"Error: Could not parse '{input_file}'. Please check the XML syntax.")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
input_file = '/Users/kyleabrahams/Documents/GitHub/tv/scripts/_epg-start/channels-custom-start-copy.xml'
output_file = '/Users/kyleabrahams/Documents/GitHub/tv/scripts/_epg-start/channels-custom-start-A-Z.xml'

sort_channels_in_file(input_file, output_file)
