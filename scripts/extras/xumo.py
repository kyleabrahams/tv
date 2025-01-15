import subprocess
import sys
# Try to import schedule module, if not found install it
try:
    import schedule
except ImportError:
    print("schedule module not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule  # Try importing again after installation
import argparse
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from time import time
import time as system_time
from threading import Thread


# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SITES_DIR = './sites'  # Directory for site-specific channel data

# Get the directory of the script and construct a relative path
script_dir = Path(__file__).parent.resolve()
default_output = script_dir / "xumo.xml"

# Step 1: Define command-line arguments using argparse
def parse_args():
    parser = argparse.ArgumentParser(description="Xumo EPG Data Generator")
    parser.add_argument('-s', '--site', type=str, help="Name of the site to parse")
    parser.add_argument('-c', '--channels', type=str, help="Path to *.channels.xml file (required if --site is not specified)")
    parser.add_argument('-o', '--output', type=str, default=str(default_output), help="Path to output file")
    parser.add_argument('-l', '--lang', type=str, help="Filter channels by language (ISO 639-2 code)")
    parser.add_argument('-t', '--timeout', type=int, help="Override the default timeout for each request")
    parser.add_argument('-d', '--delay', type=int, help="Override the default delay between requests")
    parser.add_argument('--days', type=int, help="Override the number of days for which the program will be loaded")
    parser.add_argument('--maxConnections', type=int, default=1, help="Limit on the number of concurrent requests")
    parser.add_argument('--cron', type=str, help="Schedule a script run (example: '0 0 * * *')")
    parser.add_argument('--gzip', action='store_true', help="Create a compressed version of the guide")
    return parser.parse_args()

# Step 2: Load channels based on site or channels path
def load_channels(args):
    files = []
    if args.site:
        pattern = os.path.join(SITES_DIR, args.site, '*.channels.xml')
        files = [str(path) for path in Path().glob(pattern)]
    elif args.channels:
        files = [args.channels]

    # Simulating channel loading and parsing
    channels = []
    for file in files:
        with open(file, 'r') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            channels.extend([channel.text for channel in root.findall('.//channel')])
    
    return channels

# Step 3: Filter channels by language if provided
def filter_channels(channels, lang):
    if lang:
        return [channel for channel in channels if channel.lang == lang]
    return channels

# Step 4: Create a queue based on parsed channels (simplified version)
def create_queue(channels):
    return channels  # In reality, you would queue these for processing

# Step 5: Simulate running the job (in this case, just writing the XML to a file)
def run_job(channels, output_file):
    logger.info("Running job with channels: %s", channels)
    root = ET.Element("guide")
    for channel in channels:
        channel_elem = ET.SubElement(root, "channel")
        channel_elem.text = channel
    
    tree = ET.ElementTree(root)
    tree.write(output_file)
    logger.info("Job complete. Output written to %s", output_file)

# Step 6: Set up a cron job or run immediately
def schedule_task(job_func, channels, output_file, cron_expr=None):
    if cron_expr:
        logger.info(f"Scheduling task with cron expression: {cron_expr}")
        schedule.every().day.at(cron_expr).do(job_func, channels, output_file)
        
        # Running the scheduler in a separate thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                system_time.sleep(1)
        Thread(target=run_scheduler, daemon=True).start()
    else:
        logger.info("Running job immediately.")
        job_func(channels, output_file)

# Main execution flow
def main():
    args = parse_args()

    # Step 1: Load channels
    logger.info('Loading channels...')
    channels = load_channels(args)

    logger.info(f"Found {len(channels)} channel(s)")

    # Step 2: Filter channels by language if necessary
    if args.lang:
        channels = filter_channels(channels, args.lang)
    
    # Step 3: Create queue (this is just a placeholder in the Python example)
    queue = create_queue(channels)

    # Step 4: Schedule the job or run immediately
    schedule_task(run_job, channels, args.output, args.cron)

    # This is to keep the script running if a cron job is set
    if args.cron:
        while True:
            system_time.sleep(1)
    else:
        logger.info(f"Job completed, output saved to {args.output}")

if __name__ == '__main__':
    start_time = time()
    main()
    logger.info(f"Script executed in {time() - start_time:.2f} seconds")
