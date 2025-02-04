# EPG Multitool: 

This project is a custom tool that creates dummy data, fetches URLs, and uncompresses .gz files, ultimately generating a single XML file. The XML file(s) are stored locally in your repository and can be accessed through Nginx (Homebrew).
I'm hoping to add remote access in the near future.

## Tool 1. IPTV-Checker is a utility designed to verify the status of links in M3U playlists. It categorizes each link as online, offline, or a duplicate.

# IPTV-Checker global installation
npm install -g iptv-checker epg-grabber @freearhey/core @freearhey/epg-grabber typescript tsx axios xml2js dotenv commander cron

npm install @freearhey/core commander cron epg-grabber

pip install requests pytz


# NPM packages installed
npm list -g --depth=0

# Channel Sources
https://github.com/awiouy/webgrabplus/blob/master/config/siteini.pack/Canada/canada.com.L9H1N3.channels.xml

https://www.npmjs.com/package/@iptv/xmltv?activeTab=readme

# Playlist execution
iptv-checker /path/to/playlist.m3u -o /path/to/output/directory/ServerNameHere_$(date +%Y%m%d)"

## Tool 2: Playlist-Generator is a utility designed to generate an M3U playlist with a specified range of channel numbers (e.g., 1-100). Its primary purpose is to identify hidden or non-public channels at the server level.
# Modify the python file below and run it with the command below
cd scripts
python3 playlist_generator.py

## Step 1: In the working directory, run the following command in Terminal to create the node modules:
npm install

# Step 1b: If you wish to uninstall node modules run:
rm package-lock.json
rm -rf node_modules

## Step 2: A virtual Python environment may be necessary; run the following command:
python3 -m venv ~/venv
source ~/venv/bin/activate
python3 merge_epg.py


## Step 3: To fully automate the remaining installation, run the following script:
cd scripts
python3 install_all.py

## Step 3b: If you wish to uninstall everything and leave only the base files, run the following command:
cd scripts
python3 uninstall_all.py

## Step 4: To manually update the epg.xml file, run the following command:
cd scripts
python3 merge_epg.py
nohup python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg.py > my_output.log 2>&1 &

# If you want to verify if it's actively running, you can use:
launchctl status com.kyleabrahams.mergeepg

# If you want to stop or unload the job:
launchctl bootout user/$(id -u) /Users/kyleabrahams/Library/LaunchAgents/com.kyleabrahams.mergeepg.plist

# If you'd like to reload or restart the job:
launchctl bootload user/$(id -u) /Users/kyleabrahams/Library/LaunchAgents/com.kyleabrahams.mergeepg.plist


## Step 5: To access the epg.xml file in a web browser, paste the following URL:
http:/localhost:8080/epg.xml

## Step 6: To modify the scheduling for the merge_epg.py in crontab (macOS), enter the following command in Terminal:
crontab -e

https://tinyurl.com/multiservice21?region=ca&service=SamsungTVPlus
https://tinyurl.com/multiservice21?region=us&service=SamsungTVPlus
https://tinyurl.com/multiservice21?region=ca&service=Plex


npm run channels:parse --- --config=./sites/tvpassport.com/tvpassport.com.config.js --output=./sites/tvpassport.com/tvpassport.com.channels.xml

npm run grab -- --channels=./scripts/_epg-start/channels_custom_start_TEST.xml --output=./_epg-end/channels_custom_end_Test.xml

npm run grab -- --channels=./scripts/_epg-start/channels_custom_start_output.xml --output=./scripts/_epg-end/channels_custom_end_output.xml

# Codespace
source venv/bin/activate

python3 merge_epg_cs.py

python3 merge_epg_cs.py update update || exit 1

act -W .github/workflows/channel-fetch.yml -j channel-fetch



https://raw.githubusercontent.com/kyleabrahams/tv/main/scripts/www/epg.xml