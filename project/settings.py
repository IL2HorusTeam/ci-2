# coding: utf-8

import os
import tempfile


env = os.getenv


# -----------------------------------------------------------------------------
# Flask
# -----------------------------------------------------------------------------

DEBUG = int(env('FLASK_DEBUG', 0)) == 1
SECRET_KEY = env('FLASK_SECRET_KEY', '^vl#9lg@xm1@+6s*fb!lym0l#n#v5&6xp')

MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MiB for uploads
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


# -----------------------------------------------------------------------------
# Github
# -----------------------------------------------------------------------------

DEFAULT_GITHUB_REPO_OWNER = env('DEFAULT_GITHUB_REPO_OWNER', 'IL2HorusTeam')
DEFAULT_GITHUB_REPORT_ISSUES = int(env('DEFAULT_GITHUB_REPORT_ISSUES', 0)) == 1
DEFAULT_GITHUB_ACCESS_TOKEN = env('DEFAULT_GITHUB_ACCESS_TOKEN', None)


# -----------------------------------------------------------------------------
# Google Drive
# -----------------------------------------------------------------------------

GOOGLE_SERVICE_EMAIL = env('GOOGLE_SERVICE_EMAIL')
GOOGLE_SERVICE_PRIVATE_KEY = env('GOOGLE_SERVICE_PRIVATE_KEY')
GOOGLE_SERVICE_CREDENTIALS_STORAGE = os.path.join(
    tempfile.gettempdir(),
    'google-service-credentials.json')

GOOGLE_DRIVE_API_NAME = 'drive'
GOOGLE_DRIVE_API_VERSION = 'v2'
GOOGLE_DRIVE_API_SCOPE = 'https://www.googleapis.com/auth/drive.file'
