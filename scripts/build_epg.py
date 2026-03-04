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
    # Samsung (14)
    "GB2000955S": "AMC Cupid",
    "CABC23000223U": "The Weather Network",
    "ATBD190000101": "CNN Headlines",
    "USBA300004TE": "Dallas Cowboys Cheerleaders",
    "CA3400002KP": "Dog Whisperer",
    "CA300017ZS": "Love Pets",
    "DEBC4700004VZ": "Love the Planet",
    "CA4600001IG": "Murdoch Mysteries",
    "CHAK3504501A": "Pluto TV Food",
    "US14000030Y": "Rainy Day Vibes",
    "CABB2500020SS": "TED",
    "ES2300004XW": "Al Jazeera",
    "FRAJ3800004CC": "MTV Classics",
    "USBD4200016QR": "PickleballTV",
    # Pluto (41)
    "6536721dbfbaec00088687c0": "CBC News Toronto",
    "5e8397936791b30007ebb5a7": "Just for Laughs Gags",
    "66df8a29b25d2b0008fc5fe0": "Love Nature 4k",
    "65d92a8c8b24c80008e285c0": "BBC News",
    "6508be683a0d700008c534e4": "ABC News Live",
    "62ba60f059624e000781c436": "00s Replay",
    "6176f39e709f160007ec61c3": "48 Hours",
    "5f4d878d3d19b30007d2e782": "70s Cinema",
    "5ca525b650be2571e3943c63": "80s Rewind",
    "5f4d86f519358a00072b978e": "90s Throwback",
    "5e84f54a82f05300080e6746": "America's Test Kitchen",    
    "5ce44810b421747ae467b7cd": "Antiques Roadshow",
    "60a3d889a5b3690008dc7fe8": "Bar Rescue",
    "656535fc2c46f30008870fae": "BBC Earth",
    "6419ab7c9189ce000865a469": "Cops",
    "63eb9c5351f5d000085e8d7e": "CSI: Miami",
    "62e92951c2db99000787c00d": "Deal or no Deal",
    "65788362cbd0d60008f8729a": "Dog The Bounty Hunter",
    "5dc0c78281eddb0009a02d5e": "ET",
    "5ff8c708653d080007361b14": "Frasier & Cheers",
    "60f75771dfc72a00071fd0e0": "Gunsmoke",
    "62e917b5e354cf0007b97a67": "Happy Days",
    "62ea45010d0611000839868c": "Hell's Kitchen",
    "6408b41b83f58900081d91ad": "Inspector Gadget",
    "64424b21e1979c0008379681": "Jersey Shore",
    "6132619f9ddaa50007e7dd86": "King of Queens",
    "677fb3432952c1163bf1a539": "Million Dollar Listing",
    "66ff0cf663292d0008320cf8": "No Reservations",
    "63b48016d9dd51000828fa37": "PowerNation",
    "5e1f7da4bc7d740009831259": "America's Voice News",
    "64f9cccf110545000837912e": "Ridiculousness",
    "6532e8342cf13100083b404c": "Say Yes to the Dress",
    "6675c88da1d7ad00084762cb": "Star Trek",
    "66abefe5d2d50d00082c7d12": "VH1 Queens of Reality",
    "61d4c2817a823d00070ba53e": "True School Hip-Hop",
    "5da0d83f66c9700009b96d0e": "Vevo R&B",
    "5d93b635b43dd1a399b39eee": "Vevo Pop",
    "61d4b38226b8a50007fe03a6": "Vevo Rock",
    "5616f9c0ada51f8004c4b091": "World Poker Tour",
    "66ed3e9d5e4a6e0008b346e0": "UFC",
    # Plex > Samsung (21)
    "CA1400004AE": "CTV News",  
    "CABD1200043OK": "CBC Comedy",
    "US1900012GD": "The Conners",
    "CA900005B8": "Dance Moms",
    "ESBD3700001S0": "Dateline",
    "GB2700003KS": "Evolution Earth",
    "5e20b730f2f8d5003d739db7-6490c01f3b3ce9e1aaad95be": "FashionTV",
    "GBBC900014LW": "Great British Menu",
    "CABB2500030GT": "Journy",
    "GBBB4600001IK": "Project Runway",
    "CA1400017PU": "Property Brothers",
    "GBBB1000005IO": "Real Wild",
    "USBD350002623": "Stingray Classica",
    "CAAJ3400016J9": "The Design Network",
    "CA1400009E5": "The Mightiest by CTV",
    "USBB32000251N": "Today All day",
    "USBB1500001GD": "USA Today",
    "USAJ4300005PJ": "Yahoo Finance",
    # Roku > Samsung (22)
    "CABA3700001DB": "Always Funny Videos",
    "GB38000026H": "Bon Appétit",
    "USBD700021WG": "BUZZR",   
    "CABC5200020WJ": "Comedy Dynamics",
    "USAJ3504708A": "DangerTV",
    "d93912b4b21158fd95af2ceb8979c586": "Dove > Roku",
    "15cc44e50d8453e18f21ea37713319c5": "Electric Now > Roku",   
    "ATAJ32000027V": "FailArmy",
    "CAAJ27000079E": "FilmRise True Crime",
    "USBB32000196O": "FilmRise Westerns",
    "CABD1200001SY": "Gravitas Movies",
    "USBC1300009VM": "Lol! Network",
    "CAAJ2700030ON": "Outside TV",
    "CAAJ1700002PA": "The Asylum",
    "CABC2300001X9": "The Jack Hanna Channel",
    "GBBC4000002H3": "The Jamie Oliver Channel",
    "USBC13000065U": "This Old House",
    "USBC3600002EK": "Vevo Hip-Hop",
    "USBC3900009K5": "Vevo R&B",
    "CABC2300002VB": "Xplore",
    "USBA300031OT": "Sportsgrid",
    # Tubi > Samsung (17)
    "GBBB1600006RS": "Are We There Yet?",
    "USBC3600005U9": "Discovery Turbo TV",
    "GBBA33000557H": "Moviesphere by Lionsgate",
    "USBD70000213": "TMZ",
    "USBB4400018LR": "Wipeout Xtra",
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
print("Channels included:")
for cid in seen_channels:
    print(f" - {CHANNELS.get(cid, 'Unknown')} ({cid})")