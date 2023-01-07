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

# Create a folder for all of the files on the desktop
now = datetime.now()
date_time = now.strftime("%d %b %Y %I:%M%p")
file_metadata = {
    "name": date_time,
    "mimeType": "application/vnd.google-apps.folder",
    "parents": [folder_id]
}
file = service.files().create(body=file_metadata, fields="id").execute()
subfolder_id = file.get("id")
print(f"Created folder: {date_time}")


def create_subfolders(path, parent_id):
    print(f"Creating subfolders for path: {path}, parent_id: {parent_id}")
    # Split the path into a list of subfolders
    subfolders = path.split(os.sep)
    # Iterate through the subfolders and create them if necessary
    for subfolder in subfolders:
        if not subfolder:
            continue
        # Search for the subfolder in the parent folder
        query = f"mimeType='application/vnd.google-apps.folder' and trashed = false and name='{subfolder}' and parents in '{parent_id}'"
        response = service.files().list(q=query, spaces='drive').execute()
        # If the subfolder doesn't exist, create it
        if not response['files']:
            file_metadata = {
                "name": subfolder,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id]
            }
            file = service.files().create(body=file_metadata, fields="id").execute()
            subfolder_id = file.get("id")
            print(f"Created folder: {subfolder}")
        else:
            subfolder_id = response['files'][0]['id']
    return subfolder_id


# Iterate through the files and subdirectories on the user's desktop
for root, dirs, files in os.walk(os.path.join(os.environ['userprofile'], 'Desktop')):
    # Get the relative path of the current subdirectory
    rel_path = os.path.relpath(root, os.path.join(
        os.environ['userprofile'], 'Desktop'))
    # Create the necessary subfolders in Google Drive
    folder_id = create_subfolders(rel_path, subfolder_id)
    print(f"folder_id for path {rel_path}: {folder_id}")
    # Iterate through the files in the subdirectory
    for file in files:
        if file.endswith((".ini", ".lnk")):
            continue
        file_path = os.path.join(root, file)
        if os.path.getsize(file_path) > 5000000:
            continue
        file_metadata = {
            "name": file,
            "parents": [folder_id]
        }
        media = MediaFileUpload(file_path)
        upload_file = service.files().create(body=file_metadata,
                                             media_body=media,
                                             fields="id").execute()
        print(f"Backed up: {file}")
