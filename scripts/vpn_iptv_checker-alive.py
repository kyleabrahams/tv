import subprocess
import time
import os

def connect_vpn(vpn_config_path):
    """Connect to the VPN using OpenVPN."""
    command = ["sudo", "openvpn", "--config", vpn_config_path]
    subprocess.Popen(command)

def run_iptv_checker(m3u_file_path, output_path):
    """Run the IPTV checker command."""
    command = ["iptv-checker", m3u_file_path, "-o", output_path]
    subprocess.run(command)

def commit_and_push_changes(directory, commit_message):
    """Commit and push changes in the specified directory to GitHub."""
    try:
        # Stage all changes in the specified directory
        subprocess.run(["git", "add", directory], check=True)
        
        # Commit the staged changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push the committed changes to the remote repository
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print(f"Changes in {directory} successfully committed and pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Error committing or pushing changes: {e}")

from datetime import datetime

def main():
    # Set the base directory relative to the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the ProtonVPN config file
    vpn_config_path = os.path.join(base_dir, "../_VPN/ca.protonvpn.udp.ovpn")
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS

    # Generate the M3U file path with dynamic timestamp
    m3u_file_path = os.path.join(base_dir, "_alive", f"alive_{timestamp}.m3u")

    # Define the output folder path
    output_path = os.path.join(base_dir, "_alive")

    # Ensure the '_alive' directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Print paths for debugging
    print(f"M3U file will be saved at: {m3u_file_path}")
    print(f"Output folder: {output_path}")

    # Connect to VPN
    connect_vpn(vpn_config_path)

    # Wait for VPN to establish
    time.sleep(10)

    # Run IPTV checker
    run_iptv_checker(m3u_file_path, output_path)

    # Commit and push changes in the www folder
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-update IPTV files at {current_time}"
    commit_and_push_changes(output_path, commit_message)

if __name__ == "__main__":
    main()
