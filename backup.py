import json
import os
import os.path
from datetime import datetime

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Read the token from "token.json"
with open("token.json", "r") as token:
    info = json.loads(token.read())
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
        info=info, scopes=SCOPES)

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
    folder_id = file.get("id")
else:
    folder_id = response["files"][0]["id"]

# Iterate through the files and subdirectories on the user's desktop
for root, dirs, files in os.walk(os.path.join(os.environ['userprofile'], 'Desktop')):
    now = datetime.now()
    date_time = now.strftime("%d-%m-%Y %H:%M:%S")
    file_metadata = {
        "name": date_time,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [folder_id]
    }
    file = service.files().create(body=file_metadata, fields="id").execute()
    subfolder_id = file.get("id")

    # Iterate through the files in the subdirectory
    for file in files:
        if file.endswith((".ini", ".lnk")):
            continue

        file_metadata = {
            "name": file,
            "parents": [subfolder_id]
        }
        media = MediaFileUpload(os.path.join(root, file))
        upload_file = service.files().create(body=file_metadata,
                                             media_body=media,
                                             fields="id").execute()
        print(f"Backed up: {file}")
