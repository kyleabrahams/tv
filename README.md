# EPG Merger

This project merges multiple EPG XML files into a single XML file found locally on the computer with the cloned repo.

*See Android TV sheets doc, nginx tab for epg.xml creation frequency,

## Step 1. Installation of Nginx in Terminal for a (http:/localhost:8080/epg.xml)
chmod +x install_nginx.sh
./install_nginx.sh

## Step 1a. Verify epg.xml works
http:/localhost:8080/epg.xml

## Step 1b. Uninstallation of Nginx in Terminal for removing the local epg.xml
chmod +x uninstall_nginx.sh
./uninstall_nginx.sh

## Step 2. Setup crontab to help schedule when to refresh epg.xml (macOS)
## Step 2a. Terminal command:
crontab -e

## Step 2b. Copy & Paste:

# Run EPG merge script every 6 hours and log output
0 */6 * * * /usr/local/bin/python3 /path/to/Github/tv/merge_epg.py >> /path/to/Documents/Github/tv/epg_merge.log 2>&1

# Reload Nginx every 6 hours after the EPG update and log output
5 */6 * * * sudo nginx -s reload >> /path/to/Documents/Github/tv/nginx_reload.log 2>&1

## Step 2c. Terminal command to complete:
Esc, :wq, Enter

## Step 3. Install install_pureFTP.sh in Terminal:
chmod +x install_pureFTP.sh
./install_pureFTP.sh


## Terminal command to manually merge xml urls into one big local epg.xml
python3 merge_epg.py

##  Version Check
nginx -v

##  Status Check
sudo nginx -t

## Reload Nginx
sudo nginx -s reload

## Uninstall Nginx
sudo brew services stop nginx

sudo rm -rf /opt/homebrew/Cellar/nginx/1.27.2
sudo rm -rf /usr/local/var/www












# timed merge_epg.py script using nginx to run through out the day 

Terminal commad:
sudo crontab -e

Copy & paste:
# Run EPG merge script every 6 hours and log output
0 */6 * * * /usr/local/bin/python3 /Volumes/Kyle4tb1223/Documents/Github/tv/merge_epg.py >> /Volumes/Kyle4tb1223/Documents/Github/tv/epg_merge.log 2>&1

# Reload Nginx every 6 hours after the EPG update and log output
5 */6 * * * sudo nginx -s reload >> /Volumes/Kyle4tb1223/Documents/Github/tv/nginx_reload.log 2>&1

Terminal commad:
Esc, :wq , Enter, to save

# Nginx structure for github automation
nginx-setup/
│
├── nginx.conf
├── default.conf
├── install_nginx.sh
└── README.md

# /Users/kyleabrahams/Documents/GitHub/tv/
├── core/
│   └── index.js         # Contains the exampleFunction
├── app.js               # Main app file importing from core
├── node_modules/        # Installed dependencies
├── package.json         # Npm configuration file
├── install.sh           # Installation script
└── other_files/         # Other files in the project

# Grabber structure
/project-root
  ├── /src
  │   ├── /core
  │   │   ├── QueueCreator.ts
  │   │   ├── Job.ts
  │   │   ├── ChannelsParser.ts
  │   ├── /sites
  │   │   ├── <site-specific-files>
  │   ├── constants.ts
  │   ├── grabber.ts (your provided code)
  ├── /test
  │   ├── QueueCreator.test.ts
  │   ├── Job.test.ts
  │   ├── ChannelsParser.test.ts
  ├── package.json
  ├── tsconfig.json