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

def main():
    # Set the base directory relative to the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the ProtonVPN config file
    vpn_config_path = os.path.join(base_dir, "../_VPN/ca.protonvpn.udp.ovpn")
    
    # M3U file and output path for IPTV checker
    m3u_file_path = os.path.join(base_dir, "../list/list.m3u")
    output_path = os.path.join(base_dir, "www")

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

    # Commit and push changes in the www folder
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-update IPTV files at {current_time}"
    commit_and_push_changes(output_path, commit_message)

if __name__ == "__main__":
    main()
