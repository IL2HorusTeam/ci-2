# coding: utf-8

import httplib2
import os

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.file import Storage

from project.app import app


def get_google_drive_service():
    storage = Storage(app.config['GOOGLE_SERVICE_CREDENTIALS_STORAGE'])
    credentials = storage.get()
    http = httplib2.Http()

    if credentials is None or credentials.invalid:
        email = app.config['GOOGLE_SERVICE_EMAIL']
        key = app.config['GOOGLE_SERVICE_PRIVATE_KEY']
        scope = app.config['GOOGLE_DRIVE_API_SCOPE']
        credentials = SignedJwtAssertionCredentials(email, key, scope=scope)
        storage.put(credentials)
    else:
        credentials.refresh(http)

    name = app.config['GOOGLE_DRIVE_API_NAME']
    version = app.config['GOOGLE_DRIVE_API_VERSION']
    http = credentials.authorize(http)

    return build(serviceName=name, version=version, http=http)


def upload_file_to_google_drive(file_path, folder_id, mime_type='text/plain'):
    media_body = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    body = {
        'title': os.path.basename(file_path),
        'mimeType': mime_type,
        'parents': [{'id': folder_id}, ]
    }
    service = get_google_drive_service()
    request = service.files().insert(body=body, media_body=media_body)
    return request.execute()
