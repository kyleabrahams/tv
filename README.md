# EPG Merger

The project is designed to merge multiple EPG XML files into a single XML file that is stored locally on the computer where the repository is cloned. This process helps consolidate EPG data for easier access and management.

*See Android TV sheets doc, nginx tab for epg.xml creation frequency,

## Step 1 in the working directory in Terminal run: (for node modules)
npm install

# If you want to Uninstall npm (node modules)
rm package-lock.json
rm -rf node_modules

# Step 2.Create Virtual Environment for Python
python3 -m venv ~/venv
source ~/venv/bin/activate

# Step 3. Run this script
cd scripts
python3 install_all.py


# Step 1a. Installation of Nginx in Terminal for http:/localhost:8080/epg.xml
chmod +x install_all.sh
./install_all.py

## Step 1b. To uninstall Nginx and remove the local epg.xml, run:
chmod +x uninstall_nginx.sh
./uninstall_nginx.sh


## Step 2. Verify epg.xml is accessible via:
http:/localhost:8080/epg.xml


# Step 3. Schedule EPG Merges with Cron (macOS)
## Step 3a. Open crontab via Terminal command:
crontab -e

## Step 3b. Add the following cron jobs:

## Run EPG merge script every 6 hours and log output
0 */6 * * * /usr/local/bin/python3 /path/to/Github/tv/merge_epg.py >> /path/to/Documents/Github/tv/epg_merge.log 2>&1

# Reload Nginx every 6 hours after the EPG update and log output
5 */6 * * * sudo nginx -s reload >> /path/to/Documents/Github/tv/nginx_reload.log 2>&1

## Step 3c. Save and close with
Esc, :wq, Enter


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