# EPG Merger

This project merges multiple EPG XML files into a single XML file.
See Android TV sheets doc, nginx tab for commands,

## Manually merges xml urls into one big xml
python3 merge_epg.py

## Installation of Nginx in Terminal for a local epg.xml
./install_nginx.sh

##  Version Check
nginx -v

##  Status Check
sudo nginx -t

## Reload Nginx
sudo nginx -s reload

## Verify epg.xml works
http:/localhost:8080/epg.xml

## Uninstall Nginx
sudo brew services stop nginx

sudo rm -rf /opt/homebrew/Cellar/nginx/1.27.2
sudo rm -rf /usr/local/var/www



    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://i.mjh.nz/Stirr/all.xml",
    "https://i.mjh.nz/PBS/all.xml",
    "https://www.bevy.be/bevyfiles/unitedstates1.xml",
    "https://www.bevy.be/bevyfiles/unitedstates2.xml",
    "https://www.bevy.be/bevyfiles/unitedstates3.xml",





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
