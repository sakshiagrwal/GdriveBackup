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

# Scopes required for the Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Initialize the API client with the user's credentials
creds = None

# Try to load the user's credentials from a JSON file
try:
    with open("token.json", "r") as token:
        # Load the credentials from the JSON file
        info = json.loads(token.read())
        creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
            info=info, scopes=SCOPES)

# If the JSON file doesn't exist, use OAuth2 flow to get the credentials
except FileNotFoundError:
    flow = google.auth.flow.InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials to a JSON file
    with open("token.json", "w") as token:
        token.write(json.dumps(creds.to_json()))

# Try to access the Google Drive API with the user's credentials
try:
    # Initialize the Google Drive API client
    service = build("drive", "v3", credentials=creds)

    # Check if the "Desktop Backup" folder already exists in Google Drive
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
    # If the folder exists, get its ID
    else:
        folder_id = response["files"][0]["id"]

    # Walk through the local "Desktop" directory and backup the files to Google Drive
    try:
        # Walk through the directory tree
        for root, dirs, files in os.walk("C:\\Users\\Sakshi\\Desktop"):
            # Get the current date and time
            now = datetime.now()
            date_time = now.strftime("%d-%m-%Y %H:%M:%S")

            # Create a subfolder in the "Desktop Backup" folder with the current date and time as the name
            file_metadata = {
                "name": date_time,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [folder_id]
            }
            file = service.files().create(body=file_metadata, fields="id").execute()
            subfolder_id = file.get("id")

            # Iterate through the files in the current directory
            for file in files:
                # Skip files with a .ini or .lnk extension
                if file.endswith((".ini", ".lnk")):
                    continue
                # Create a file metadata object to upload the file to the subfolder
                file_metadata = {
                    "name": file,
                    "parents": [subfolder_id]
                }
                # Use the MediaFileUpload object to upload the file
                media = MediaFileUpload(os.path.join(root, file))
                upload_file = service.files().create(body=file_metadata,
                                                     media_body=media,
                                                     fields="id").execute()
                # Print a message to indicate that the file was backed up
                print(f"Backed up file: {file}")
        # If the user's "Desktop" directory doesn't exist, print an error message
    except FileNotFoundError:
        print("The specified user was not found on the system.")
# If there is an error accessing the Google Drive API, print an error message
except HttpError as e:
    print(f"Error: {e}")
# Close the "token.json" file
finally:
    with open("token.json", "r") as token:
        token.close()
