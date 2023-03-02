import os
import json
import shutil
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load the contents of the credentials.json file into a dictionary
with open('credentials.json', 'r', encoding='utf-8') as f:
    cred_info = json.load(f)

# Check if the necessary fields are present in the cred_info dictionary
if not all(field in cred_info for field in ['installed']):
    raise ValueError('The credentials file is missing one or more required fields.')

# Set up the OAuth2 client
flow = InstalledAppFlow.from_client_config(cred_info['installed'], ['https://www.googleapis.com/auth/drive'])
creds = flow.run_local_server(port=0)
service = build('drive', 'v3', credentials=creds)

# Set the source directory (the directory to be backed up)
source_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'Raga')

# Set the destination directory (the directory on Google Drive to upload the backup to)
destination_dir_name = 'Raga Backup'
try:
    # Check if the destination directory already exists
    query = f"name='{destination_dir_name}' and mimeType='application/vnd.google-apps.folder'"
    response = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id)').execute()
    destination_dir_id = response.get('files', [])[0].get('id')
except IndexError:
    # If the destination directory doesn't exist, create it
    file_metadata = {
        'name': destination_dir_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    destination_dir_id = file.get('id')

# Copy the source directory to the destination directory
destination_dir_path = f"drive:{destination_dir_name}"
shutil.copytree(source_dir, destination_dir_path)

print('Backup completed successfully.')
