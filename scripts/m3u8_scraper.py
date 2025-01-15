import requests
from bs4 import BeautifulSoup
import re

def find_m3u8_links(url):
    """
    Finds all .m3u8 links on the given webpage.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        list: A list of .m3u8 links found on the page.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links (<a> tags with href attributes)
        links = soup.find_all('a', href=True)

        # Use regex to filter .m3u8 links
        m3u8_links = [link['href'] for link in links if re.search(r'\.m3u8$', link['href'])]

        return m3u8_links
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def save_as_m3u(m3u8_links, output_file):
    """
    Saves the .m3u8 links to a .m3u playlist file.

    Args:
        m3u8_links (list): List of .m3u8 links to include in the playlist.
        output_file (str): File path for the .m3u file.
    """
    try:
        with open(output_file, 'w') as file:
            file.write("#EXTM3U\n")  # Write the M3U file header
            for link in m3u8_links:
                file.write("#EXTINF:-1,Sample Channel\n")  # Placeholder channel name
                file.write(f"{link}\n")
        print(f".m3u file successfully created at {output_file}")
    except Exception as e:
        print(f"An error occurred while creating the .m3u file: {e}")

# Example usage
url = "http://fl1.moveonjoy.com/"
m3u8_links = find_m3u8_links(url)

if m3u8_links:
    print("Found .m3u8 links:")
    for link in m3u8_links:
        print(link)

    # Save the .m3u8 links to an .m3u file
    output_file = "playlist.m3u"
    save_as_m3u(m3u8_links, output_file)
else:
    print("No .m3u8 links found.")
