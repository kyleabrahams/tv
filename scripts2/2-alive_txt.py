import os
from datetime import datetime
import subprocess

# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/2-alive_txt.py


# Function to read server URLs from a .txt file
def read_urls_from_txt(file_path):
    try:
        with open(file_path, "r") as file:
            # Read all lines and remove extra whitespace
            server_urls = [line.strip() for line in file.readlines()]
        if not server_urls:
            raise ValueError("No data found in the specified text file!")
        return server_urls
    except Exception as e:
        print(f"❌ Error reading text file: {e}")
        raise

# Ensure the output directory exists
def create_output_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Output directory '{output_dir}' is ready.")

# Clean old M3U files
def clean_old_files(output_dir):
    for file_name in os.listdir(output_dir):
        if file_name.startswith("alive") and file_name.endswith(".m3u"):
            file_path = os.path.join(output_dir, file_name)
            os.remove(file_path)
            print(f"Removed old file: {file_path}")

# Generate M3U file
def generate_m3u_file(server_urls, output_filename):
    m3u_content = "#EXTM3U\n"
    for server_url in server_urls:
        if server_url.strip() and server_url.startswith("http://"):
            m3u_content += f"#EXTINF:-1,{server_url}\n{server_url}\n"
    
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(m3u_content)
    
    print(f"M3U playlist created: {output_filename}")

# Run a second Python script and print all subprocess output
def run_second_script(script_path):
    try:
        result = subprocess.run(
            ["python3", script_path],
            check=True,
            text=True,  # Enable text mode to handle output as string
            capture_output=True  # Capture both stdout and stderr
        )
        print(f"Second script executed successfully!\nSTDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running second script: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
        raise

def main():
    try:
        # Path to your text file with URLs
        txt_file_path = "_alive/1-alive.txt"  # Ensure this is the correct path
        # txt_file_path = "_alive/expired.txt"  # Ensure this is the correct path


        # Read URLs from the text file
        print(f"Reading URLs from: {txt_file_path}")
        server_urls = read_urls_from_txt(txt_file_path)

        # Step 1: Ensure the '_alive' directory exists
        output_dir = "_alive"
        create_output_directory(output_dir)

        # Step 2: Clean old M3U files
        clean_old_files(output_dir)

        # Step 3: Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        output_filename = f"{output_dir}/alive-txt-{timestamp}.m3u"
        # output_filename = f"{output_dir}/expired-txt-{timestamp}.m3u"


        # Step 4: Generate M3U content and save to file
        generate_m3u_file(server_urls, output_filename)

        # Step 5: Run the second Python script (if needed)
        # second_script_path = "vpn_iptv_checker-alive-txt.py"  # Specify the path to your second script
        # run_second_script(second_script_path)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()