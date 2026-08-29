import os
import requests
from mutagen.easyid3 import EasyID3

# 1. Configuration
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
GOOGLE_CX = "YOUR_SEARCH_ENGINE_ID"
MP3_FILE_PATH = "your_song.mp3"

def search_release_year(track_name, artist_name):
    """Searches Google for the release year of a track."""
    query = f"{track_name} {artist_name} release year"
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        # Look for snippet or title content containing a 4-digit year
        if "items" in search_results:
            for item in search_results["items"]:
                snippet = item.get("snippet", "")
                title = item.get("title", "")
                text_to_search = f"{title} {snippet}"
                
                # Simple extraction of a 4-digit number between 1900 and 2030
                import re
                years = re.findall(r'\b(19\d{2}|20[0-2]\d|2030)\b', text_to_search)
                if years:
                    return years[0]  # Return the first found year
    except Exception as e:
        print(f"Error fetching data from Google API: {e}")
        
    return None

def tag_mp3_date(file_path, year):
    """Writes the year to the MP3 file's ID3 tags."""
    try:
        # Load or initialize EasyID3 tags
        try:
            audio = EasyID3(file_path)
        except Exception:
            # If no ID3 tag exists, create one
            from mutagen.id3 import ID3
            meta = ID3()
            meta.save(file_path)
            audio = EasyID3(file_path)
            
        audio['date'] = str(year)
        audio.save()
        print(f"Successfully tagged {file_path} with year {year}")
    except Exception as e:
        print(f"Error tagging MP3 file: {e}")

# 2. Execution Workflow
if __name__ == "__main__":
    # Example track details (You can extract these dynamically using mutagen)
    track = "Blinding Lights"
    artist = "The Weeknd"
    
    print(f"Searching Google for the release year of '{track}' by {artist}...")
    found_year = search_release_year(track, artist)
    
    if found_year:
        print(f"Found year: {found_year}")
        tag_mp3_date(MP3_FILE_PATH, found_year)
    else:
        print("Could not reliably determine the release year from Google Search results.")
