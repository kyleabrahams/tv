import subprocess
import time
import os
from datetime import datetime
# python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/vpn_iptv_checker-alive-txt.py

import requests

def get_latest_m3u(directory):
    """Find the most recent M3U file in the specified directory."""
    try:
        files = [f for f in os.listdir(directory) if f.startswith("alive-txt-") and f.endswith(".m3u")]
        if not files:
            print("No M3U files found in directory.")
            exit(1)
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(directory, f)))
        return os.path.join(directory, latest_file)
    except Exception as e:
        print(f"Error finding latest M3U file: {e}")
        exit(1)

# Path to your source M3U directory
SOURCE_M3U_DIR = "/Users/kyleabrahams/Documents/GitHub/tv/scripts/_alive"

def is_vpn_connected():
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=5)
        return response.json().get("ip") != "YOUR_REAL_IP"  # Replace with your actual IP
    except Exception as e:
        print(f"Error checking VPN connection: {e}")
        return False


def connect_vpn(vpn_config_path):
    """Connect to the VPN using OpenVPN."""
    try:
        print("Connecting to VPN...")
        subprocess.Popen(["sudo", "openvpn", "--config", vpn_config_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)  # Initial wait
        if is_vpn_connected():
            print("VPN connected successfully.")
        else:
            print("VPN connection failed.")
            exit(1)
    except Exception as e:
        print(f"Failed to start VPN: {e}")
        exit(1)


def run_iptv_checker(m3u_file_path, output_path):
    """Run the IPTV checker command."""
    if not os.path.exists(m3u_file_path):
        print(f"M3U file not found: {m3u_file_path}")
        exit(1)
    try:
        print(f"Running IPTV checker on {m3u_file_path}...")
        command = ["iptv-checker", m3u_file_path, "-o", output_path]
        subprocess.run(command, check=True)
        print("IPTV checker completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"IPTV checker failed: {e}")


def main():
    # Set the base directory relative to the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the ProtonVPN config file
    vpn_config_path = "/Users/kyleabrahams/Documents/_VPN/ca-90.protonvpn.udp.ovpn"

    # Get the latest M3U file
    m3u_file_path = get_latest_m3u(SOURCE_M3U_DIR)
    print(f"Using latest M3U file: {m3u_file_path}")

    # Define the output folder path
    output_path = os.path.join(base_dir, "_alive")

    # Ensure the '_alive' directory exists
    os.makedirs(output_path, exist_ok=True)

    # Connect to VPN
    connect_vpn(vpn_config_path)

    # Run IPTV checker
    run_iptv_checker(m3u_file_path, output_path)


if __name__ == "__main__":
    main()