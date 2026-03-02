# Script to generate an M3U playlist
#!/usr/bin/env python3
import os
from datetime import datetime

def generate_m3u(start, end, base_url, output_dir, output_file_name):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the full path for the output file
    output_file = os.path.join(output_dir, output_file_name)
    
    with open(output_file, "w") as f:
        # Write the #EXTM3U header
        f.write("#EXTM3U\n\n")
        for channel in range(start, end + 1):
            f.write(f"#EXTINF:-1,{channel}\n")
            # f.write(f"{base_url}/{channel}.m3u8\n") # With .m3u8
            f.write(f"{base_url}/{channel}\n")

    print(f"M3U playlist generated: {output_file}")

# Parameters
start_channel = 1  # Starting channel number
end_channel = 1000000  # Ending channel number
# base_url = "http://server/usepassword"  # Base URL for the streams

# Set the output directory relative to "/Volumes/Kyle4tb1223"
output_dir = os.path.join(os.path.expanduser('~'), "Documents/___ServersFULL")

# Include today's date in the output file name
today_date = datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD
output_file_name = f"SERVER-1-1000-{today_date}.m3u"  # Output file name with today's date

# python3 playlist_generator.py

## Tool 1. IPTV-Checker is a utility designed to verify the status of links in M3U playlists. It categorizes each link as online, offline, or a duplicate.
# IPTV-Checker global installation
# npm install -g iptv-checker
# Playlist execution
# iptv-checker /path/to/playlist.m3u -o /path/to/output/directory/ServerNameHere-$(date +%Y%m%d)
# iptv-checker /path/to/playlist.m3u -o /Users/kyleabrahams/Documents/___ServersFULL/Checked/ServerNameHere-$(date +%Y%m%d)



# Generate the M3U playlist
generate_m3u(start_channel, end_channel, base_url, output_dir, output_file_name)