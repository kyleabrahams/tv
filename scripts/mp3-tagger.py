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
musicbrainzngs.set_useragent("MyMultiFormatMusicTagger", "7.0", "your_email@example.com")

# Target music folder path
MUSIC_FOLDER = "/Volumes/Kyle4tb1223/__Spotube/1970's & before TEST"

def clean_search_term(text):
    """Strips away common distracting tags like remaster dates from queries."""
    text = re.sub(r'\b\d{4}\s+Remaster\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bRemaster(ed)?\b', '', text, flags=re.IGNORECASE)
    return text.strip().strip("-").strip()

def fetch_song_and_art_details(str_a, str_b):
    """
    Queries MusicBrainz. Evaluates permutations and cross-references 
    the official database spelling of Artist and Track Title.
    """
    clean_a = clean_search_term(str_a)
    clean_b = clean_search_term(str_b)
    
    permutations = [(clean_a, clean_b), (clean_b, clean_a)]
    
    for artist_query, title_query in permutations:
        if not artist_query or not title_query:
            continue
        try:
            query = f'artist:"{artist_query}" AND recording:"{title_query}"'
            result = musicbrainzngs.search_recordings(query=query, limit=3)
            
            if not result.get('recording-list'):
                continue

            for recording in result['recording-list']:
                # Pull the exact authoritative spelling entries from the DB match
                official_title = recording.get('title')
                
                # Extract the primary artist name cleanly out of the credit metadata dictionary
                official_artist = None
                if 'artist-credit' in recording and len(recording['artist-credit']) > 0:
                    credit = recording['artist-credit'][0]
                    if isinstance(credit, dict) and 'artist' in credit:
                        official_artist = credit['artist'].get('name')
                
                if 'release-list' in recording:
                    for release in recording['release-list']:
                        album = release.get('title')
                        date = release.get('date')
                        release_id = release.get('id')
                        
                        if album and date and release_id and official_artist and official_title:
                            year_match = re.search(r'\b\d{4}\b', date)
                            year = year_match.group(0) if year_match else None
                            if year:
                                return official_artist, official_title, album, year, release_id
        except Exception as e:
            print(f"   API Search Warning: {e}")
            
    return None, None, None, None, None

def download_album_art(release_id):
    """Fetches raw image bytes from the Cover Art Archive API."""
    url = f"https://coverartarchive.org{release_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MyMultiFormatMusicTagger/7.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data and 'images' in data and len(data['images']) > 0:
                image_url = data['images'].get('image')
                if image_url:
                    img_req = urllib.request.Request(image_url, headers={'User-Agent': 'MyMultiFormatMusicTagger/7.0'})
                    with urllib.request.urlopen(img_req) as img_response:
                        return img_response.read()
    except Exception:
        pass
    return None

def process_and_tag_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"Error: Target path '{folder_path}' does not exist.")
        return

    print(f"Scanning folder: {folder_path}\n" + "="*60)
    processed_count = 0

    for filename in os.listdir(folder_path):
        if filename.startswith('.') or filename.startswith('._'):
            continue
            
        name_only, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        if ext not in ['.mp3', '.m4a']:
            continue
            
        original_filepath = os.path.join(folder_path, filename)
        
        if " - " in name_only:
            parts = name_only.split(" - ")
            str_a = parts[0].strip()
            str_b = parts[1].strip()
            
            print(f"Analyzing File: '{filename}'")
            # Pulls cross-referenced spelling corrections straight from MusicBrainz
            artist, title, album, year, release_id = fetch_song_and_art_details(str_a, str_b)
            
            if album and year:
                # Build target clean filename using the database spellings
                corrected_filename = f"{artist} - {title}{ext}"
                corrected_filename = re.sub(r'[\\/*?:"<>|]', "", corrected_filename)
                working_filepath = os.path.join(folder_path, corrected_filename)
                
                # Safely execute file naming cross-reference fixes on your drive
                if filename != corrected_filename:
                    try:
                        os.rename(original_filepath, working_filepath)
                        print(f"   [Cross-Ref Rename] -> Corrected to: '{corrected_filename}'")
                    except Exception as rename_err:
                        print(f"   [Warning] Could not rename file: {rename_err}")
                        working_filepath = original_filepath  # Fallback to safely tag the old file name
                else:
                    working_filepath = original_filepath

                formatted_album = f"({year}) {album}"
                image_bytes = download_album_art(release_id)
                
                # ---- PROCESS MP3 AUTO-TAGS ----
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
                            print("   Success: MP3 Album art embedded!")
                            
                        audio.save()
                        print(f"   [MP3 Tagged] -> Album: {formatted_album}")
                        processed_count += 1
                    except Exception as err:
                        print(f"   [Error] Writing MP3 failed: {err}")
                        
                # ---- PROCESS M4A AUTO-TAGS ----
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
                            print("   Success: M4A Album art embedded!")
                            
                        audio.save()
                        print(f"   [M4A Tagged] -> Album: {formatted_album}")
                        processed_count += 1
                    except Exception as err:
                        print(f"   [Error] Writing M4A failed: {err}")
            else:
                print(f"   [Skipped] Could not verify verified match layout on MusicBrainz.")
            
            time.sleep(1)  # API safe buffer
        else:
            print(f"   [Skipped] File name '{filename}' missing proper ' - ' break.")
        print("-" * 60)

    print(f"\nTask Complete! Successfully cross-referenced, fixed typos, and tagged {processed_count} files.")

if __name__ == "__main__":
    process_and_tag_files(MUSIC_FOLDER)
