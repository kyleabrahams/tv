from tqdm import tqdm  # add this at the top
import subprocess
import time
import os
from datetime import datetime
import shutil
import tempfile
import yaml


# vpn_iptv_checker-alive.py Mar 5 2026 928 am

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
VPN_USERNAME = os.environ.get("VPN_USERNAME")
VPN_PASSWORD = os.environ.get("VPN_PASSWORD")

# ProtonVPN config file (committed to repo, without credentials)
VPN_CONFIG = os.path.join("VPN", "ca.protonvpn.udp.ovpn")

VPN_WAIT = 10  # seconds to wait for VPN to connect

# ---------- FUNCTIONS ----------
def check_ffprobe():
    if shutil.which("ffprobe") is None:
        print("WARNING: 'ffprobe' not found. Install ffmpeg with 'brew install ffmpeg' to avoid errors.")
    else:
        print(f"ffprobe found at {shutil.which('ffprobe')}")


def connect_vpn(vpn_config_path):
    """Connect to VPN using credentials from environment variables."""
    if not VPN_USERNAME or not VPN_PASSWORD:
        raise ValueError("VPN_USERNAME or VPN_PASSWORD not set in environment")

    # Create temporary credentials file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(f"{VPN_USERNAME}\n{VPN_PASSWORD}\n")
        tmp_path = tmp.name

    # Start OpenVPN in background
    print("Starting VPN connection...")
    subprocess.Popen([
        "sudo", "openvpn",
        "--config", vpn_config_path,
        "--auth-user-pass", tmp_path
    ])
    print(f"Waiting {VPN_WAIT} seconds for VPN to establish...")
    time.sleep(VPN_WAIT)
    print("VPN should now be connected.")

    # Delete temporary file
    os.remove(tmp_path)

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


# ---------- CONFIG ----------
CREATE_LOG_FILE = True  # Set to False to skip writing offline_channel_log.yml

# ---------- FUNCTION ----------
def parse_and_check_m3u(m3u_path):
    """Check channels and optionally write offline channels to offline_channel_log.yml."""
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
    offline_channels = []

    # Progress bar
    with tqdm(total=total_channels, desc="Checking channels", unit="ch", dynamic_ncols=True) as pbar:
        for name, url in channel_list:
            alive = False
            if url and not url.startswith("#"):
                alive = check_channel_live(url)

            if not alive:
                offline_info = {
                    "channel": name,
                    "status": "No URL (offline)" if not url else "Offline"
                }
                offline_channels.append(offline_info)
                tqdm.write(f"*{name}: {offline_info['status']}")  # real-time offline output

            pbar.update(1)

    # Write YAML log if toggle is True
    if CREATE_LOG_FILE:
        log_path = os.path.join(os.getcwd(), "offline_channel_log.yml")
        with open(log_path, "w", encoding="utf-8") as log_file:
            yaml.dump({"offline_channels": offline_channels, "total_channels": total_channels}, log_file)

    # Print summary
    print("\nSummary:")
    print(f"Total channels: {total_channels}")
    print(f"Offline channels: {len(offline_channels)}")

# ---------- MAIN ----------
def main():
    check_ffprobe()
    connect_vpn(VPN_CONFIG)  # no VPN_CREDENTIALS anymore
    parse_and_check_m3u(SOURCE_M3U)


if __name__ == "__main__":
    main()