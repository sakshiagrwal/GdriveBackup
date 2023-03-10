"""
Google Drive Backup
"""

import os
import shutil
import logging
from datetime import datetime
import colorlog
import google.auth.exceptions
import googleapiclient.errors
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


BACKUP_DIR = os.path.join(os.path.expandvars("%userprofile%"), "Desktop", "backup")
ARCHIVE_DIR = os.path.join(os.getcwd(), "backup_archive")
CREDENTIALS_FILE = "credentials.json"
FOLDER_NAME = "Vivobook"

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_zip(source_dir, dest_dir, file_name):
    """
    Creates a zip file containing the contents of the specified source directory.

    Args:
        source_dir (str): The path to the directory to zip.
        dest_dir (str): The path to the directory where the zip file will be saved.
        file_name (str): The name to give the zip file.

    Returns:
        None
    """
    logger.info(
        "Creating ZIP file from %s to %s with name %s", source_dir, dest_dir, file_name
    )
    if not os.path.exists(source_dir):
        logger.error("Failed to create ZIP file: %s not found", source_dir)
        return None
    try:
        os.makedirs(dest_dir, exist_ok=True)
        file_name_without_ext = os.path.splitext(file_name)[0]
        archive_path = os.path.join(dest_dir, file_name_without_ext)
        shutil.make_archive(archive_path, "zip", source_dir)
        zip_file_path = archive_path + ".zip"
        logger.info("Created ZIP file: %s", zip_file_path)
        return zip_file_path
    except FileNotFoundError:
        logger.error("Failed to create ZIP file: %s not found", source_dir)
        return None


def authenticate_drive():
    """Authenticate the Google Drive API client with OAuth2 credentials.

    Returns:
        An authenticated Google Drive API client.
    """
    logger.info("Authenticating Google Drive API...")
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    logger.info("Authenticated Google Drive API")
    return gauth


def upload_file(gauth, file_path, file_name):
    """
    Uploads a file to Google Drive.

    Args:
        gauth (GoogleAuth): An authorized GoogleAuth instance.
        file_path (str): The local path to the file to upload.
        file_name (str): The name to use for the uploaded file.

    Returns:
        None
    """
    logger.info("Uploading file %s to Google Drive...", file_name)
    drive = GoogleDrive(gauth)
    query = f"title='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folder_list = drive.ListFile({"q": query}).GetList()
    if folder_list:
        folder_id = folder_list[0]["id"]
    else:
        folder_metadata = {
            "title": FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder["id"]
        logger.info("Created folder: %s", FOLDER_NAME)

    file_metadata = {
        "title": file_name,
        "parents": [{"kind": "drive#fileLink", "id": folder_id}],
    }
    media = drive.CreateFile(file_metadata)
    media.SetContentFile(file_path)
    media.Upload()
    logger.info("Uploaded %s to Google Drive folder: %s", file_name, FOLDER_NAME)


def backup_and_upload():
    """
    Backup the specified file and upload it to Google Drive.
    """
    now = datetime.now()
    file_name = f"backup_{now.strftime('%d-%m-%Y_%H-%M-%S')}.zip"
    archive_path = create_zip(BACKUP_DIR, ARCHIVE_DIR, file_name)
    if not archive_path:
        return

    try:
        gauth = authenticate_drive()
        upload_file(gauth, archive_path, file_name)
    except google.auth.exceptions.DefaultCredentialsError as error:
        logging.error("Failed to authenticate with Google Drive: %s", str(error))
        return
    except googleapiclient.errors.HttpError as error:
        logging.error("Failed to upload %s to Google Drive: %s", file_name, str(error))
        return
    finally:
        # shutil.rmtree(ARCHIVE_DIR)
        logging.info("Backup and upload successful!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    backup_and_upload()
