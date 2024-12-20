# Script to generate an M3U playlist

# python3 playlist_generator.py

import os

def generate_m3u(start, end, base_url, output_dir, output_file_name):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the full path for the output file
    output_file = os.path.join(output_dir, output_file_name)
    
    with open(output_file, "w") as f:
        # Write the #EXTM3U header
        f.write("#EXTM3U\n\n")
        for channel in range(start, end + 1):
            f.write(f"#EXTINF:-1 ,channel {channel}\n")
            # f.write(f"{base_url}/{channel}.m3u8\n") # With .m3u8
            f.write(f"{base_url}/{channel}\n")

    print(f"M3U playlist generated: {output_file}")

# Parameters
start_channel = 46000  # Starting channel number
end_channel = 60000  # Ending channel number
# base_url = "http://xxx/xxx/xxx"  # Base URL for the streams
base_url = "http://fortv.cc:8080/105094817/105094817"  # Base URL for the streams
output_dir = "/Volumes/Kyle4tb1223/_Android/_M3U/___ServersFULL"  # Directory to save the file
output_file_name = "fortv-ccDec20.m3u"  # Output file name

# Generate the M3U playlist
generate_m3u(start_channel, end_channel, base_url, output_dir, output_file_name)
