#m3u_list_fetch.py
# python3 m3u_list_fetch.py

import os
import requests
import random
import re
import subprocess
import time
import tempfile
import urllib3
import socket
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- CONFIGURATION ----------
INPUT_FILE = "m3u_list.txt"
BASE_OUTPUT_DIR = "/Volumes/Kyle4tb1223/_Android/_M3U/____Fetched"
CHANNELS_TO_CHECK = 3 
SAVE_INACTIVE = False 

VPN_CONFIG = os.path.join("VPN", "ca.protonvpn.udp.ovpn")
CRED_FILE = "/Volumes/Kyle4tb1223/Documents/_VPN/proton_credentials.txt"
VPN_WAIT = 15

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 safari/537.36'}

# ---------- UTILS ----------
def load_vpn_credentials(local_file_path):
    user, pw = None, None
    if os.path.isfile(local_file_path):
        with open(local_file_path, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key.strip().lower() == "username": user = value.strip()
                    if key.strip().lower() == "password": pw = value.strip()
    return user, pw

def connect_vpn(config_path, user, pw):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(f"{user}\n{pw}\n")
        tmp_path = tmp.name
    print(f"Connecting to VPN...", flush=True)
    subprocess.Popen(["sudo", "openvpn", "--config", config_path, "--auth-user-pass", tmp_path, "--daemon"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(VPN_WAIT)
    os.remove(tmp_path)

def check_channel_live(url):
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", url],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
        return result.returncode == 0
    except: return False

def draw_progress_bar(current, total, bar_length=30):
    percent = float(current) / total
    arrow = '█' * int(round(percent * bar_length))
    spaces = '░' * (bar_length - len(arrow))
    sys.stdout.write(f"\rProgress: [{arrow}{spaces}] {int(round(percent * 100))}% ({current}/{total})")
    sys.stdout.flush()

# ---------- MAIN PROCESS ----------
def run_fetcher():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_FILE)
    active_total, inactive_total = 0, 0

    if not os.path.exists(input_path):
        print(f"Error: {INPUT_FILE} not found!"); return

    session = requests.Session()
    session.headers.update(HEADERS)

    with open(input_path, "r") as file:
        content = file.read()

    blocks = [b.strip() for b in re.split(r'(?=http://|https://)', content) if b.strip()]
    total_blocks = len(blocks)
    now = datetime.now()

    print(f"🚀 Starting fetch for {total_blocks} entries...\n")

    for index, block in enumerate(blocks, start=1):
        try:
            # 1. Extract Data
            url_match = re.search(r'(http[^\s]+)', block)
            if not url_match:
                draw_progress_bar(index, total_blocks)
                continue
            url = url_match.group(1)
            
            # Parse the actual downloaded URL directly
            parsed_url = urlparse(url)
            
            # A. Extract Username from URL query
            username = parse_qs(parsed_url.query).get('username', ['unknown'])[0]

            # B. Extract Server name from URL host
            netloc_clean = parsed_url.netloc.split(':')[0]  # Strips ports
            
            if netloc_clean and not netloc_clean[0].isdigit():
                domain_parts = netloc_clean.split('.')
                
                # Check if the first word is "server" and there are more words available
                if domain_parts[0].lower() == "server" and len(domain_parts) > 1:
                    server_name = domain_parts[1] # Choose the next word (e.g., iptvxxx)
                else:
                    server_name = domain_parts[0] # Normal behavior (e.g., bgdc or lunar)
            else:
                server_name = netloc_clean.replace('.', '-')

            # 2. Expiry Check & Format
            exp_match = re.search(r'Expires:\s*(\d{2}/\d{2}/\d{4})', block)
            exp_date_str = "NoExp"
            if exp_match:
                exp_dt = datetime.strptime(exp_match.group(1), "%d/%m/%Y")
                exp_date_str = exp_dt.strftime("%b %d %Y")
                
                if exp_dt < now:
                    inactive_total += 1
                    draw_progress_bar(index, total_blocks)
                    continue

            # 3. Verification
            resp = session.get(url, timeout=20, verify=False)
            if resp.status_code != 200: 
                raise Exception()

            channels = re.findall(r'^http.*$', resp.text, re.MULTILINE)
            if not channels: 
                raise Exception()

            sample = random.sample(channels, min(len(channels), CHANNELS_TO_CHECK))
            is_live = any(check_channel_live(ch.strip()) for ch in sample)

            # 4. Save
            if is_live:
                active_total += 1
                status = "Active"
            else:
                inactive_total += 1
                status = "Inactive"

            # Resulting Format: Jul 27 2026-iptvxxx-cprimemain.m3u
            filename = f"{exp_date_str}-{server_name}-{username}.m3u"

            if is_live or SAVE_INACTIVE:
                final_dir = os.path.join(BASE_OUTPUT_DIR, status)
                os.makedirs(final_dir, exist_ok=True)
                with open(os.path.join(final_dir, filename), "w", encoding="utf-8") as f:
                    f.write(resp.text)

        except Exception:
            inactive_total += 1
        
        draw_progress_bar(index, total_blocks)

    print(f"\n\n{'='*40}\n ✅ Active: {active_total}\n ❌ Inactive: {inactive_total}\n{'='*40}\n")

if __name__ == "__main__":
    u, p = load_vpn_credentials(CRED_FILE)
    connect_vpn(VPN_CONFIG, u, p)
    run_fetcher()
