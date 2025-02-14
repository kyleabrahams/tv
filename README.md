# EPG Multitool: 

This project is a custom tool that creates dummy data, fetches URLs, and uncompresses .gz files, ultimately generating a single XML file. The XML file(s) are stored locally in your repository and can be accessed through Nginx (Homebrew).
I'm hoping to add remote access in the near future.

## Tool 1. IPTV-Checker is a utility designed to verify the status of links in M3U playlists. It categorizes each link as online, offline, or a duplicate.
# IPTV-Checker etc global installation
npm install -g epg-grabber jest typescript ts-node @ntlab/sfetch @octokit/plugin-rest-endpoint-methods

iptv-checker

# See Android TV sheets doc, nginx tab for commands,

# Nginx.conf path 
/opt/homebrew/etc/nginx/nginx.conf

# Nginx reload
sudo nginx -s reload
ps aux | grep nginx
sudo nginx -t


# Run scripts 
cd scripts
python3 -m venv myenv
source myenv/bin/activate
source venv/bin/activate


python3 merge_epg.py 
python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg.py
python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg-test.py

python3 dummy_epg.py

# Github Commit issues resolve

git add .
git commit -m "Updated files"
git push origin main


# RUN script manually to debug
source /Users/kyleabrahams/Documents/GitHub/tv/scripts/venv/bin/activate && /Users/kyleabrahams/Documents/GitHub/tv/scripts/venv/bin/python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg.py



# Below used to grab xumo.tv (5.1 mb xml file) and other sites https://github.com/iptv-org/epg
npm run grab -- --site=xumo.tv
npm run grab -- --channels=sites/ontvtonight.com/ontvtonight.com_ca.channels.xml --output=./scripts/ontvtonight.com_ca.channels.xml
npm run channels:parse --- --config=./sites/ontvtonight.com/ontvtonight.com.config.js --output=./scripts/ontvtonight.com_ca.channels.xml --set=country:ca

# Step 3: Function to run the npm grab command and show real-time output https://github.com/iptv-org/epg/tree/master/sites
npm run grab --- --channels=channels_custom_start.xml --output ./scripts/channels_custom_end.xml
npm run grab --- --channels=./scripts/_epg-start/channels-test-start.xml --output ./scripts/_epg-end/channels-test-end.xml

npm run grab --- --channels=./scripts/_Search_Results/_Channels-grouped-to-sites/dstv.com_channels.xml --output ./scripts/_Search_Results/_Channels-xml-end/dstv.com_channels-end.xml


/usr/bin/python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/vpn_iptv_checker.py
source /Users/kyleabrahams/Documents/GitHub/tv/scripts/venv/bin/activate && python3 /Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg.py >> /Users/kyleabrahams/Documents/GitHub/tv/scripts/www/cron_job.log 2>&1
# NPM run test
npm run grab --- --channels=./scripts/_epg-start/channels-custom-start.xml --output ./scripts/_epg-end/channel-custom-start-$(date +%Y%m%d).xml

npm run grab --- --channels=./scripts/_epg-start/channels-test-start.xml --output ./scripts/_epg-end/channel-test-start-end.xml

# TV Lists
# Regions all (for all regions)
# ar (Argentina) br (Brazil) ca (Canada) cl (Chile) de (Germany) dk (Denmark) es (Spain) 
# fr (France) gb (United Kingdom) mx (Mexico) no (Norway) se (Sweden) us (United States)
https://tinyurl.com/multiservice21?region=ADD_REGION&service=ADD_SERVICE

https://tinyurl.com/multiservice21?region=ca&service=Plex
https://tinyurl.com/multiservice21?region=ca&service=Roku
https://tinyurl.com/multiservice21?region=all&service=SamsungTVPlus
https://tinyurl.com/multiservice21?region=ca&service=SamsungTVPlus
https://tinyurl.com/multiservice21?region=us&service=SamsungTVPlus
https://tinyurl.com/multiservice21?region=ca&service=PlutoTV
https://tinyurl.com/multiservice21?region=ca&service=PBS
https://tinyurl.com/multiservice21?region=ca&service=PBSKids
https://tinyurl.com/multiservice21?region=ca&service=Stirr
https://tinyurl.com/multiservice21?region=ca&service=Tubi

# Playlist execution
iptv-checker /path/to/playlist.m3u -o /path/to/output/directory/ServerNameHere-$(date +%Y%m%d)

# URL check
iptv-checker /Volumes/Kyle4tb1223/_Android/_M3U/___X/X_plus.m3u -o /Users/kyleabrahams/Documents/___ServersFULL/Checked/X_plus-$(date +%Y%m%d)

iptv-checker https://raw.githubcontent.com/mikefoxwell/x_plus/blob/main/X_plus.m3u -o /Users/kyleabrahams/Documents/___ServersFULL/Checked/X_plus-$(date +%Y%m%d)

# Local file check
iptv-checker /Users/kyleabrahams/Documents/___ServersFULL/Steve-Cyprus.m3u -o /Users/kyleabrahams/Documents/___ServersFULL/Checked/Steve-Cyprus-1-1mill-$(date +%Y%m%d)

# Specifc expiry check
iptv-checker /Users/kyleabrahams/Documents/___ServersFULL/extraott-262264-1mill-20250110.m3u -o /Users/kyleabrahams/Documents/___ServersFULL/Checked/extraott-20250110

# List.m3u expiry check
iptv-checker /Users/kyleabrahams/Documents/GitHub/tv/list/list.m3u -o /Users/kyleabrahams/Documents/GitHub/tv/scripts/www
iptv-checker ./list/list.m3u -o ./scripts/www

# Servers expiry check
iptv-checker /Users/kyleabrahams/Documents/___ServersFULL/SERVER-EXPIRY-TEST.m3u -o /Users/kyleabrahams/Documents/___ServersFULL/Checked/_SERVERS-1-1mill--$(date +%Y%m%d)

# i.mjh.nz channels.xml updates
npm run channels:parse --- --config=./sites/i.mjh.nz/i.mjh.nz.config.js --output=./sites/i.mjh.nz/i.mjh.nz_pluto.channels.xml --set=provider:pluto
npm run channels:parse --- --config=./sites/i.mjh.nz/i.mjh.nz.config.js --output=./sites/i.mjh.nz/i.mjh.nz_plex.channels.xml --set=provider:plex
npm run channels:parse --- --config=./sites/i.mjh.nz/i.mjh.nz.config.js --output=./sites/i.mjh.nz/i.mjh.nz_samsung.channels.xml --set=provider:samsung

npm run channels:parse --- --config=./sites/i.mjh.nz/i.mjh.nz.config.js --output=./sites/i.mjh.nz/i.mjh.nz_samsung.channels.xml --set=provider:samsung

npm run channels:parse --- --config=./sites/xumo.tv/xumo.tv.config.js --output=./sites/xumo.tv/xumo.tv.channels.xml


npm run channels:parse --- --config=./sites/tvtv.us/tvtv.us.config.js --output=./sites/tvtv.us/tvtv.us.channels.xml

npm run channels:parse --- --config=./sites/i.mjh.nz/i.mjh.nz.config.js --output=./sites/i.mjh.nz/i.mjh.nz_samsung.channels.xml --set=provider:samsung

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

## Step 3: To fully automate the remaining installation, run the following script:
cd scripts
python3 install_all.py

## Step 3b: If you wish to uninstall everything and leave only the base files, run the following command:
cd scripts
python3 uninstall_all.py

## Step 4: To manually update the epg.xml file, run the following command:
cd scripts
python3 merge_epg.py

## Step 5: To access the epg.xml file in a web browser, paste the following URL:
http:/localhost:8080/epg.xml

## Step 6: To modify the scheduling for the merge_epg.py in crontab (macOS), enter the following command in Terminal:
crontab -e
