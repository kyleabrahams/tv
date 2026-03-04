import requests
import xml.etree.ElementTree as ET
from io import BytesIO
import os
import time

# python3 -m venv myenv
# source myenv/bin/activate
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts2/build_epg.py


# Base directory relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Output path inside scripts/_epg-end
OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml")
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# XML URLs to fetch
XMLTV_URLS = [
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Roku/all.xml",
    "https://i.mjh.nz/SamsungTVPlus/all.xml"
]

# Optional: only include these channels (empty = all channels)
CHANNELS = {
{
    "6508be683a0d700008c534e4": "ABC News Live - Pluto",
    "GB2000955S": "AMC Cupid - Samsung",
    "5e1f7da4bc7d740009831259": "America's Voice News - Pluto",
    "5e84f54a82f05300080e6746": "America's Test Kitchen - Pluto",
    "ES2300004XW": "Al Jazeera - Samsung",
    "CABA3700001DB": "Always Funny Videos - Samsung",
    "US1900015FR": "Anger Management - Samsung",
    "USBC6000108Z": "BBC Food - Samsung",
    "CABD1200012B8": "BBC Home & Garden - Samsung",
    "5e20b730f2f8d5003d739db7-65622eddb7d737841f30a4fd": "BBC Travel - Plex",
    "65d92a8c8b24c80008e285c0": "BBC News - Pluto",
    "GB38000026H": "Bon Appétit - Samsung",
    "USAJ3504714A": "Cheddar News - Samsung",
    "CABC5200020WJ": "Comedy Dynamics - Samsung",
    "CABD1200043OK": "CBC Comedy - Samsung",
    "6536721dbfbaec00088687c0": "CBC News Toronto - Pluto",
    "ATBD190000101": "CNN Headlines - Samsung",
    "66e0b4536ad04d0008fff4b2": "CNN Originals - Pluto",
    "US1900012GD": "The Conners - Samsung",
    "CA1400004AE": "CTV News - Samsung",
    "CA14000028T": "CTV @ Home - Samsung",
    "CA35000025N": "CTV Gets Real - Samsung",
    "CA1400005SO": "CTV Laughs - Samsung",
    "USBA300004TE": "Dallas Cowboys Cheerleaders - Samsung",
    "CA900005B8": "Dance Moms - Samsung",
    "ESBD3700001S0": "Dateline - Samsung",
    "62e92951c2db99000787c00d": "Deal or no Deal - Pluto",
    "d93912b4b21158fd95af2ceb8979c586": "Dove - Roku",
    "CA3400002KP": "Dog Whisperer - Samsung",
    "65788362cbd0d60008f8729a": "Dog The Bounty Hunter - Pluto",
    "15cc44e50d8453e18f21ea37713319c5": "Electric Now - Roku",
    "ATAJ32000027V": "FailArmy - Samsung",
    "5e20b730f2f8d5003d739db7-64106a1075be345a863fe0d7": "Fifth Gear - Plex",
    "5e20b730f2f8d5003d739db7-6490c01f3b3ce9e1aaad95be": "FashionTV - Plex",
    "GB500007VM": "Family Feud - Samsung",
    "CAAJ2700014EE": "FilmRise Action - Samsung",
    "CAAJ40000077N": "FilmRise Free Movies - Samsung",
    "CAAJ27000079E": "FilmRise True Crime - Samsung",
    "USBB32000196O": "FilmRise Westerns - Samsung",
    "USBA3800004EL": "Fireplace 4K - Samsung",
    "GB2700003KS": "Evolution Earth - Samsung",
    "GBBC900014LW": "Great British Menu - Samsung",
    "60f75771dfc72a00071fd0e0": "Gunsmoke - Pluto",
    "CABB2500021YQ": "Gusto TV - Samsung",
    "CABB2500030GT": "Journy - Samsung",
    "64424b21e1979c0008379681": "Jersey Shore - Pluto",
    "CAAJ3400002DI": "Jail - Samsung",
    "CABC2300001X9": "The Jack Hanna Channel - Samsung",
    "GBBC4000002H3": "The Jamie Oliver Channel - Samsung",
    "6132619f9ddaa50007e7dd86": "King of Queens - Pluto",
    "USBD270001633": "Hallmark Movies & More - Samsung",
    "CA300017ZS": "Love Pets - Samsung",
    "DEBC4700004VZ": "Love the Planet - Samsung",
    "66df8a29b25d2b0008fc5fe0": "Love Nature 4k - Pluto",
    "FRAJ3800004CC": "MTV Classics - Samsung",
    "CA4600001IG": "Murdoch Mysteries - Samsung",
    "GBBA33000557H": "Moviesphere by Lionsgate - Samsung",
    "677fb3432952c1163bf1a539": "Million Dollar Listing - Pluto",
    "USBB40000028E": "NBC LX Home - Samsung",
    "ESBC400003YM": "NBC News NOW - Samsung",
    "CAAJ2700030ON": "Outside TV - Samsung",
    "CA1400017PU": "Property Brothers - Samsung",
    "GBBB4600001IK": "Project Runway - Samsung",
    "USBD4200016QR": "PickleballTV - Samsung",
    "USBB32000251N": "Today All day - Samsung",
    "USBC13000065U": "This Old House - Samsung",
    "CABB2500020SS": "TED - Samsung",
    "USBD350002623": "Stingray Classica - Samsung",
    "CAAJ3400003T7": "Stingray Naturescape - Samsung",
    "USBA300031OT": "Sportsgrid - Samsung",
    "USBD70000213": "TMZ - Samsung",
    "US14000030Y": "Rainy Day Vibes - Samsung",
    "64f9cccf110545000837912e": "Ridiculousness - Pluto",
    "GBBB1000005IO": "Real Wild - Samsung",
    "6532e8342cf13100083b404c": "Say Yes to the Dress - Pluto",
    "USAJ3504708A": "DangerTV - Samsung",
    "USAJ30000039U": "Dry Bar Comedy - Samsung",
    "5da0d83f66c9700009b96d0e": "Vevo R&B - Pluto",
    "61d4b38226b8a50007fe03a6": "Vevo Rock - Pluto",
    "61d4c2817a823d00070ba53e": "True School Hip-Hop - Pluto",
    "USBC3600002EK": "Vevo Hip-Hop - Samsung",
    "USBC3900009K5": "Vevo R&B - Samsung",
    "USBC3600008WY": "Vevo Pop - Samsung",
    "60db737695c95b599dad50d2c5595fe3": "Vevo Reggaeton & Trap",
    "CABC23000223U": "The Weather Network - Samsung",
    "USAJ4300005PJ": "Yahoo Finance - Samsung",
    "USBB1500001GD": "USA Today - Samsung",
    "USBB4400018LR": "Wipeout Xtra - Samsung",
    "USBD700021WG": "BUZZR - Samsung",
    "USBD300012YC": "Vevo '80s - Samsung",
    "USBD3000133M": "Vevo '90s - Samsung",
    "USBB4400015F5": "Vevo 2K - Samsung",
    "DEBA3300030O1": "Trace Urban - Samsung",
    "US3800007CR": "WildEarth - Samsung",
    "5bb3fea0f711fd76340eebff": "Pluto TV Military - Pluto",
    "5c665db3e6c01b72c4977bc2": "Pluto TV Cult Films - Pluto",
    "6823030830b839eca51489d6": "Popstar! - Pluto",
    "5ca671f215a62078d2ec0abf": "South Park - Pluto",
    "CABD1200002T9": "Tastemade - Samsung",
    "CABC5200002OG": "Tastemade Home - Samsung",
    "USBD700017WC": "Tastemade Travel - Samsung",
    "USBD1200004NS": "The Walking Dead Universe - Samsung",
    "CA9000103C": "Tiny House Nation - Samsung",
    "US1900002QK": "Universal Monsters - Samsung",
    "": "Name",    
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",          
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",     
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",    
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",   
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",     
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",    
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name", 
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",     
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",    
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",   
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",     
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",    
    "": "Name",
    "": "Name",
    "": "Name",
    "": "Name",     
}

# User-Agent header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

# -------------------------
# PROCESS
# -------------------------
new_root = ET.Element("tv")
seen_channels = set()

for url in XMLTV_URLS:
    print(f"⬇️ Fetching {url}")

    # Retry logic
    r = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < 2:
                print("⏳ Retrying in 5 seconds...")
                time.sleep(5)

    if not r:
        print(f"❌ Skipping {url} after 3 failed attempts")
        continue

    # Parse XML
    root = ET.parse(BytesIO(r.content)).getroot()

    # ---- Channels ----
    for channel in root.findall("channel"):
        cid = channel.get("id")
        if not cid or (CHANNELS and cid not in CHANNELS) or cid in seen_channels:
            continue
        seen_channels.add(cid)
        new_root.append(channel)

    # ---- Programmes ----
    for programme in root.findall("programme"):
        cid = programme.get("channel")
        if not cid or (CHANNELS and cid not in CHANNELS):
            continue
        new_root.append(programme)

# -------------------------
# WRITE OUTPUT
# -------------------------
ET.ElementTree(new_root).write(
    OUTPUT_XML,
    encoding="utf-8",
    xml_declaration=True
)

# -------------------------
# SUMMARY
# -------------------------
print(f"✅ Generated {OUTPUT_XML}")
print(f"📺 Total channels added: {len(seen_channels)}")
print("Channels and number of programs:")

# Count programs per channel
program_counts = {cid: 0 for cid in seen_channels}
for programme in new_root.findall("programme"):
    cid = programme.get("channel")
    if cid in seen_channels:
        program_counts[cid] += 1

# Print results
for cid in seen_channels:
    channel_name = CHANNELS.get(cid, "Unknown")
    print(f" - {channel_name} ({cid}): {program_counts[cid]} programs")