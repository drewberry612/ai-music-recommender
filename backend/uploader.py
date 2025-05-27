import os
import asyncio
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import settings

SCOPES = ['https://www.googleapis.com/auth/drive.file']
LOG_DIR = settings.LOG_DIR

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        settings.CREDENTIALS_PATH,
        scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

def find_file_id(service, filename):
    """Check if file already exists in the folder; return file ID or None."""
    query = f"name='{filename}' and '{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    return None

async def upload_logs_to_drive():
    service = get_drive_service()

    while True:
        for file_path in Path(LOG_DIR).glob("*.log"):
            file_id = find_file_id(service, file_path.name)
            media = MediaFileUpload(str(file_path), mimetype='text/plain', resumable=True)

            metadata = {
                'name': file_path.name,
                'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
            }

            if file_id:
                # Update existing file
                service.files().update(
                    fileId=file_id,
                    media_body=media,
                    body=metadata
                ).execute()
            else:
                # Create new file
                service.files().create(
                    body=metadata,
                    media_body=media,
                    fields='id'
                ).execute()

        await asyncio.sleep(settings.LOG_UPLOAD_INTERVAL_MINS * 60)
