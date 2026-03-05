from tqdm import tqdm  # add this at the top
import subprocess
import time
import os
from datetime import datetime
import shutil
import tempfile
import sys
# import yaml


# vpn_iptv_checker-alive.py Mar 5 2026 205 pm

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

# ---------- CONFIG ----------
# Source M3U file (full playlist) — relative to repo
SOURCE_M3U = os.path.join("list", "list.m3u")

# ProtonVPN credentials from GitHub Actions secrets
# Will fallback to local file if these are not set
VPN_USERNAME = os.environ.get("VPN_USERNAME")
VPN_PASSWORD = os.environ.get("VPN_PASSWORD")

# ProtonVPN config file (committed to repo, without credentials)
VPN_CONFIG = os.path.join("VPN", "ca.protonvpn.udp.ovpn")

VPN_WAIT = 10  # seconds to wait for VPN to connect

# Local credentials file (for Mac)
CRED_FILE = "/Volumes/Kyle4tb1223/Documents/_VPN/proton_credentials.txt"

# ---------- CREDENTIALS ----------
def load_vpn_credentials(local_file_path=None):
    creds = {}

    # 1️⃣ Try local file first
    if local_file_path and os.path.isfile(local_file_path):
        with open(local_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                creds[key.strip().lower()] = value.strip()

    # 2️⃣ Fallback to environment variables
    username = creds.get("username") or os.environ.get("VPN_USERNAME")
    password = creds.get("password") or os.environ.get("VPN_PASSWORD")

    if not username or not password:
        raise ValueError(
            f"VPN credentials not found. Make sure the file exists or set VPN_USERNAME and VPN_PASSWORD in the environment."
        )

    return username, password


# ---------- CREDENTIALS ----------
def load_vpn_credentials(local_file_path=None):
    global VPN_USERNAME, VPN_PASSWORD

    # Try local file first if environment variables not set
    if (not VPN_USERNAME or not VPN_PASSWORD) and local_file_path and os.path.isfile(local_file_path):
        with open(local_file_path, "r") as f:
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

    if not VPN_USERNAME or not VPN_PASSWORD:
        raise ValueError(
            "VPN credentials not found. Set VPN_USERNAME and VPN_PASSWORD as env variables or provide local credentials file."
        )


# ---------- VPN ----------
def connect_vpn(vpn_config_path, username, password):
    """Connect to VPN using provided credentials."""

    # Create temporary credentials file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(f"{username}\n{password}\n")
        tmp_path = tmp.name

    print("Starting VPN connection...", flush=True)

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

    print(f"Waiting {VPN_WAIT} seconds for VPN to establish...", flush=True)
    time.sleep(VPN_WAIT)
    print("VPN should now be connected.", flush=True)

    # Remove temporary credentials file
    os.remove(tmp_path)


# ---------- FFPROBE ----------
def check_ffprobe():
    if shutil.which("ffprobe") is None:
        print("WARNING: 'ffprobe' not found. Install ffmpeg with 'brew install ffmpeg' to avoid errors.")
    else:
        print(f"ffprobe found at {shutil.which('ffprobe')}")


# ---------- CHANNEL CHECK ----------
def check_channel_live(url):
    """Check if a stream is online using ffprobe."""
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


def parse_and_check_m3u(m3u_path):
    """Check channels and print offline channels in real-time."""
    if not os.path.isfile(m3u_path):
        raise FileNotFoundError(f"Source M3U not found: {m3u_path}")

    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"

    with open(m3u_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    channel_list = []
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            name = line.split(",", 1)[1] if "," in line else "Unknown"
            url = lines[i + 1] if i + 1 < len(lines) else None
            channel_list.append((name, url))

    offline_channels = []
    with tqdm(
        total=len(channel_list),
        desc="Checking channels",
        unit="ch",
        dynamic_ncols=True,
        disable=in_actions
    ) as pbar:
        for name, url in channel_list:
            alive = url and not url.startswith("#") and check_channel_live(url)
            if not alive:
                status = "No URL (offline)" if not url else "Offline"
                offline_channels.append((name, status))
                print(f"❌ {name}: {status}", flush=True)
            pbar.update(1)

    print("\nSummary:", flush=True)
    print(f"Total channels: {len(channel_list)}", flush=True)
    print(f"Offline channels: {len(offline_channels)}", flush=True)


# ---------- MAIN ----------
def main():
    check_ffprobe()
    load_vpn_credentials(CRED_FILE)  # sets VPN_USERNAME / VPN_PASSWORD
    connect_vpn(VPN_CONFIG, VPN_USERNAME, VPN_PASSWORD)
    parse_and_check_m3u(SOURCE_M3U)


if __name__ == "__main__":
    main()