import json
import os
import os.path
import google.auth

from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_folder(service, local_path, parent_id):
    # List the contents of the local directory
    contents = os.listdir(local_path)

    # Iterate through the contents of the local directory
    for item in contents:
        # Construct the local and Google Drive paths
        local_item_path = os.path.join(local_path, item)
        drive_item_path = os.path.join('/', item)

        # Check if the item is a file or a directory
        if os.path.isfile(local_item_path):
            # Upload the file to Google Drive
            file_metadata = {
                "name": item,
                "parents": [parent_id]
            }
            media = MediaFileUpload(local_item_path)
            service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"Backed up: {drive_item_path}")
        elif os.path.isdir(local_item_path):
            # Create a new folder on Google Drive
            file_metadata = {
                "name": item,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id]
            }
            folder = service.files().create(body=file_metadata, fields="id").execute()
            folder_id = folder.get("id")
            print(f"Created folder: {drive_item_path}")
            # Recursively upload the contents of the directory
            upload_folder(service, local_item_path, folder_id)


# Read the credentials from the JSON file
with open("token.json", "r") as cred_file:
    info = json.loads(cred_file.read())
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
        info=info)

# Authenticate with the Google Drive API
service = build("drive", "v3", credentials=creds)

# Search for the "Desktop Backup" folder
response = service.files().list(
    q="name='Desktop Backup' and mimeType='application/vnd.google-apps.folder'", spaces="drive").execute()

# If the folder doesn't exist, create it
if not response["files"]:
    file_metadata = {
        "name": "Desktop Backup",
        "mimeType": "application/vnd.google-apps.folder"
    }
    file = service.files().create(body=file_metadata, fields="id").execute()
    root_folder_id = file.get("id")
else:
    root_folder_id = response["files"][0]["id"]

# Set the local path to the user's desktop
local_path = os.path.join(os.environ['userprofile'], 'Desktop')

# Upload the contents of the local directory to Google Drive
upload_folder(service, local_path, root_folder_id)
