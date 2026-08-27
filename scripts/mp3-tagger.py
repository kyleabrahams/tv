import os
import re
import urllib.request
import json
import time
import musicbrainzngs
from mutagen.mp4 import MP4, MP4Tags, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC

# Initialize MusicBrainz
musicbrainzngs.set_useragent("MyMultiFormatMusicTagger", "9.0", "your_email@example.com")

# Target music folder path
MUSIC_FOLDER = "/Volumes/Kyle4tb1223/__Spotube/1970's & before TEST"

def clean_search_term(text):
    """Strips away common distracting tags like remaster dates from queries."""
    text = re.sub(r'\b\d{4}\s+Remaster\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bRemaster(ed)?\b', '', text, flags=re.IGNORECASE)
    return text.strip().strip("-").strip()

def fetch_song_and_art_details(str_a, str_b):
    """
    Queries MusicBrainz. Prioritizes the absolute oldest original release year 
    associated with the song recording entry.
    """
    clean_a = clean_search_term(str_a)
    clean_b = clean_search_term(str_b)
    
    permutations = [(clean_a, clean_b), (clean_b, clean_a)]
    
    for artist_query, title_query in permutations:
        if not artist_query or not title_query:
            continue
        try:
            query = f'artist:"{artist_query}" AND recording:"{title_query}"'
            result = musicbrainzngs.search_recordings(query=query, limit=5)
            
            if not result.get('recording-list'):
                continue

            for recording in result['recording-list']:
                official_title = recording.get('title')
                recording_first_date = recording.get('first-release-date')
                
                official_artist = None
                if 'artist-credit' in recording and len(recording['artist-credit']) > 0:
                    credit = recording['artist-credit']
                    if isinstance(credit, dict) and 'artist' in credit:
                        official_artist = credit['artist'].get('name')
                
                if 'release-list' in recording:
                    for release in recording['release-list']:
                        album = release.get('title')
                        release_id = release.get('id')
                        date_to_parse = recording_first_date if recording_first_date else release.get('date')
                        
                        if album and date_to_parse and release_id and official_artist and official_title:
                            year_match = re.search(r'\b\d{4}\b', date_to_parse)
                            year = year_match.group(0) if year_match else None
                            if year:
                                return official_artist, official_title, album, year, release_id
        except Exception:
            pass
            
    return None, None, None, None, None

def download_album_art(release_id):
    """Fetches raw image bytes from the Cover Art Archive API."""
    url = f"https://coverartarchive.org{release_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MyMultiFormatMusicTagger/9.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data and 'images' in data and len(data['images']) > 0:
                image_url = data['images'].get('image')
                if image_url:
                    img_req = urllib.request.Request(image_url, headers={'User-Agent': 'MyMultiFormatMusicTagger/9.0'})
                    with urllib.request.urlopen(img_req) as img_response:
                        return img_response.read()
    except Exception:
        pass
    return None

def process_and_tag_files(folder_path):
    # Import tqdm dynamically here to keep script self-contained for uv execution
    from tqdm import tqdm

    if not os.path.exists(folder_path):
        print(f"Error: Target path '{folder_path}' does not exist.")
        return

    # First pass: Gather and filter only valid target music files to size the bar accurately
    all_files = os.listdir(folder_path)
    valid_files = [
        f for f in all_files 
        if not (f.startswith('.') or f.startswith('._')) and os.path.splitext(f)[1].lower() in ['.mp3', '.m4a']
    ]

    if not valid_files:
        print("No valid .mp3 or .m4a audio tracks detected in target directory.")
        return

    print(f"Initializing Multi-Format Engine on: {folder_path}")
    print(f"Found {len(valid_files)} audio tracks to evaluate.\n")
    
    processed_count = 0

    # Wrap loop sequence with a custom, sleek tqdm terminal progress visualization bar
    with tqdm(valid_files, desc="Processing Library", unit="track", bar_format="{l_bar}{bar:30}{r_bar}{bar:-10b}") as pbar:
        for filename in pbar:
            name_only, ext = os.path.splitext(filename)
            ext = ext.lower()
            original_filepath = os.path.join(folder_path, filename)
            
            if " - " in name_only:
                parts = name_only.split(" - ")
                str_a = parts[0].strip()
                str_b = parts[1].strip()
                
                # Update progress bar suffix text with currently processing track file string layout
                pbar.set_postfix_str(f"Analyzing: {filename[:25]}...")
                
                artist, title, album, year, release_id = fetch_song_and_art_details(str_a, str_b)
                
                if album and year:
                    corrected_filename = f"{artist} - {title}{ext}"
                    corrected_filename = re.sub(r'[\\/*?:"<>|]', "", corrected_filename)
                    working_filepath = os.path.join(folder_path, corrected_filename)
                    
                    if filename != corrected_filename:
                        try:
                            os.rename(original_filepath, working_filepath)
                        except Exception:
                            working_filepath = original_filepath
                    else:
                        working_filepath = original_filepath

                    formatted_album = f"({year}) {album}"
                    image_bytes = download_album_art(release_id)
                    
                    # ---- PROCESS MP3 ----
                    if ext == '.mp3':
                        try:
                            try:
                                audio = MP3(working_filepath, ID3=ID3)
                            except Exception:
                                audio = MP3(working_filepath)
                                audio.add_tags()
                            
                            audio.tags.add(TPE1(encoding=3, text=artist))
                            audio.tags.add(TIT2(encoding=3, text=title))
                            audio.tags.add(TALB(encoding=3, text=formatted_album))
                            audio.tags.add(TDRC(encoding=3, text=year))
                            
                            if image_bytes:
                                audio.tags.add(APIC(
                                    encoding=3, mime='image/jpeg', type=3, 
                                    desc=u'Cover', data=image_bytes
                                ))
                                
                            audio.save()
                            processed_count += 1
                        except Exception:
                            pass
                            
                    # ---- PROCESS M4A ----
                    elif ext == '.m4a':
                        try:
                            audio = MP4(working_filepath)
                            if audio.tags is None:
                                audio.tags = MP4Tags()
                            
                            audio.tags['\xa9ART'] = artist
                            audio.tags['\xa9nam'] = title
                            audio.tags['\xa9alb'] = formatted_album
                            audio.tags['\xa9day'] = year
                            
                            if image_bytes:
                                audio.tags['covr'] = [MP4Cover(image_bytes, imageformat=MP4Cover.FORMAT_JPEG)]
                                
                            audio.save()
                            processed_count += 1
                        except Exception:
                            pass
                
                # API request rhythm buffer
                time.sleep(1)
            else:
                # Track skips automatically bypass without stalling the tqdm sequence counter
                pass

    print(f"\nTask Complete! Successfully verified, renamed, and tagged {processed_count} files.")

if __name__ == "__main__":
    process_and_tag_files(MUSIC_FOLDER)
