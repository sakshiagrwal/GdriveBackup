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
        archive_path = os.path.join(dest_dir, file_name)
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
    drive = GoogleDrive(gauth)
    return drive


def upload_file(drive, file_path, file_name):
    file_metadata = {"title": file_name}
    media = GoogleDrive.CreateFile(file_metadata)
    media.SetContentFile(file_path)
    media.Upload()
    logging.info(f"Uploaded {file_name} to Google Drive")


def backup_and_upload():
    now = datetime.now()
    file_name = f"backup_{now.strftime('%d-%m-%Y_%H-%M-%S')}.zip"
    archive_path = create_zip(BACKUP_DIR, ARCHIVE_DIR, file_name)
    if not archive_path:
        return

    drive = authenticate_drive()
    upload_file(drive, archive_path, file_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    backup_and_upload()
