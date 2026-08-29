import os
import re
import urllib.request
import urllib.parse
import json
import time
from mutagen.mp4 import MP4, MP4Tags, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC

# ==============================================================================
# STEP 1: INITIALIZE CONFIGURATIONS
# ==============================================================================
MUSIC_FOLDER = "/Volumes/Kyle4tb1223/__Spotube/1970's & before TEST"


# ==============================================================================
# STEP 2: EMBEDDED METADATA EXTRACTION ENGINE
# ==============================================================================
def read_existing_tags(file_path, ext):
    """
    Reads the file bytes directly and extracts any pre-existing tags 
    (Artist, Title, Year) currently saved inside the embedded metadata.
    """
    artist, title, year = None, None, None
    try:
        if ext == '.mp3':
            audio = MP3(file_path, ID3=ID3)
            if audio.tags:
                if 'TPE1' in audio.tags: artist = str(audio.tags['TPE1'].text)
                if 'TIT2' in audio.tags: title = str(audio.tags['TIT2'].text)
                for frame_key in ['TDRC', 'TYER']:
                    if frame_key in audio.tags:
                        year_match = re.search(r'\b\d{4}\b', str(audio.tags[frame_key].text))
                        if year_match: year = year_match.group(0)
                        break
        elif ext == '.m4a':
            audio = MP4(file_path)
            if audio.tags:
                if '\xa9ART' in audio.tags: artist = str(audio.tags['\xa9ART'])
                if '\xa9nam' in audio.tags: title = str(audio.tags['\xa9nam'])
                if '\xa9day' in audio.tags:
                    year_match = re.search(r'\b\d{4}\b', str(audio.tags['\xa9day']))
                    if year_match: year = year_match.group(0)
    except Exception:
        pass
    return artist, title, year


# ==============================================================================
# STEP 3: DEDICATED ARTWORK FETCH ENGINE (FIXED ABSOLUTE ITUNES API PATH)
# ==============================================================================
def fetch_cover_art_url(artist, title):
    """
    Queries the public Apple iTunes API to grab ultra-high-res artwork URL data 
    matching your track names with zero token restrictions.
    """
    try:
        search_phrase = f"{artist} {title}"
        encoded_query = urllib.parse.quote(search_phrase)
        
        # DEFINITIVE FIX: Explicitly corrected the absolute web routing target address url path
        url = f"https://apple.com{encoded_query}&media=music&entity=musicTrack&limit=5"
        print(f"   [DEBUG ART] Querying Apple API -> {url}")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            results = data.get('results', [])
            
            print(f"   [DEBUG ART] Apple API returned {len(results)} matches.")
            if results and len(results) > 0:
                top_track = results[0]
                image_url = top_track.get('artworkUrl100')
                if image_url:
                    high_res_url = image_url.replace("100x100bb.jpg", "1000x1000bb.jpg")
                    print(f"   [DEBUG ART] Discovered image target URL: {high_res_url}")
                    return high_res_url
                else:
                    print("   [DEBUG ART] Match found, but 'artworkUrl100' field was blank.")
            else:
                print("   [DEBUG ART] Zero matches returned from Apple for this search phrase text.")
    except Exception as e:
        print(f"   [DEBUG ART ERROR] Failed to complete network call: {e}")
    return None


def download_album_art(image_url):
    """Downloads raw binary image cover bytes straight from global asset servers."""
    if not image_url:
        return None
    try:
        print(f"   [DEBUG IMAGE] Attempting download from CDN...")
        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req) as response:
            img_bytes = response.read()
            print(f"   [DEBUG IMAGE] Download success! Payload size: {len(img_bytes)} bytes.")
            return img_bytes
    except Exception as e:
        print(f"   [DEBUG IMAGE ERROR] Download connection failed: {e}")
    return None



# ==============================================================================
# STEP 4: FILE SYSTEM TRAVERSAL LOOP (INTELLIGENT MIXED CONVENTION PARSER)
# ==============================================================================
def process_and_tag_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"Error: Target path '{folder_path}' does not exist.")
        return

    all_files = os.listdir(folder_path)
    
    valid_files = [
        f for f in all_files 
        if not (f.startswith('.') or f.startswith('._')) and os.path.splitext(f)[1].lower() in ['.mp3', '.m4a']
    ]

    if not valid_files:
        print("No valid .mp3 or .m4a audio tracks detected in target directory.")
        return

    print(f"Initializing Production Engine on: {folder_path}")
    print(f"Found {len(valid_files)} audio tracks to evaluate.")
    print("=" * 80)
    
    processed_count = 0

    for filename in valid_files:
        name_only, ext = os.path.splitext(filename)
        ext = ext.lower()
        original_filepath = os.path.join(folder_path, filename)
        
        print(f"\n[FILE START] Core Evaluation for: '{filename}'")
        
        if " - " in name_only:
            # Read internal tags first to see if we can resolve formatting without guessing text split layouts
            tag_artist, tag_title, tag_year = read_existing_tags(original_filepath, ext)
            
            parts = name_only.split(" - ")
            parts = [p.strip() for p in parts if p.strip()]
            
            # AUTOMATED ORIENTATION ENGINE: Determine if file is 'Artist - Title' vs 'Title - Artist'
            if tag_artist and tag_title:
                print(f"   [DEBUG INTERNAL] Found existing metadata tags -> Artist: '{tag_artist}' | Title: '{tag_title}'")
                artist = tag_artist
                title = tag_title
                year = tag_year
            else:
                # Fallback to textual positioning logic if internal tag space fields are totally blank
                print("   [DEBUG INTERNAL] No pre-existing internal tags. Falling back to filename split...")
                artist = parts[0]
                title = " - ".join(parts[1:])
                year = None
                
            # If the folder contains duplicate echo trailing tags, slice them out cleanly
            if artist.lower().endswith(title.lower()) or title.lower().endswith(artist.lower()):
                if len(parts) >= 2:
                    artist = parts[0]
                    title = parts[1]

            # Parse out alternative regex year timestamps if available
            if not year:
                year_match = re.search(r'\b(19\d{2}|20\d{2})\b', name_only)
                year = year_match.group(0) if year_match else "1970"
            
            # Clean up string noise clutter patterns
            title = re.sub(r'\[.*?\]', '', title)
            title = re.sub(r'\(.*?\)', '', title)
            title = re.sub(r'\b' + year + r'\b', '', title)
            title = re.sub(r'\b(original|remastered|remaster|official|video|audio|lyric|hq|hd)\b', '', title, flags=re.IGNORECASE)
            title = title.strip().strip("-").strip()
            
            # Map common classic artist variances uniformly
            if artist.lower() in ["the jacksons", "jacksons"]: artist = "The Jackson 5"
            elif "sam cooke" in artist.lower() or "samcooke" in artist.lower(): artist = "Sam Cooke"
            elif artist.lower() == "acdc": artist = "AC/DC"

            album = f"{title} Single"
            formatted_album = f"({year}) {album}"
            print(f"   [DEBUG PARSE] Prepared clean metadata attributes -> Artist: '{artist}' | Title: '{title}' | Album: '{formatted_album}'")
            
            # Query network CDN layer asset pipelines
            image_url = fetch_cover_art_url(artist, title)
            image_bytes = download_album_art(image_url)

            # Standardize the drive file name to "Artist - Title.ext"
            corrected_filename = f"{artist} - {title}{ext}"
            corrected_filename = re.sub(r'[\\/*?:"<>|]', "", corrected_filename)
            working_filepath = os.path.join(folder_path, corrected_filename)
            
            if filename != corrected_filename:
                try:
                    os.rename(original_filepath, working_filepath)
                    print(f"   [DEBUG ACTION] Disk rename executed -> '{corrected_filename}'")
                except Exception as e:
                    print(f"   [DEBUG ACTION WARNING] Disk rename blocked: {e}")
                    working_filepath = original_filepath
            else:
                working_filepath = original_filepath

            # ---- WRITE MP3 ATOMS ----
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
                        print("   [DEBUG WRITE] APIC image tag frame pushed to MP3 structure array.")
                    else:
                        print("   [DEBUG WRITE SKIP] MP3 skipped art embedding because image_bytes variable is empty.")
                        
                    audio.save()
                    print("   [DEBUG SUCCESS] MP3 file binary tags flushed and saved to disk volume.")
                    processed_count += 1
                except Exception as e:
                    print(f"   [DEBUG MP3 CRASH] Write pipeline failed: {e}")
                    
            # ---- WRITE M4A ATOMS ----
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
                        print("   [DEBUG WRITE] 'covr' block data pushed to M4A atom container array.")
                    else:
                        print("   [DEBUG WRITE SKIP] M4A skipped art embedding because image_bytes variable is empty.")
                        
                    audio.save()
                    print("   [DEBUG SUCCESS] M4A file atoms flushed and saved to disk volume.")
                    processed_count += 1
                except Exception as e:
                    print(f"   [DEBUG M4A CRASH] Write pipeline failed: {e}")
        else:
            print(f"   [RESULT] Skipped track. Missing ' - ' divider sequence pattern.")
        print("-" * 80)
        time.sleep(1)

    print(f"\nTask Complete! Successfully evaluated and tagged {processed_count} files on disk.")


# ==============================================================================
# STEP 5: RUN MAIN INTERFACE CONTAINER
# ==============================================================================
if __name__ == "__main__":
    process_and_tag_files(MUSIC_FOLDER)
