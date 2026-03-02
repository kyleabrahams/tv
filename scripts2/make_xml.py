# Step 4: Main merge_epg function
def merge_epg_data():
    """Coordinates the EPG generation and merging process."""

    print("Merging EPG data...") # Proceed with EPG merging logic

# Execute the process
if __name__ == "__main__":
    merge_epg_data()

# Step 5: Function to read the EPG URLs from a file
def load_epg_urls(file_path):
    """Read EPG URLs from the specified file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            epg_urls = [line.strip() for line in file.readlines() if line.strip()]  # Remove empty lines and strip whitespace
        return epg_urls
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

# Step 6: Check for XML files if no URLs are found
def load_local_xml_files(directory):
    """Look for XML files in the directory if no EPG URLs are found."""
    xml_files = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                xml_files.append(os.path.join(directory, filename))  # Add XML file path to the list
        return xml_files
    except Exception as e:
        print(f"Error loading XML files from {directory}: {e}")
        return []

# Get the directory where the script is located (absolute path)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # Ensure the 'log' directory exists

# Relative path to the epg_urls.txt file
epg_urls_file = os.path.join(script_dir, '_epg-start', 'epg_urls.txt')

# Load EPG URLs using the relative path
epg_urls = load_epg_urls(epg_urls_file)

# Check if URLs are found, if not, look for XML files in the _epg-end directory
if not epg_urls:
    # Use a relative path to the _epg-end directory
    epg_end_dir = os.path.join(script_dir, '_epg-end')  # Relative path to _epg-end directory
    print(f"No EPG URLs found in {epg_urls_file}, scanning {epg_end_dir} for XML files...")
    epg_urls = load_local_xml_files(epg_end_dir)

# Print out the list of EPG URLs or local XML files found
print("EPG URLs or local XML files found:", epg_urls)

# Step 7: Path to save the merged EPG file
save_path = os.path.join(REPO_DIR, "www", "epg.xml")  # Path where the EPG file will be saved
gz_directory = os.path.join(REPO_DIR, "www")  # Directory where .gz files are located

# Step 8: Function to ensure directory and file permissions
def ensure_permissions(file_path):
    # Ensure the directory exists
    directory = os.path.dirname(file_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it...")
        os.makedirs(directory, exist_ok=True)

    # Check if we have write permissions on the directory, and if not, set it
    if not os.access(directory, os.W_OK):
        print(f"Directory {directory} does not have write permissions. Updating permissions...")
        os.chmod(directory, 0o755)  # Set write permission for the directory owner

    # If the file already exists, check and ensure it has write permissions
    if os.path.exists(file_path):
        if not os.access(file_path, os.W_OK):
            print(f"File {file_path} does not have write permissions. Updating permissions...")
            os.chmod(file_path, 0o644)  # Set write permission for the file owner
    else:
        print(f"File {file_path} does not exist. It will be created.")

# Ensure permissions for the save path
ensure_permissions(save_path)


# Step 9: Function to fetch and merge EPG data
def fetch_epg_data(url, index, total, retries=3, delay=5):
    logging.info(f"Fetching {index + 1}/{total} - {url}")
    print(f"Fetching {index + 1}/{total} - {url}")

    attempt = 0
    while attempt < retries:
        try:
            if url.startswith('http'):  # Step 5.1: Handle remote URLs
                response = requests.get(url, timeout=10)  # Timeout to avoid hanging
                if response.status_code == 200:
                    try:
                        if url.endswith('.gz'):  # Step 5.2: Handle .gz files (compressed XML)
                            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                                xml_content = gz.read()
                            epg_tree = ET.ElementTree(ET.fromstring(xml_content))
                        else:
                            epg_tree = ET.ElementTree(ET.fromstring(response.content))
                        print(f"Successfully fetched {index + 1}/{total}")
                        logging.info(f"Successfully fetched {index + 1}/{total}")
                        return epg_tree
                    except ET.ParseError as e:
                        logging.error(f"XML parse error for {url}: {e}")
                        print(f"XML parse error for {url}: {e}")
                        return None
                    except Exception as e:
                        logging.error(f"Error processing {url}: {e}")
                        print(f"Error processing {url}: {e}")
                        return None
                else:
                    logging.error(f"Error fetching {url}: HTTP {response.status_code}")
                    print(f"Error fetching {url}: HTTP {response.status_code}")
                    return None
            else:  # Step 5.3: Handle local XML files
                try:
                    epg_tree = ET.parse(url)
                    print(f"Successfully loaded local file: {url}")
                    logging.info(f"Successfully loaded local file: {url}")
                    return epg_tree
                except ET.ParseError as e:
                    logging.error(f"Failed to parse local XML file {url}: {e}")
                    print(f"Failed to parse local XML file {url}: {e}")
                except Exception as e:
                    logging.error(f"Error processing local file {url}: {e}")
                    print(f"Error processing local file {url}: {e}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            attempt += 1
            time.sleep(delay)  # Wait before retrying
    return None  # Return None after all attempts fail    

# Function to extract XML from .gz files
import log
def extract_gz_files(gz_directory):
    """Extract .gz files in the specified directory."""
    # Make sure you're using the correct directory
    gz_directory = os.path.join(REPO_DIR, "www")  # Ensure this points to the right directory

    if not os.path.exists(gz_directory):
        log(f"Error: Directory {gz_directory} does not exist.")
        return []

    extracted_files = []
    for filename in os.listdir(gz_directory):
        if filename.endswith(".gz"):
            file_path = os.path.join(gz_directory, filename)
            log(f"Extracting {file_path}...")
            # Your extraction code here
            extracted_files.append(file_path)
    return extracted_files


# Step 10: Merge EPG data into a single XML
merged_root = ET.Element("tv")
total_files = len(epg_urls)


# Step 11: Process each EPG URL
for index, url in enumerate(epg_urls):
    epg_tree = fetch_epg_data(url, index, total_files)
    if epg_tree:
        for element in epg_tree.getroot():
            merged_root.append(element)
    sleep(0.5)  # Small delay to simulate and visualize progress


# Step 12: Extract XML from .gz files
print("Extracting XML from .gz files...")
extracted_files = extract_gz_files(gz_directory)
for xml_file in extracted_files:
    try:
        epg_tree = ET.parse(xml_file)
        for element in epg_tree.getroot():
            merged_root.append(element)
    except ET.ParseError as e:
        logging.error(f"Failed to parse extracted XML file {xml_file}: {e}")
        print(f"Failed to parse extracted XML file {xml_file}: {e}")



# Step 13: Save the merged EPG file after merging data
save_path = "www/epg.xml"  # Set your desired save path
try:
    save_dir = os.path.dirname(save_path)
    os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

    # Get the current Eastern Time
    current_time_et = datetime.now().strftime("%b %d, %Y %I:%M:%S %p")

    # Step 13: Save the merged EPG/log file and push to Github
    # Define directories to auto-commit
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directories_to_commit = [
        os.path.join(script_dir, "www"),
        os.path.join(script_dir, "_epg-end")
    ]

    # Add a check for the "scripts" directory
    additional_directory = os.path.join(script_dir, "scripts")
    if os.path.exists(additional_directory):
        directories_to_commit.append(additional_directory)

    # Set up logging
    logging.basicConfig(filename="merge_epg.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Make sure merged_root exists and is valid
    # merged_root = ... (Ensure merged_root is created and populated with the merged XML data)

    # Create the merged XML file
    merged_tree = ET.ElementTree(merged_root)
    save_path = os.path.join(script_dir, "www", "epg.xml")
    merged_tree.write(save_path, encoding="utf-8", xml_declaration=True)

    # Log success message
    success_message = f"EPG file successfully saved to {save_path} at {current_time_et} ET"
    logging.info(success_message)  # Log to merge_epg.log
    print(success_message)  # Echo success to console

    # Stage all files (modified & untracked) before committing
    print("Staging all updated files for commit...")
    subprocess.run(["git", "add", "--all"], check=True)  # Stage all files (new, modified, deleted)

    # Check if there are uncommitted changes and commit them
    result = subprocess.run(["git", "diff-index", "--quiet", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:  # If there are uncommitted changes
        commit_message = f"Saving uncommitted changes before rebase at {current_time_et} ET"
        print(f"Uncommitted changes detected. Committing changes with message: {commit_message}")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

    # Fetch latest changes from the remote repository
    print("Fetching latest changes from the remote repository...")
    subprocess.run(["git", "fetch"], check=True)

    # Attempt to rebase onto the latest changes from origin/main
    print("Attempting to rebase onto the latest changes from origin/main...")
    result = subprocess.run(["git", "rebase", "origin/main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print("Rebase failed. Aborting and notifying user.")
        subprocess.run(["git", "rebase", "--abort"], check=True)
        logging.error("Rebase aborted due to conflicts. Please resolve manually.")
        raise subprocess.CalledProcessError(result.returncode, result.args)

    # Push changes to GitHub after successful rebase
    print("Pushing changes to GitHub...")
    subprocess.run(["git", "push", "origin", "main", "--force-with-lease"], check=True)

    print("All files in the specified directories successfully committed and pushed to GitHub.")

except subprocess.CalledProcessError as e:
    # Log error if git operations fail
    error_message = f"Failed to commit, rebase, or push files - Error: {e}"
    logging.error(error_message)
    print(error_message)

except Exception as e:
    # Handle unexpected errors
    unexpected_error_message = f"An unexpected error occurred - {str(e)}"
    logging.error(unexpected_error_message)
    print(unexpected_error_message)
