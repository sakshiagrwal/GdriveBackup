import os
import shutil
import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Set the path to your Windows desktop folder named "Deepak"
DESKTOP_PATH = os.path.join(os.environ["USERPROFILE"], "Desktop", "Deepak")

# Set the ID of the folder in your Google Drive where you want to upload the files
DRIVE_FOLDER_ID = "INSERT_YOUR_FOLDER_ID_HERE"

# Set the name of the folder in your Google Drive where you want to upload the files
DRIVE_FOLDER_NAME = "Deepak Backup"

# Set the credentials file path
CREDENTIALS_FILE = "credentials.json"

# Set the scopes needed for the Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Authenticate with the Google Drive API using the credentials file
creds = None
if os.path.exists(CREDENTIALS_FILE):
    creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = google.auth.default(scopes=SCOPES)
        creds = flow.run_local_server(port=0)
    with open(CREDENTIALS_FILE, "w") as credentials_file:
        credentials_file.write(creds.to_json())

# Create a Google Drive API client
service = build("drive", "v3", credentials=creds)

# Create the folder in Google Drive if it doesn't exist
try:
    folder_metadata = {"name": DRIVE_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"}
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    DRIVE_FOLDER_ID = folder.get("id")
except HttpError as error:
    print(f"An error occurred: {error}")
    DRIVE_FOLDER_ID = None

# Upload the files to Google Drive
for root, dirs, files in os.walk(DESKTOP_PATH):
    for file in files:
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, DESKTOP_PATH)
        drive_path = os.path.join(DRIVE_FOLDER_ID, relative_path)
        file_metadata = {"name": file, "parents": [DRIVE_FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"Uploaded {file_path} to {drive_path}")
        except HttpError as error:
            print(f"An error occurred: {error}")
