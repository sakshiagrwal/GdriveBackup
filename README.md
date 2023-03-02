# Google Drive Backup

![](https://img.shields.io/badge/MadeWith-Python-green)

A simple script to backup folder from a local directory to Google Drive.

### [Learn about the entire process from start to end in this blog](https://python.plainenglish.io/automate-google-drive-backup-using-python-105f57e2151)

## Set up:

1. `pip install -r requirements.txt`
2. This project uses Google drive API which requires a client secret, [follow step-1 only from this procedure](https://developers.google.com/drive/api/v3/quickstart/python). Save the secret file as `client_secrets.json` and place in project folder.
3. Execute `python backup.py`

## Info:

1. Zip file is uploaded to `My Drive`.
2. Local backup is srored in `archive` folder.
3. By default `backup_me` is set as backup folder
