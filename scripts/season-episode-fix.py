import os
import re
import logging

# Set up logging
logging.basicConfig(
    filename="rename_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def rename_files(media_dir):
    """
    Renames Greek media files in the given directory to follow Plex naming conventions:
    'Β' season Επεισόδιο 1' -> 'S02E01'.
    """
    # Regex pattern to match Greek season and episode naming
    pattern = re.compile(
        r"^(.*?)\s*(?:[Α-Ω']+\s?season)?\s*(?:Β'?|Γ'?|Δ'?)?\s*(?:Επεισ?)(\d+)(.*?)(\.mp4|\.avi|\.mkv|\.flv|\.mov|\.wmv)?$",
        re.IGNORECASE
    )

    # Map Greek season identifiers to numeric values
    season_map = {
        "Α": 1, "Β": 2, "Γ": 3, "Δ": 4,
        "Ε": 5, "ΣΤ": 6, "Ζ": 7, "Η": 8,
        "Θ": 9, "Ι": 10
    }

    # Counters
    processed_count = 0
    renamed_count = 0
    skipped_count = 0

    for root, _, files in os.walk(media_dir):
        for file in files:
            processed_count += 1  # Increment total processed files
            print(f"Processing file: {file}")  # Show the file being processed
            match = pattern.match(file)
            if match:
                # Extract components
                show_name, episode, rest, extension = match.groups()

                # Identify season from Greek identifier
                season = 1  # Default season
                for greek, num in season_map.items():
                    if f"{greek}'" in file:
                        season = num
                        break

                # Format the season and episode
                season_formatted = f"S{int(season):02}"
                episode_formatted = f"E{int(episode):02}"

                # Create the new name
                new_name = f"{show_name.strip()} {season_formatted}{episode_formatted}{extension if extension else '.mp4'}"

                # Full paths
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)

                # Avoid renaming if the name is already correct
                if old_path != new_path:
                    # Rename the file
                    try:
                        os.rename(old_path, new_path)
                        logging.info(f"Renamed: {old_path} -> {new_path}")
                        print(f"[{processed_count}] Renamed: {old_path} -> {new_path}")
                        renamed_count += 1
                    except Exception as e:
                        logging.error(f"Failed to rename {old_path}: {e}")
                        print(f"[{processed_count}] Failed to rename {old_path}: {e}")
                else:
                    skipped_count += 1
                    logging.warning(f"Skipping file with the same name: {file}")
                    print(f"[{processed_count}] Skipping file with the same name: {file}")
            else:
                skipped_count += 1
                logging.warning(f"Skipping unrecognized file: {file}")
                print(f"[{processed_count}] Skipping unrecognized file: {file}")

    # Summary
    print(f"\nSummary:")
    print(f"Total files processed: {processed_count}")
    print(f"Files renamed: {renamed_count}")
    print(f"Files skipped: {skipped_count}")
    
if __name__ == "__main__":
    # Replace this with the path to your media directory
    media_directory = "'/Volumes/Kyle4tb1223/__Steve/Βουράτε Γειτόνοι (2001-2010)'"
    rename_files(media_directory)
