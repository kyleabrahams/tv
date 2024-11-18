#!/bin/bash

# Define variables
API_TOKEN=$CLOUDFLARE_API_TOKEN
ZONE_ID="your_zone_id"
DOMAIN="example.com"
SUBDOMAIN="sub.example.com"
TARGET_FOLDER="/usr/local/var/www"
RECORD_TYPE="A"
RECORD_NAME="sub.example.com"
RECORD_CONTENT="your_server_ip"

# Create a DNS record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "A",
       "name": "sub.example.com",
       "content": "your_server_ip",
       "ttl": 1,
       "proxied": true
     }'

# Optional: Sync your EPG.xml file to the folder
rsync -avz /usr/local/var/www/epg.xml $TARGET_FOLDER
