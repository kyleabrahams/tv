with open("playlist.m3u8", "r") as file:
    for line in file:
        line = line.strip()
        if line and not line.startswith("#"):  # Skip metadata lines
            print(line)  # Print URLs
