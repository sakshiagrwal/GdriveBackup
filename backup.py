import json
import os
import os.path
import glob
import logging
from datetime import datetime

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def create_folder(service, folder_name):
    """
    Creates a folder with the given name in Google Drive.
    Returns the folder's ID.
    """
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    file = service.files().create(body=file_metadata, fields="id").execute()
    folder_id = file.get("id")
    return folder_id


def get_folder(service, folder_name):
    """
    Returns the ID of the folder with the given name if it exists in Google Drive,
    otherwise creates the folder and returns the ID.
    """
    response = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        spaces="drive"
    ).execute()
    if not response["files"]:
        folder_id = create_folder(service, folder_name)
    else:
        folder_id = response["files"][0]["id"]
    return folder_id


def create_subfolder(service, parent_folder_id, subfolder_name):
    """
    Creates a subfolder with the given name within the given parent folder in Google Drive.
    Returns the subfolder's ID.
    """
    file_metadata = {
        "name": subfolder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id]
    }
    file = service.files().create(body=file_metadata, fields="id").execute()
    subfolder_id = file.get("id")
    return subfolder_id


def upload_file(service, file_path, file_name, parent_folder_id):
    """
    Uploads the file at the given file path to the given parent folder in Google Drive.
    """
    file_metadata = {
        "name": file_name,
        "parents": [parent_folder_id]
    }
    media = MediaFileUpload(file_path)
    upload_file = service.files().create(body=file_metadata,
                                         media_body=media,
                                         fields="id").execute()
    logging.info(f"Backed up file: {file_name}")


def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Check for authorization file
    creds = None
    try:
        with open("token.json", "r") as token:
            info = json.loads(token.read())
            creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
                info=info, scopes=SCOPES)
    except FileNotFoundError:
        flow = google.auth.flow.InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(json.dumps(creds.to_json()))

    # Create the Drive API service
    service = build("drive", "v3", credentials=creds)

    # Get or create the "Desktop Backup" folder
    folder_id = get_folder(service, "Desktop Backup")

    # Create a subfolder with the current date and time
    now = datetime.now()
    date_time = now.strftime("%d-%m-%Y %H:%M:%S")
    subfolder_id = create_subfolder(service, folder_id, date_time)

    # Upload the files from the user's desktop to the subfolder
    desktop_path = "C:\\Users\\Sakshi\\Desktop"
    for file_path in glob.glob(os.path.join(desktop_path, "*")):
        if file_path.endswith((".ini", ".lnk")):
            continue
        file_name = os.path.basename(file_path)
        upload_file(service, file_path, file_name, subfolder_id)


if __name__ == "__main__":
    main()
