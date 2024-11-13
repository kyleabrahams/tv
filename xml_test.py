import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_epg():
    # Create the root XML element for TV guide
    tv = ET.Element("tv", generator_info_name="none", generator_info_url="none")

    # Add the channel element below <tv> tag, with no spaces between tags
    channel_elem = ET.SubElement(tv, "channel", id="TYTNetwork.us")
    display_name_elem = ET.SubElement(channel_elem, "display-name")
    display_name_elem.text = "TYT Network"
    url_elem = ET.SubElement(channel_elem, "url")
    url_elem.text = "https://xumo.tv"

    # Create multiple programme elements as children of the tv element
    programmes = [
        {"start": "20241113103000 +0000", "stop": "20241113110000 +0000", "channel": "CITYNEWS247", "title": "The Lightbulb Moment", "desc": "The surprising impact of less-celebrated inventions."},
        {"start": "20241113110000 +0000", "stop": "20241113113000 +0000", "channel": "0#99991220", "title": "Innovation Today", "desc": "A look at today's most innovative technologies."},
        {"start": "20241113113000 +0000", "stop": "20241113120000 +0000", "channel": "0#99991221", "title": "The New Era", "desc": "Exploring the future of artificial intelligence."}
    ]

    # Add programmes to the TV root element (on a single line)
    for prog in programmes:
        programme_elem = ET.SubElement(tv, "programme", start=prog["start"], stop=prog["stop"], channel=prog["channel"])
        title_elem = ET.SubElement(programme_elem, "title", lang="en")
        title_elem.text = prog["title"]
        desc_elem = ET.SubElement(programme_elem, "desc", lang="en")
        desc_elem.text = prog["desc"]

    # Create the XML tree with indentation and newlines for readability
    epg_xml = ET.tostring(tv, encoding='unicode', method='xml')

    # Add XML declaration at the start of the XML string
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'

    # Use minidom to prettify the XML and remove unnecessary newlines
    xml_str = minidom.parseString(epg_xml).toprettyxml(indent="  ")

    # Combine the XML declaration with the prettified content
    formatted_xml = xml_declaration + xml_str.strip()

    # Remove newlines to make everything appear on a single line, and remove spaces between tags
    formatted_xml = formatted_xml.replace('\n', '').replace('<channel', '\n<channel').replace('<programme', '\n<programme').replace('</tv>', '\n</tv>').replace('><', '><')

    return formatted_xml

def save_to_file(filename):
    epg_xml = create_epg()
    with open(filename, 'w') as file:
        file.write(epg_xml)

# Call the function to save to the file
save_to_file("text.xml")
