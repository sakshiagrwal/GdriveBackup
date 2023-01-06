import json
import os
import os.path
import google.auth

from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Read the token from "token.json"
with open("token.json", "r") as token:
    info = json.loads(token.read())
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
        info=info, scopes=SCOPES)

# Authenticate with the Google Drive API
service = build("drive", "v3", credentials=creds)

# Create a folder for all of the files
now = datetime.now()
date_time = now.strftime("%d %b %Y %I:%M%p")
folder_metadata = {
    "name": date_time,
    "mimeType": "application/vnd.google-apps.folder"
}
folder = service.files().create(body=folder_metadata, fields="id").execute()
folder_id = folder.get("id")
print(f"Created folder: {date_time}")


def upload_to_folder(service, dir_path, parent_id):
    # Iterate through the files and subdirectories in the current directory
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            # Upload the file
            file_metadata = {
                "name": item,
                "parents": [parent_id]
            }
            media = MediaFileUpload(item_path)
            upload_file = service.files().create(body=file_metadata,
                                                 media_body=media,
                                                 fields="id").execute()
            print(f"Uploaded file: {item}")
        else:
            # Create a subfolder for the subdirectory
            subfolder_metadata = {
                "name": item,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id]
            }
            subfolder = service.files().create(body=subfolder_metadata, fields="id").execute()
            subfolder_id = subfolder.get("id")
            print(f"Created folder: {item}")

            # Recursively upload the files in the subdirectory
            upload_to_folder(service, item_path, subfolder_id)


# Recursively upload the files to the folder
upload_to_folder(service, ".", folder_id)
