import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = None

try:
    with open("token.json", "r") as token:
        creds = Credentials.from_authorized_user_info(
            info=token.read(), scopes=SCOPES)
except FileNotFoundError:
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

try:
    service = build("drive", "v3", credentials=creds)
    response = service.files().list(
        q="name='MasterBackup' and mimeType='application/vnd.google-apps.folder'", spaces="drive").execute()
    if not response["files"]:
        file_metadata = {
            "name": "MasterBackup",
            "mimeType": "application/vnd.google-apps.folder"
        }

        file = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = file.get("id")
    else:
        folder_id = response["files"][0]["id"]
        for file in os.listdir(os.path.join("backupfiles")):
            file_metadata = {
                "name": file,
                "parents": [folder_id]
            }
            media = MediaFileUpload(f"{os.path.join('backupfiles', file)}")
            upload_file = service.files().create(body=file_metadata,
                                                 media_body=media,
                                                 fields="id").execute()
            print(f"Backed up file: {file}")
except HttpError as e:
    print(f"Error: {e}")
finally:
    with open("token.json", "r") as token:
        token.close()
