import json
import os
import os.path

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

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

try:
    service = build("drive", "v3", credentials=creds)
    response = service.files().list(
        q="name='Desktop Backup' and mimeType='application/vnd.google-apps.folder'", spaces="drive").execute()
    if not response["files"]:
        file_metadata = {
            "name": "Desktop Backup",
            "mimeType": "application/vnd.google-apps.folder"
        }

        file = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = file.get("id")
    else:
        folder_id = response["files"][0]["id"]

    for root, dirs, files in os.walk("C:\\Users\\Sakshi\\Desktop"):
        for file in files:
            file_metadata = {
                "name": file,
                "parents": [folder_id]
            }
            media = MediaFileUpload(os.path.join(root, file))
            upload_file = service.files().create(body=file_metadata,
                                                 media_body=media,
                                                 fields="id").execute()
            print(f"Backed up file: {file}")
except HttpError as e:
    print(f"Error: {e}")
finally:
    with open("token.json", "r") as token:
        token.close()
