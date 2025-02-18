#!/usr/bin/env python3

# merge_epg.py Feb 10 2025 808p
import requests
import xml.etree.ElementTree as ET
import os
import gzip
import io
import subprocess
from time import sleep
import sys
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
import re
import pytz

# Define REPO_DIR at the top of merge_epg.py if it's not already defined
REPO_DIR = os.path.abspath(os.path.dirname(__file__))  # This will set REPO_DIR to the script's directory
venv_python = sys.executable  # Relative path from the script to the virtual environment
print(venv_python)
print("Starting data processing...")
# your data processing code
print("Data processing complete.")

# Step 1: Set up Logging
formatted_time = datetime.now().strftime("%b %d %Y %H:%M:%S")
print(formatted_time)

# Define SuccessFilter to filter messages
class SuccessFilter(logging.Filter):
    def filter(self, record):
        return "EPG file successfully saved" in record.getMessage()

# Get the directory where the script is located (absolute path)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create the relative path for the log file
log_file_path = os.path.join(script_dir, 'www', 'merge_epg.log')

# Ensure the 'www' directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Set up logging configuration
log_format = "%(asctime)s - %(message)s"
date_format = "%b %d %Y %H:%M:%S"

logging.basicConfig(filename=log_file_path,
                    level=logging.INFO,
                    format=log_format,
                    datefmt=date_format)

# Create a logger instance
logger = logging.getLogger(__name__)

# Create a RotatingFileHandler
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5 * 1024 * 1024, backupCount=4  # 5 MB file size limit, keep 4 backups
)

# Set up the formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the SuccessFilter to filter specific messages
file_handler.addFilter(SuccessFilter())

# Add the file handler to the logger
logger.addHandler(file_handler)

# Log starting message
logger.info("Starting EPG merge process...")

# Step 1. NPM run grab channels
def run_npm_grab():
    # Get current date and time for timestamping the output file
    current_datetime = datetime.now().strftime("%m-%d-%I-%M-%S %p")
    
    # List of npm commands with timestamped output file
    commands = [
        ["npm", "run", "grab", "--", 
        #  f"--channels=./scripts/_epg-start/channels-custom-start.xml", 
        #  f"--output=./scripts/_epg-end/channels-custom-{current_datetime}.xml"]

         f"--channels=./scripts/_epg-start/channels-test-start.xml", 
         f"--output=./scripts/_epg-end/channels-test-end.xml"]

        #  f"--channels=./scripts/_epg-start/channels-test-start-copy.xml", 
        #  f"--output=./scripts/_epg-end/channels-test-copy{current_datetime}.xml"]

    ]

    
    # Set the output directory for deleting old files
    output_dir = os.path.join(script_dir, "_epg-end")
    
    # Delete all older files except the latest one
    try:
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)

            # Check if the file matches the pattern 'channels-YYYY-MM-DD-HH-MM-SS.xml' and is not the latest file
            if file_name.startswith("channels-") and file_name != f"channels-{current_datetime}.xml":
                os.remove(file_path)
                print(f"Old file {file_path} deleted.")
    except Exception as e:
        print(f"Error deleting old files: {e}")

    for command in commands:
        try:
            # Combine the command into a string for logging and display
            command_str = ' '.join(command)
            logger.info(f"Running command: {command_str}")
            print(f"Running command: {command_str}")

            # Run the command and capture output
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            stdout_output = []
            stderr_output = []

            # Process stdout and capture lines
            for line in process.stdout:
                stripped_line = line.strip()
                stdout_output.append(stripped_line)
                logger.info(f"STDOUT: {stripped_line}")
                print(f"STDOUT: {stripped_line}")

            # Process stderr and capture lines
            for line in process.stderr:
                stripped_line = line.strip()
                stderr_output.append(stripped_line)
                logger.error(f"STDERR: {stripped_line}")
                print(f"STDERR: {stripped_line}")

            # Wait for process completion
            process.wait()

            # Check for successful execution
            if process.returncode == 0:
                logger.info(f"Command {command_str} executed successfully.")
                print(f"Command {command_str} executed successfully.")

                # Extract and log the number of channels found
                channel_count_pattern = r"found (\d+) channel\(s\)"
                for line in stdout_output:
                    match = re.search(channel_count_pattern, line)
                    if match:
                        channel_count = match.group(1)
                        logger.info(f"Found {channel_count} channel(s) in the output.")
                        print(f"Found {channel_count} channel(s) in the output.")
                        break  # Stop after the first match

            else:
                logger.error(f"Command {command_str} failed with error code {process.returncode}.")
                print(f"Command {command_str} failed with error code {process.returncode}.")

        except Exception as e:
            logger.error(f"Error while running npm command {command_str}: {e}")
            print(f"Error while running npm command {command_str}: {e}")

# Run the process
if __name__ == "__main__":
    run_npm_grab()
