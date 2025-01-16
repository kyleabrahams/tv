import subprocess
import time
import datetime
import os

def connect_vpn(vpn_config_path):
    """Connect to the VPN using OpenVPN."""
    command = ["sudo", "openvpn", "--config", vpn_config_path]
    subprocess.Popen(command)

def run_iptv_checker(m3u_file_path, output_path):
    """Run the IPTV checker command."""
    command = ["iptv-checker", m3u_file_path, "-o", output_path]
    subprocess.run(command)

def main():
    # Set the base directory relative to the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the ProtonVPN config file (absolute path, as you provided)
    vpn_config_path = "/Users/kyleabrahams/Documents/_VPN/ca.protonvpn.udp.ovpn"
    
    # M3U file and output path for IPTV checker
    m3u_file_path = "/Users/kyleabrahams/Documents/GitHub/tv/list/list.m3u"
    output_path = "/Users/kyleabrahams/Documents/GitHub/tv/scripts/www"

    # Print the paths to verify
    print(f"VPN config path: {vpn_config_path}")
    print(f"M3U file path: {m3u_file_path}")
    print(f"Output path: {output_path}")

    # Connect to VPN
    connect_vpn(vpn_config_path)

    # Wait for VPN to establish
    time.sleep(10)

    # Run IPTV checker
    run_iptv_checker(m3u_file_path, output_path)

if __name__ == "__main__":
    main()
