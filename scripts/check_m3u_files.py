import os
import requests
from pathlib import Path

def check_m3u_files(directory):
    """
    Check if the URLs in .m3u files in a given directory are online.
    
    Args:
        directory (str): Path to the directory containing .m3u files.
    """
    # Create directories for ONLINE and OFFLINE files
    online_dir = os.path.join(directory, "ONLINE")
    offline_dir = os.path.join(directory, "OFFLINE")
    Path(online_dir).mkdir(exist_ok=True)
    Path(offline_dir).mkdir(exist_ok=True)

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".m3u"):
            filepath = os.path.join(directory, filename)
            print(f"Checking URLs in: {filename}")
            online, offline = check_m3u_file(filepath)
            
            # Move the file to the appropriate directory
            if len(offline) == 0:  # All URLs are online
                os.rename(filepath, os.path.join(online_dir, filename))
            else:  # Some or all URLs are offline
                os.rename(filepath, os.path.join(offline_dir, filename))
            print("\n")

def check_m3u_file(filepath):
    """
    Check if the URLs in a single .m3u file are online.
    
    Args:
        filepath (str): Path to the .m3u file.
        
    Returns:
        (list, list): Lists of online and offline URLs.
    """
    online_urls = []
    offline_urls = []
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith("http"):
                    if check_url(line.strip()):
                        online_urls.append(line.strip())
                    else:
                        offline_urls.append(line.strip())
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
    return online_urls, offline_urls

def check_url(url):
    """
    Check if a single URL is online.
    
    Args:
        url (str): The URL to check.
        
    Returns:
        bool: True if the URL is online, False otherwise.
    """
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            print(f"ONLINE: {url}")
            return True
        else:
            print(f"OFFLINE: {url} (Status code: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"OFFLINE: {url} (Error: {e})")
        return False

if __name__ == "__main__":
    # Specify the directory containing .m3u files
    directory = "/Volumes/Kyle4tb1223/_Android/_M3U/___Servers/cord cutter"  # Replace with your directory path
    if os.path.exists(directory):
        check_m3u_files(directory)
    else:
        print(f"Directory not found: {directory}")
