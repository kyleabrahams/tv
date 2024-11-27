# EPG Multitool: 

This project is a custom tool that creates dummy data, fetches URLs, and uncompresses .gz files, ultimately generating a single XML file. The XML file(s) are stored locally in your repository and can be accessed through Nginx (Homebrew).
I'm hoping to add remote access in the near future.

## Step 1: In the working directory, run the following command in Terminal to create the node modules:
npm install

## Step 1b: If you wish to uninstall node modules run:
rm package-lock.json
rm -rf node_modules

## Step 2: A virtual Python environment may be necessary; run the following command:
python3 -m venv ~/venv
source ~/venv/bin/activate

## Step 3: To fully automate the remaining installation, run the following script:
cd scripts
python3 install_all.py

## Step 3b: If you wish to uninstall everything and leave only the base files, run the following command:
python3 uninstall_all.py

## Step 4: To manually update the epg.xml file, run the following command:
python3 merge_epg.py

## Step 5: To access the epg.xml file in a web browser, paste the following URL:
http:/localhost:8080/epg.xml

## Step 6: To modify the scheduling for the merge_epg.py in crontab (macOS), enter the following command in Terminal:
crontab -e
