# EPG Merger

This project merges multiple EPG XML files into a single XML file.


See Android TV sheets doc, nginx tab for commands,
sudo nginx -s reload
python3 merge_epg.py

## Installation of Nginx in Terminal for a local epg.xml

cd tv

    "https://www.bevy.be/bevyfiles/canadapremium.xml", 
    "https://www.bevy.be/bevyfiles/canadapremium2.xml",
    "https://www.bevy.be/bevyfiles/canadapremium3.xml",
    "https://www.bevy.be/bevyfiles/canada.xml",
    "https://i.mjh.nz/SamsungTVPlus/us.xml",
    "https://i.mjh.nz/SamsungTVPlus/ca.xml",
    "https://i.mjh.nz/PlutoTV/all.xml",
    "https://i.mjh.nz/Plex/all.xml",
    "https://i.mjh.nz/Stirr/all.xml",
    "https://i.mjh.nz/PBS/all.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium3.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium4.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium5.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium6.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium7.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdom.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium1.xml",

## Intel Mac IP Address
http://192.168.2.30:8080/epg.xml

## Check version

nginx -v

nginx     1234  0.1  0.2  295672  1234 ?        S    12:34   0:00 nginx: worker process

nada             85580   0.0  0.0 33598548    820 s003  S+    8:18PM   0:00.00 grep nginx

## Alternative way to start Nginx

brew services start nginx


## Verify epg.xml works

http:/localhost:8080/epg.xml


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
