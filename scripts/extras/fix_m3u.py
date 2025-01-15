import os
import re

def fix_and_format_m3u(input_file):
    try:
        # Generate output file name based on input file name
        base_name, ext = os.path.splitext(input_file)
        output_file = f"{base_name}_fixed{ext}"  # Appends '_fixed' to the original name

        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # This will hold the corrected lines
        fixed_lines = []

        # Regular expression to capture EXTINF lines and their URLs
        pattern = r"(#EXTINF.*?)(https?://[^\s]+)"

        # Split the content into lines and process it
        matches = re.findall(pattern, content)

        # Iterate through all matches (pairs of EXTINF and URL)
        for match in matches:
            extinf_line = match[0].strip()  # Extract EXTINF line
            url_line = match[1].strip()    # Extract URL

            # Add EXTINF and URL on separate lines to fixed_lines
            fixed_lines.append(extinf_line)
            fixed_lines.append(url_line)

        # Ensure the file starts with #EXTM3U
        if fixed_lines:
            fixed_lines.insert(0, "#EXTM3U")

        # Write the cleaned and formatted data to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            for line in fixed_lines:
                file.write(line + '\n')  # Ensure each entry starts on a new line

        print(f"Fixed and formatted .m3u file saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")

# File path (Replace with the path to your .m3u file)
input_file = "/Users/kyleabrahams/Documents/GitHub/tv/bad_format.m3u"

# Run the script
fix_and_format_m3u(input_file)
