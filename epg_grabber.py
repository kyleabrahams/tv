import argparse
import logging
import asyncio
import aiohttp
from pathlib import Path
import xml.etree.ElementTree as ET
import gzip
from datetime import datetime
import os
import glob
import subprocess
import sys

# Run the site grabber
# chmod +r epg_grabber.py
# python3 epg_grabber.py -s "https://raw.githubusercontent.com/iptv-org/epg/master/sites/xumo.tv/xumo.channels.xml" -o "/usr/local/var/www/xumo.xml"

# Step 1: Attempt to import aiohttp, and if it fails, install it using pip
try:
    import aiohttp
except ImportError:
    print("aiohttp module not found. Installing it now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])

# Now, we can safely import it after installation
import aiohttp

# Step 2: Configure logging to track progress and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 3: Parse command-line arguments
def parse_args():
    """
    Parse command-line arguments for the program.
    """
    parser = argparse.ArgumentParser(description="EPG Grabber")  # Initialize argument parser
    parser.add_argument('-s', '--site', help='Name of the site to parse')  # URL for the site
    parser.add_argument('-c', '--channels', help='Path to *.channels.xml file')  # Local file path for channels
    parser.add_argument('-o', '--output', default='./output/xumo.xml', help='Path to output file')  # Output file path
    parser.add_argument('-l', '--lang', help='Filter channels by language (ISO 639-2 code)')  # Language filter
    parser.add_argument('-t', '--timeout', type=int, help='Timeout for each request in milliseconds')  # Timeout
    parser.add_argument('-d', '--delay', type=int, help='Delay between requests in milliseconds')  # Delay
    parser.add_argument('--days', type=int, help='Number of days of data to grab')  # Number of days to fetch
    parser.add_argument('--maxConnections', type=int, default=1, help='Max concurrent requests')  # Max concurrent connections
    parser.add_argument('--cron', help='Cron schedule expression (e.g., "0 0 * * *")')  # Cron schedule (optional)
    parser.add_argument('--gzip', action='store_true', help='Compress the output as gzip')  # Option for gzip compression
    return parser.parse_args()  # Return parsed arguments

# Step 4: Fetch URL content asynchronously with semaphore for concurrency
async def fetch_url_with_semaphore(session, url, timeout, semaphore):
    """
    Fetch the URL content asynchronously with a limit on concurrency.
    """
    async with semaphore:  # Limit concurrent requests using the semaphore
        try:
            async with session.get(url, timeout=timeout / 1000) as response:  # Fetch the URL content
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}, status code: {response.status}")  # Log errors if response is not 200
                    return None
                data = await response.text()  # Read the content
                logger.info(f"Fetched data from {url[:50]}...")  # Log a preview of the fetched data
                return data
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")  # Log error if fetching fails
            return None

# Step 5: Parse channel data from XML files
async def parse_channels(file_path_pattern, lang_filter=None):
    """
    Parse channel data from one or more XML files.
    """
    logger.info(f"Parsing channels from {file_path_pattern}")  # Log start of channel parsing
    all_files = glob.glob(file_path_pattern)  # Get all files matching the path pattern
    channels = []  # Initialize a list to store channel data

    # Loop through each file found
    for file_path in all_files:
        tree = ET.parse(file_path)  # Parse the XML file
        root = tree.getroot()  # Get the root of the XML tree
        for channel in root.findall('channel'):  # Loop through each channel in the XML
            lang = channel.find('lang').text if channel.find('lang') is not None else None  # Check the language
            if not lang_filter or lang == lang_filter:  # Filter channels by language if specified
                channels.append(channel)  # Add the channel to the list

    logger.info(f"Found {len(channels)} channel(s) across {len(all_files)} file(s)")  # Log the number of channels found
    return channels  # Return the list of channels

# Step 6: Parse the program data from the fetched content
def parse_program_data(data):
    """
    Parse the program data from the fetched XML content.
    """
    program_data = []  # List to store program data
    tree = ET.ElementTree(ET.fromstring(data))  # Parse the fetched XML data
    root = tree.getroot()  # Get the root of the XML tree

    # Loop through each programme in the XML
    for programme in root.findall('programme'):
        title = programme.find('title').text
        start_time = programme.find('start').text
        description = programme.find('desc').text if programme.find('desc') is not None else ''
        program_data.append({
            'title': title,
            'start_time': start_time,
            'description': description,
            'channel': programme.get('channel')  # Assuming 'channel' attribute is present
        })

    return program_data  # Return the parsed program data

# Step 7: Write the output to the file (either as XML or GZipped)
def write_output_file(program_data, output_path, options):
    """
    Write the parsed program data to a file (either as regular XML or compressed with gzip).
    """
    # Write XML data to the output file
    with open(output_path, 'w') as f:
        f.write("<guide>\n")
        for programme in program_data:
            f.write(f"<programme start='{programme['start_time']}' channel='{programme['channel']}'>\n")
            f.write(f"  <title>{programme['title']}</title>\n")
            f.write(f"  <desc>{programme['description']}</desc>\n")
            f.write('</programme>\n')
        f.write('</guide>\n')

    # If gzip is enabled, create a gzipped version of the output file
    if options.gzip:
        with open(output_path, 'rb') as f_in, gzip.open(f"{output_path}.gz", 'wb') as f_out:
            f_out.writelines(f_in)
        logger.info(f"Gzip file created at {output_path}.gz")

# Step 8: Main job execution for fetching data and writing output
async def run_job(channels, output_path, options):
    """
    Main job execution for fetching data from channels and writing the output to a file.
    """
    logger.info("Starting job...")

    semaphore = asyncio.Semaphore(options.maxConnections)  # Limit the number of concurrent requests

    # Create an aiohttp session for making requests
    async with aiohttp.ClientSession() as session:
        tasks = []  # List to hold the tasks for fetching URLs
        for channel in channels:
            url = channel.find('url').text  # Get the URL of the channel
            tasks.append(fetch_url_with_semaphore(session, url, options.timeout, semaphore))  # Add task to the list

        results = await asyncio.gather(*tasks)  # Fetch all URLs concurrently

        program_data = []  # List to store program data
        for data in results:
            if data:
                program_data.extend(parse_program_data(data))  # Parse the program data and add it to the list

        write_output_file(program_data, output_path, options)  # Write the output to the specified file

# Step 9: Main program entry point
async def main():
    """
    The main entry point for the program.
    """
    options = parse_args()  # Parse the command-line arguments
    if not options.site and not options.channels:  # Ensure either --site or --channels is provided
        raise ValueError("Either --site or --channels must be specified.")

    logger.info("Starting EPG Grabber...")  # Log that the grabber is starting

    # If the --site option is provided, fetch the channel data from the site
    if options.site:
        channels = await parse_channels(options.site, lang_filter=options.lang)
    else:
        channels = await parse_channels(options.channels or f"./sites/*.channels.xml", lang_filter=options.lang)

    # Start the job with the parsed channels and output to the specified file
    await run_job(channels, options.output, options)

# Step 10: Run the script if this file is executed as the main program
if __name__ == "__main__":
    asyncio.run(main())  # Run the main async function