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

# List of Google Drive API scope strings
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Path to the user's desktop
desktop_path = os.path.join(os.environ['userprofile'], 'Desktop')

# Credentials object to authenticate with the Google Drive API
creds = None

# Check if "token.json" exists
if os.path.exists("token.json"):
    # Read the contents of "token.json"
    with open("token.json", "r") as token:
        info = json.loads(token.read())
        creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
            info=info, scopes=SCOPES)
else:
    # Create a flow object to request user authorization
    flow = google.auth.flow.InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    # Write the authorization information to "token.json"
    with open("token.json", "w") as token:
        token.write(json.dumps(creds.to_json()))

# Create a Drive API service object
service = build("drive", "v3", credentials=creds)

# Query for the "Desktop Backup" folder
response = service.files().list(
    q="name='Desktop Backup' and mimeType='application/vnd.google-apps.folder'", spaces="drive").execute()

# Check if the "Desktop Backup" folder exists
if not response["files"]:
    # Create the "Desktop Backup" folder
    file_metadata = {
        "name": "Desktop Backup",
        "mimeType": "application/vnd.google-apps.folder"
    }
    file = service.files().create(body=file_metadata, fields="id").execute()
    folder_id = file.get("id")
else:
    # Get the ID of the "Desktop Backup" folder
    folder_id = response["files"][0]["id"]

# Iterate over all files and directories in the user's desktop
for root, dirs, files in os.walk(desktop_path):
    # Get the current time
    now = datetime.now()
    date_time = now.strftime("%d-%m-%Y %H:%M:%S")

    # Create a subfolder with the current date and time
    file_metadata = {
        "name": date_time,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [folder_id]
    }
    file = service.files().create(body=file_metadata, fields="id").execute()
    subfolder_id = file.get("id")

    # Iterate over all files in the current directory
    for file in files:
        # Skip certain file types
        if file.endswith((".ini", ".lnk")):
            continue

        # Create a file metadata object
        file_metadata = {
            "name": file,
            "parents": [subfolder_id]
        }

        # Create a MediaFileUpload object for the file
        media = MediaFileUpload(os.path.join(root, file))

        # Use the Drive API to upload the file
        try:
            upload_file = service.files().create(body=file_metadata,
                                                 media_body=media,
                                                 fields="id").execute()
            print(f"Backed up file: {file}")
        except HttpError as e:
            print(f"Error: {e}")
