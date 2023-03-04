# Google Drive Backup

![Made with Python](https://img.shields.io/badge/MadeWith-Python-green)

This is a Python script for backing up a directory and uploading it to Google Drive using the Google Drive API.

## Configuration

1. Install the required Python packages:

- ```bash
  pip install -r requirements.txt
  ```

2. Follow [Step 1 of this guide](https://developers.google.com/drive/api/v3/quickstart/python) to create a client secret for the Google Drive API. Save the secret file as `client_secrets.json` and place it in the project folder.

3. Edit the `backup.py` file to configure the backup settings:

- Change the `BACKUP_DIR` variable to the absolute path of the directory you want to back up.
- Change the `ARCHIVE_DIR` variable to the absolute path of the directory where you want to save the ZIP file.
- Change the `FOLDER_NAME` variable to the Google Drive folder where you want to upload the backup.

4. Execute the `backup.py` script:

- ```bash
  python backup.py
  ```

## Info

- The backup ZIP file is uploaded to the Google Drive folder specified by `FOLDER_NAME`.
- The local backup is stored in the `backup_archive` folder.
- By default, the `backup` folder is set as the backup directory.
- [Learn about the entire process from start to end in this blog](https://python.plainenglish.io/automate-google-drive-backup-using-python-105f57e2151)
