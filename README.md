# Google Drive Backup

A simple script to backup files from a local directory to Google Drive

## Installation

- Install Python 3.x from https://www.python.org/downloads/
- Install the required libraries using pip:
  - google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
- Follow the instructions at https://developers.google.com/drive/api/v3/quickstart/python to enable the Google Drive API and download the "credentials.json" file
- Place the "credentials.json" file in the same directory as the script

## Usage

- Run the script and follow the prompts to authorize the script to access your Google Drive
- The script will create a "Desktop Backup" folder on Google Drive, if it doesn't already exist, and then iterate through all the files in the "C:\Users\Sakshi\Desktop" directory and its subdirectories, and upload each file to the "Desktop Backup" folder
- The script will store the user's credentials in the "token.json" file, so the user does not have to authorize the script every time it is run


- **Here are the steps to create the credentials:**

1. Go to the Google Cloud Console at https://console.cloud.google.com/.
2. Click the project dropdown and select or create the project you want to use for this script.
3. Click on the "APIs & Services" tab on the left sidebar and select "Credentials".
4. Click the "+ CREATE CREDENTIALS" button and select "OAuth client ID".
5. Select "Desktop app" as the application type.
6. Give your credentials a name and click "Create".
7. Click "Download" to download your credentials as a JSON file.
8. Save the downloaded file as credentials.json in the same directory as your Python script.

## Contributing

- Fork the repository
- Create a new branch for your changes
- Make your changes and commit them
- Create a pull request to merge your changes into the master branch

## Issues

- If you encounter any issues or have any suggestions for improvement, please open a new issue on the repository

