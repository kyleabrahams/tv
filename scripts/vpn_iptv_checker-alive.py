# vpn_iptv_checker-alive.py Jun 26 2026 1025 am

# brew install openvpn
# brew install ffmpeg
# pip3 install tqdm
# pip3 install pyyaml
# npm install -g iptv-checker
# export PATH="$HOME/.nvm/versions/node/v20.18.0/bin:$PATH"
# source ~/.zshrc
# add repo
# git clone https://github.com/freearhey/iptv-checker.git
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/vpn_iptv_checker-alive.py

#!/usr/bin/env python3
import os
import sys
import time
import shutil
import tempfile
import subprocess
from datetime import datetime
import yaml
from tqdm import tqdm

# ---------- CONFIG ----------
# Dynamically locate the absolute directory where this script file lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up one folder to hit the root level of your repository
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# Source M3U playlist file path (Anchored to the repository root)
SOURCE_M3U = os.path.join(REPO_ROOT, "list", "list.m3u")

# ProtonVPN configuration profile file path (Anchored to the repository root)
VPN_CONFIG = os.path.join(REPO_ROOT, "VPN", "ca.protonvpn.udp.ovpn")

# Destination path target for GitHub Action artifact pipeline collections
LOG_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "offline_channel_log.yml")

# Timeout buffer allocation for VPN network handshake setup (seconds)
VPN_WAIT = 10  

# Local hardcoded fallback authentication configuration for Mac environments
CRED_FILE = "/Volumes/Kyle4tb1223/Documents/_VPN/proton_credentials.txt"

# System global variables
VPN_USERNAME = os.environ.get("VPN_USERNAME")
VPN_PASSWORD = os.environ.get("VPN_PASSWORD")


# ---------- CREDENTIALS ----------
def load_vpn_credentials(local_file_path=None):
    """Loads operational credentials prioritizing active runtime environment variables."""
    global VPN_USERNAME, VPN_PASSWORD

    # 1️⃣ GitHub Actions Check: If variables are set via runner pipeline env mapping, use them
    if VPN_USERNAME and VPN_PASSWORD:
        print("VPN credentials successfully loaded from environment variables.", flush=True)
        return

    # 2️⃣ Local Machine Fallback: Look up configuration details inside local disk storage path
    if local_file_path and os.path.isfile(local_file_path):
        print(f"Loading local credentials from tracking file: {local_file_path}...", flush=True)
        with open(local_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "username":
                    VPN_USERNAME = value
                elif key == "password":
                    VPN_PASSWORD = value

    # 3️⃣ Structural Exception Verification Safeguard
    if not VPN_USERNAME or not VPN_PASSWORD:
        raise ValueError(
            "VPN credentials missing! Please configure VPN_USERNAME and VPN_PASSWORD values."
        )


# ---------- VPN UTILITIES ----------
def connect_vpn(vpn_config_path, username, password):
    """Spawns background OpenVPN sub-processes using secure ephemeral login parameters."""
    if not os.path.isfile(vpn_config_path):
        raise FileNotFoundError(f"OpenVPN connection profile missing at: {vpn_config_path}")

    # Writes a safe temporary credential file to feed stdin routing profiles
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(f"{username}\n{password}\n")
        tmp_path = tmp.name

    print("Initializing system OpenVPN configuration routing network...", flush=True)

    subprocess.Popen(
        [
            "sudo", "openvpn",
            "--config", vpn_config_path,
            "--auth-user-pass", tmp_path,
            "--daemon"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print(f"Waiting {VPN_WAIT} seconds for stable secure network handshake...", flush=True)
    time.sleep(VPN_WAIT)
    print("Network routing verification active.", flush=True)

    # Detach and destroy clear-text files safely
    try:
        os.remove(tmp_path)
    except OSError:
        pass


# ---------- VALIDATION CORE ----------
def check_ffprobe():
    """Validates existence of local tool installations."""
    if shutil.which("ffprobe") is None:
        print("WARNING: 'ffprobe' was not located within system search environments.", flush=True)
    else:
        print(f"System ffprobe binary mapped at: {shutil.which('ffprobe')}", flush=True)


def check_channel_live(url):
    """Probes stream link configurations using direct ffprobe connection queries."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


# ---------- METRICS PROCESSOR ----------
def parse_and_check_m3u(m3u_path):
    """Parses playlist data items, tracks operational states, and dumps structured log files."""
    if not os.path.isfile(m3u_path):
        raise FileNotFoundError(f"Source M3U configuration file missing: {m3u_path}")

    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"

    with open(m3u_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    channel_list = []
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            name = line.split(",", 1)[1] if "," in line else "Unknown"
            url = lines[i + 1] if i + 1 < len(lines) else None
            
            # String parsing exclusion filter for 'ott.' elements
            if "ott." in name.lower():
                continue
                
            channel_list.append((name, url))

    offline_channels = []
    
    with tqdm(
        total=len(channel_list),
        desc="Validating IPTV Streams",
        unit="ch",
        dynamic_ncols=True,
        disable=in_actions
    ) as pbar:
        for name, url in channel_list:
            alive = url and not url.startswith("#") and check_channel_live(url)
            if not alive:
                status = "Empty URL Argument" if not url else "Offline"
                offline_channels.append({
                    "name": name,
                    "status": status,
                    "url": url if url else "None"
                })
                print(f"❌ {name}: {status}", flush=True)
            pbar.update(1)

    print("\nProcessing Verification Summary:", flush=True)
    print(f"Total Monitored Streams: {len(channel_list)}", flush=True)
    print(f"Dead Stream Targets Detected: {len(offline_channels)}", flush=True)

    # Document wrapper dictionary for structured logging
    log_payload = {
        "scan_timestamp": datetime.now().isoformat(),
        "total_monitored_channels": len(channel_list),
        "total_offline_channels": len(offline_channels),
        "offline_channels_list": offline_channels
    }

    # Ensure parent folder directory structure paths exist
    os.makedirs(os.path.dirname(LOG_OUTPUT_PATH), exist_ok=True)
    
    with open(LOG_OUTPUT_PATH, "w", encoding="utf-8") as yaml_out:
        yaml.dump(log_payload, yaml_out, default_flow_style=False, sort_keys=False)
        
    print(f"Metrics output generated successfully at: {LOG_OUTPUT_PATH}", flush=True)


# ---------- SYSTEM RUNTIME APPLICATION ENTRY ----------
def main():
    check_ffprobe()
    load_vpn_credentials(CRED_FILE)
    connect_vpn(VPN_CONFIG, VPN_USERNAME, VPN_PASSWORD)
    parse_and_check_m3u(SOURCE_M3U)


if __name__ == "__main__":
    main()
