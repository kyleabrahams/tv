from tqdm import tqdm  # add this at the top
import subprocess
import time
import os
from datetime import datetime
import shutil

# vpn_iptv_checker-alive.py Mar 5 2026 928 am

# brew install openvpn
# brew install ffmpeg
# pip3 install tqdm
# npm install -g iptv-checker
# export PATH="$HOME/.nvm/versions/node/v20.18.0/bin:$PATH"
# source ~/.zshrc
# add repo
# git clone https://github.com/freearhey/iptv-checker.git
# python3 /Volumes/Kyle4tb1223/Documents/Github/tv/scripts/vpn_iptv_checker-alive.py

# ---------- CONFIG ----------
# Source M3U file (full playlist)
SOURCE_M3U = "/Volumes/Kyle4tb1223/Documents/Github/tv/list/list.m3u"

# ProtonVPN files
VPN_CONFIG = "/Volumes/Kyle4tb1223/Documents/_VPN/ca.protonvpn.udp.ovpn"
VPN_CREDENTIALS = "/Volumes/Kyle4tb1223/Documents/_VPN/proton_credentials.txt"

VPN_WAIT = 10  # seconds to wait for VPN to connect

# ---------- FUNCTIONS ----------
def check_ffprobe():
    if shutil.which("ffprobe") is None:
        print("WARNING: 'ffprobe' not found. Install ffmpeg with 'brew install ffmpeg' to avoid errors.")
    else:
        print(f"ffprobe found at {shutil.which('ffprobe')}")

def connect_vpn(vpn_config_path, credentials_path):
    """Connect to VPN in the background."""
    if not os.path.isfile(vpn_config_path) or not os.path.isfile(credentials_path):
        raise FileNotFoundError("VPN config or credentials not found.")
    
    print("Starting VPN connection...")
    subprocess.Popen([
        "sudo", "openvpn",
        "--config", vpn_config_path,
        "--auth-user-pass", credentials_path
    ])
    print(f"Waiting {VPN_WAIT} seconds for VPN to establish...")
    time.sleep(VPN_WAIT)
    print("VPN should now be connected.")

def check_channel_live(url):
    """Check if a stream is online using ffprobe with proper return code."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15  # increase timeout for slow streams
        )
        # ffprobe returns 0 if stream is valid
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def parse_and_check_m3u(m3u_path):
    """Check channels with a stable progress bar at the bottom."""
    if not os.path.isfile(m3u_path):
        raise FileNotFoundError(f"Source M3U not found: {m3u_path}")

    with open(m3u_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Build channel list
    channel_list = []
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            try:
                name = line.split(",", 1)[1]
            except IndexError:
                name = "Unknown"
            url = lines[i + 1] if i + 1 < len(lines) else None
            channel_list.append((name, url))

    total_channels = len(channel_list)
    offline_channels = 0

    # Use a proper tqdm bar
    with tqdm(total=total_channels, desc="Checking channels", unit="ch", dynamic_ncols=True) as pbar:
        for name, url in channel_list:
            alive = False
            if url and not url.startswith("#"):
                alive = check_channel_live(url)

            if not alive:
                offline_channels += 1
                tqdm.write(f"{name}: {'No URL (offline)' if not url else 'Offline'}")

            pbar.update(1)

    # Summary
    print("\nSummary:")
    print(f"Total channels: {total_channels}")
    print(f"Offline channels: {offline_channels}")


# ---------- MAIN ----------
def main():
    check_ffprobe()
    connect_vpn(VPN_CONFIG, VPN_CREDENTIALS)
    parse_and_check_m3u(SOURCE_M3U)


if __name__ == "__main__":
    main()