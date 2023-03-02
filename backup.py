import os
import shutil
import logging
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


BACKUP_DIR = os.path.join(os.path.expandvars("%userprofile%"), "Desktop", "backup")
ARCHIVE_DIR = os.path.join(os.path.expandvars("%userprofile%"), "Desktop", "backup_archive")
CREDENTIALS_FILE = "credentials.json"


def create_zip(source_dir, dest_dir, file_name):
    try:
        os.makedirs(dest_dir, exist_ok=True)
        file_name_without_ext = os.path.splitext(file_name)[0]
        archive_path = os.path.join(dest_dir, file_name_without_ext)
        shutil.make_archive(archive_path, "zip", source_dir)
        return archive_path + ".zip"
    except FileNotFoundError:
        logging.error(f"Failed to create ZIP file: {source_dir} not found")
        return None


def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    return gauth


def upload_file(gauth, file_path, file_name):
    drive = GoogleDrive(gauth)
    folder_name = "Vivobook"
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folder_list = drive.ListFile({'q': query}).GetList()
    if folder_list:
        folder_id = folder_list[0]['id']
    else:
        folder_metadata = {"title": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']
        logging.info(f"Created folder: {folder_name}")

    file_metadata = {"title": file_name, "parents": [{"kind": "drive#fileLink", "id": folder_id}]}
    media = drive.CreateFile(file_metadata)
    media.SetContentFile(file_path)
    media.Upload()
    logging.info(f"Uploaded {file_name} to Google Drive folder: {folder_name}")


def backup_and_upload():
    now = datetime.now()
    file_name = f"backup_{now.strftime('%d-%m-%Y_%H-%M-%S')}.zip"
    archive_path = create_zip(BACKUP_DIR, ARCHIVE_DIR, file_name)
    if not archive_path:
        return

    gauth = authenticate_drive()
    upload_file(gauth, archive_path, file_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    backup_and_upload()
