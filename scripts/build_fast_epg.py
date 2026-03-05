import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from io import BytesIO
import os
import time
import re
import gzip
from xml.sax.saxutils import escape



# build_fast_epg.py Mar 5 2026 1203 am
# python3 -m venv myenv
# source myenv/bin/activate
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/build_fast_epg.py


# Base directory relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Output path inside scripts/_epg-end
OUTPUT_XML = os.path.join(BASE_DIR, "_epg-end", "fast-epg-end.xml")
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# XML URLs to fetch
XMLTV_URLS = [
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://i.mjh.nz/Roku/all.xml",
    "https://raw.githubusercontent.com/acidjesuz/EPGTalk/refs/heads/master/guide.xml",
    "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CY1.xml.gz",
    "https://i.mjh.nz/SamsungTVPlus/all.xml"
]

# Optional: only include these channels (empty = all channels)
CHANNELS = {
    "6508be683a0d700008c534e4": "ABC News Live - Pluto",
    "GB2000955S": "AMC Cupid - Samsung",
    "5e1f7da4bc7d740009831259": "America's Voice News - Pluto",
    "5e84f54a82f05300080e6746": "America's Test Kitchen - Pluto",
    "ES2300004XW": "Al Jazeera - Samsung",
    "CABA3700001DB": "Always Funny Videos - Samsung",
    "US1900015FR": "Anger Management - Samsung",
    "USBC6000108Z": "BBC Food - Samsung",
    "CABD1200012B8": "BBC Home and Garden - Samsung",
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
    "USBD270001633": "Hallmark Movies and More - Samsung",
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
    "5da0d83f66c9700009b96d0e": "Vevo RandB - Pluto",
    "61d4b38226b8a50007fe03a6": "Vevo Rock - Pluto",
    "61d4c2817a823d00070ba53e": "True School Hip-Hop - Pluto",
    "USBC3600002EK": "Vevo Hip-Hop - Samsung",
    "USBC3900009K5": "Vevo RandB - Samsung",
    "USBC3600008WY": "Vevo Pop - Samsung",
    "60db737695c95b599dad50d2c5595fe3": "Vevo Reggaeton and Trap - Roku",
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
    # US Local TV
    "WUTV-DT.us": "FOX 29 WUTV",
    "WIVB-DT.us": "CBS Buffalo WIVB",
    "WNBC-DT.us_": "NBC New York WNBC",
    "WKBW-DT.us": "ABC New York WKBW",    
    "": "Name",
    # Paid TV
    "": "Name",
    "I215.10105.schedulesdirect.org": "Omni 1 - acidjesuz",
    "I802.46245.schedulesdirect.org": "CBC Toronto - acidjesuz",
    "I1051.44784.schedulesdirect.org": "CTV Toronto - acidjesuz",          
    "I1131.62890.schedulesdirect.org": "CTV Calgary - acidjesuz",
    "I237.10057.schedulesdirect.org": "Bravo.ca - acidjesuz",
    "I218.60123.schedulesdirect.org": "CHCH - acidjesuz",
    "I530.99429.schedulesdirect.org": "Makeful - acidjesuz",     
    "I501.17615.schedulesdirect.org": "CTV News Channel - acidjesuz",
    "I281.31046.schedulesdirect.org": "MotorTrend - Discovery Turbo - acidjesuz",
    "I486.72139.schedulesdirect.org": "Much Music HD - acidjesuz",
    "I7.87004.schedulesdirect.org": "AandE.ca - acidjesuz",          
    "I193.58646.schedulesdirect.org": "CNN - acidjesuz",
    "I251.21484.schedulesdirect.org": "Oxygen - acidjesuz",     
    "I601.15181.schedulesdirect.org": "Slice - acidjesuz",
    "I269.57708.schedulesdirect.org": "History.ca - acidjesuz",    
    "I629.26772.schedulesdirect.org": "H2 History - acidjesuz",
    "I810.52745.schedulesdirect.org": "Love Nature - acidjesuz",
    "I256.12852.schedulesdirect.org": "TCM - acidjesuz",   
    "I282.16331.schedulesdirect.org": "CTV Wild / Animal Planet - acidjesuz",
    "I283.66804.schedulesdirect.org": "Nat Geo Wild East - acidjesuz",
    "I331.10986.schedulesdirect.org": "MTV - acidjesuz",     
    "I618.17693.schedulesdirect.org": "DTOUR - acidjesuz",
    "I232.30156.schedulesdirect.org": "Cooking Channel - acidjesuz",
    "I236.10989.schedulesdirect.org": "E!.ca - acidjesuz",    
    "I248.58574.schedulesdirect.org": "FX.ca - acidjesuz",
    "I259.17927.schedulesdirect.org": "FXX.ca - acidjesuz",
    "I641.26779.schedulesdirect.org": "Cottage Life - acidjesuz",
    "I230.67375.schedulesdirect.org": "Magnolia Network - acidjesuz", 
    "I279.70387.schedulesdirect.org": "OWN - acidjesuz",
    "I360.60179.schedulesdirect.org": "Fox News - acidjesuz",
    "I191.58780.schedulesdirect.org": "CNBC - acidjesuz",
    "I357.26849.schedulesdirect.org": "CNBC World - acidjesuz",     
    "I425.113876.schedulesdirect.org": "HLN - acidjesuz",
    "I149.60048.schedulesdirect.org": "Cartoon Network - acidjesuz",
    "I501.10240.schedulesdirect.org": "HBO - acidjesuz",    
    "I506.59839.schedulesdirect.org": "HBO Comedy - acidjesuz",
    "I300.10191.schedulesdirect.org": "Crave 1 - acidjesuz",
    "I301.12222.schedulesdirect.org": "Crave 2 - acidjesuz",
    "I302.12223.schedulesdirect.org": "Crave 3 - acidjesuz",   
    "I303.21351.schedulesdirect.org": "Crave 4 - acidjesuz",
    "I141.70312.schedulesdirect.org": "Sony Movie - acidjesuz",
    "I545.11115.schedulesdirect.org": "Paramount+Showtime - acidjesuz",
    "I547.11116.schedulesdirect.org": "Showtime 2 - acidjesuz",     
    "I549.18086.schedulesdirect.org": "Showtime Extreme - acidjesuz",
    "I552.103892.schedulesdirect.org": "Showtime Family Zone - acidjesuz",
    "I551.68342.schedulesdirect.org": "Showtime Next - acidjesuz",
    "I585.25272.gracenote.com": "Showtime Women - acidjesuz",    
    "I558.65687.schedulesdirect.org": "MGM+ - acidjesuz",
    "I559.67929.schedulesdirect.org": "MGM+ Hits - acidjesuz",
    "I173.101730.schedulesdirect.org": "Cinemax - acidjesuz",
    "I517.59373.schedulesdirect.org": "Cinemax MoreMax - acidjesuz",     
    "I519.59948.schedulesdirect.org": "Cinemax ActionMax - acidjesuz",
    "I525.12719.schedulesdirect.org": "Starz - acidjesuz",
    "I530.16833.schedulesdirect.org": "Starz in Black - acidjesuz",    
    "I531.67236.schedulesdirect.org": "Starz Cinema - acidjesuz",
    "I528.57569.schedulesdirect.org": "Starz Comedy - acidjesuz",
    "I529.57573.schedulesdirect.org": "Starz Edge - acidjesuz",
    "I535.10178.schedulesdirect.org": "Starz Encore - acidjesuz", 
    "I538.102906.schedulesdirect.org": "Starz Encore Westerns - acidjesuz",
    "I128.69387.schedulesdirect.org": "BBC One - acidjesuz",
    "I256.50059.schedulesdirect.org": "BBC Two - acidjesuz",
    "I109.20684.schedulesdirect.org": "BBC Four - acidjesuz",     
    "I104.60940.schedulesdirect.org": "BBC Alba - acidjesuz",
    "I326.117175.schedulesdirect.org": "Channel 4 - acidjesuz",
    "I351.50717.schedulesdirect.org": "Channel 5 - acidjesuz",
    "I997.61177.schedulesdirect.org": "SKY Cinema Action - acidjesuz",    
    "I998.115495.schedulesdirect.org": "Sky Cinema Animation - acidjesuz",
    "I1000.61179.schedulesdirect.org": "SKY Cinema Drama - acidjesuz",
    "I1005.24040.schedulesdirect.org": "SKY Cinema Family - acidjesuz",
    "I1008.61180.schedulesdirect.org": "SKY Cinema Greats - acidjesuz",   
    "I1010.49453.schedulesdirect.org": "SKY Cinema Hits - acidjesuz",
    "I1011.21107.schedulesdirect.org": "Sky Cinema Premiere - acidjesuz",
    "I1014.61178.schedulesdirect.org": "Sky Cinema Sci-Fi Horror - acidjesuz",
    "I1015.49139.schedulesdirect.org": "Sky Cinema Select - acidjesuz",     
    "I1015.49139.schedulesdirect.org": "SkyCinemaSelect.uk - acidjesuz",
    "I1018.50176.schedulesdirect.org": "Sky Cinema Thriller - acidjesuz",
    "I1020.113612.schedulesdirect.org": "Sky Comedy - acidjesuz",
    "I1022.45005.schedulesdirect.org": "Sky Crime - acidjesuz",    
    "I1031.60500.schedulesdirect.org": "Sky History - acidjesuz",
    "I1063.16235.schedulesdirect.org": "Sky Showcase - acidjesuz",
    "I1125.17443.schedulesdirect.org": "Sky Witness - acidjesuz",
    # epgshare01 GZ
    "Home.and.Garden.Television.ca2": "HGTV",  
    "Cable.Pulse.24.(CP24).HD.ca2": "CP24",
    "Global.Toronto.HD.ca2": "Global Toronto",    
    "Citytv.Toronto.HD.ca2": "Citytv Toronto",
    "CTV.Two.-.Barrie.ca2": "CTV Barrie",
    "CTV.Two.-.London/Windsor.ca2": "CTV2 Windsor",
    "W.Network.ca2": "W Network", 
    "CTV.Speed.HD.ca2": "CTV Speed",
    "A.and.E.Canada.HD.ca2": "A&E",
    "AMC.Canada.HD.ca2": "AMC",
    "The.Learning.Channel.HD.Canada.ca2": "TLC",     
    "CTV.LIFE.CHANNEL.ca2": "CTV Life",
    "Country.Music.Television.(CMT).ca2": "CMT",
    "Showcase.Television.Inc..(Canada).ca2": "Showcase",
    "CTV.DRAMA.CHANNEL.ca2": "CTV Drama",    
    "USA.Network.HD.ca2": "USA Network",
    "History.Television.HD.(Canada).ca2": "History",
    "CTV.COMEDY.CHANNEL.ca2": "CTV Comedy",
    "Home.Network.HD.ca2": "Home Network",   
    "Turner.Classic.Movies.Canada.HD.ca2": "TCM",
    "CTV.Nature.HD.ca2": "CTV Nature",
    "CTV.SCI-FI.CHANNEL.HD.ca2": "CTV Sci-fi",
    "National.Geographic.Wild.Canada.HD.ca2": "Nat Geo Wild",     
    "National.Geographic.Wild.HD.us2": "US Nat Geo Wild",
    "Flavour.Network.HD.ca2": "Flavour Network",
    "Food.Network.HD.us2": "Food Network",
    "WNED-DT.us": "PBS WNED",    
    "E!.Entertainment.Television.Canada.HD.ca2": "E!",
    "FX.HD.ca2": "FX",
    "FXX.Canada.ca2": "FXX",
    "CHARGE!.us2": "Charge!",  
    "Peachtree.TV.us2": "Peachtree",
    "T+E.ca2": "Travel + Escape",
    "Aboriginal.Peoples.Television.Network.HD.ca2": "APTN",    
    "MSNBC.HD.us2": "MSNBC",
    "BNN.Bloomberg.HD.ca2": "BNN Bloomberg",
    "Lifetime.HD.us2": "Lifetime",
    "LMN.HD.us2": "LMN", 
    "Paramount.Network.HD.us2": "Paramount",
    "National.Geographic.Canada.HD.ca2": "National Geographic",
    "National.Geographic.HD.us2": "National Geographic",
    "Curiosity.Channel.HD.us2": "Curiosity",     
    "Smithsonian.HD.Network.us2": "Smithsonian",
    "USA.Network.HD.us2": "USA Network",
    "Game.Show.Network.HD.us2": "Game Show Network",
    "GameTV.Canada.ca2": "GameTV",    
    "TVO.ca2": "TV Ontario",
    "YTVP.ca2": "YTV",
    "Nickelodeon.HD.us2": "Nickelodeon",
    "Treehouse.ca2": "Treehouse",   
    "Disney.Junior.HD.us2": "Disney Junior",
    "Disney.Channel.HD.us2": "Disney Channel",
    "HBO.Canada.1.HD.ca2": "HBO",
    "HBO.Canada.West.HD.ca2": "HBO2",     
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

import gzip

# -------------------------
# PROCESS
# -------------------------
new_root = ET.Element("tv")
seen_channels = {}
programmes_to_add = []

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

    # Parse XML safely (.xml or .xml.gz)
    content = r.content
    if content[:2] == b'\x1f\x8b':  # gzip magic bytes
        with gzip.open(BytesIO(content), "rt", encoding="utf-8", errors="ignore") as f:
            root = ET.parse(f).getroot()
    else:
        root = ET.parse(BytesIO(content)).getroot()

    # ---- Channels ----
    for channel in root.findall("channel"):
        cid = channel.get("id")
        if not cid or (CHANNELS and cid not in CHANNELS) or cid in seen_channels:
            continue

        # Remove <icon> from the channel before storing
        for icon in channel.findall("icon"):
            channel.remove(icon)

        # Add <url> tag pointing to the source XML
        url_elem = ET.Element("url")
        url_elem.text = url  # source URL
        channel.append(url_elem)

        seen_channels[cid] = channel  # store cleaned element

    # ---- Programmes ----
    for programme in root.findall("programme"):
        cid = programme.get("channel")
        if not cid or (CHANNELS and cid not in CHANNELS):
            continue
        programmes_to_add.append(programme)

# -------------------------
# SORT AND BUILD XML
# -------------------------
# Sort channels alphabetically by name
sorted_channel_ids = sorted(
    seen_channels.keys(),
    key=lambda cid: CHANNELS.get(cid, cid).lower()
)

# Append channels first
for cid in sorted_channel_ids:
    new_root.append(seen_channels[cid])

# Then append all programmes
for prog in programmes_to_add:
    new_root.append(prog)

# -------------------------
# Function to pretty-print XML
# -------------------------
# -------------------------
# Step 1: Build merged_root
# -------------------------
merged_root = ET.Element("tv")

# Add channels
for cid in sorted_channel_ids:
    merged_root.append(seen_channels[cid])

# Add programmes
for prog in programmes_to_add:
    merged_root.append(prog)

# -------------------------
# Step 2: Pretty-print XML
# -------------------------
def build_flat_xml(channels, programmes):
    """
    Build single-line XML string:
    - One line per channel
    - One line per programme
    - Removes <icon>, keeps <url> if present
    """
    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>', '<tv>']

    # Channels
    for channel in channels:
        cid = channel.get("id")
        display_name = escape(channel.findtext("display-name", default=""))
        url_elem = channel.find("url")
        url = escape(url_elem.text) if url_elem is not None and url_elem.text else ""

        line = f'<channel id="{cid}"><display-name>{display_name}</display-name>'
        if url:
            line += f'<url>{url}</url>'
        line += '</channel>'
        xml_lines.append(line)

    # Programmes
    for prog in programmes:
        attribs = " ".join(f'{k}="{v}"' for k, v in prog.attrib.items())

        children_str = ""
        for child in prog:
            tag = child.tag
            text = escape(child.text or "")
            children_str += f"<{tag}>{text}</{tag}>"

        line = f'<programme {attribs}>{children_str}</programme>'
        xml_lines.append(line)

    xml_lines.append("</tv>")

    return "\n".join(xml_lines)

# Example usage:
flat_xml = build_flat_xml(
    [seen_channels[cid] for cid in sorted_channel_ids],
    programmes_to_add
)

with open(OUTPUT_XML, "w", encoding="utf-8") as f:
    f.write(flat_xml)

print("✅ Fast EPG XML saved with one-line channels and one-line programmes")

# -------------------------
# SUMMARY
# -------------------------
print(f"✅ Generated {OUTPUT_XML}")
print(f"📺 Total channels added: {len(seen_channels)}")
print("Channels and number of programs:")

# Count programs per channel
program_counts = {cid: 0 for cid in seen_channels}
for programme in programmes_to_add:
    cid = programme.get("channel")
    if cid in seen_channels:
        program_counts[cid] += 1

# Print results in alphabetical order
for cid in sorted_channel_ids:
    channel_name = CHANNELS.get(cid, "Unknown")
    print(f" - {channel_name} ({cid}): {program_counts[cid]} programs")