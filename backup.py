import os
import shutil
from datetime import datetime

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


def create_zip(path, file_name):
    desktop_path = os.path.join(os.path.expandvars('%userprofile%'), 'Desktop')
    backup_dir = os.path.join(desktop_path, 'backup_archive')
    os.makedirs(backup_dir, exist_ok=True)
    try:
        shutil.make_archive(os.path.join(backup_dir, file_name), "zip", path)
        return True
    except FileNotFoundError as e:
        return False


def google_auth():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return gauth, drive


def upload_backup(drive, path, file_name):
    f = drive.CreateFile({"title": file_name})
    f.SetContentFile(os.path.join(path, file_name))
    f.Upload()
    f = None


def controller():
    path = os.path.join(os.path.expandvars('%userprofile%'), 'Desktop', 'backup')
    now = datetime.now()
    file_name = "backup " + now.strftime(r"%d-%m-%Y %H:%M:%S").replace(":", "-").replace(" ", "_")

    if not create_zip(path, file_name):
        print("Failed to create ZIP file")
        return

    auth, drive = google_auth()
    upload_backup(drive, os.path.join(os.environ['USERPROFILE'], 'Desktop', 'backup_archive'), file_name + ".zip")
    print("Backup uploaded successfully")


if __name__ == "__main__":
    controller()
