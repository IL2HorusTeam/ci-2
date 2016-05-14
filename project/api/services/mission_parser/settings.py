# coding: utf-8

import os

from project.app import app


env = os.getenv


ALLOWED_EXTENSIONS = ['mis', ]
ALLOWED_MIME_TYPES = ['application/octet-stream', ]


# -----------------------------------------------------------------------------
# Github
# -----------------------------------------------------------------------------

_github_report_issues = env('MISSION_PARSER_GITHUB_REPORT_ISSUES')
GITHUB_REPORT_ISSUES = (
    int(_github_report_issues) == 1
    if _github_report_issues is not None else
    app.config['DEFAULT_GITHUB_REPORT_ISSUES'])

GITHUB_REPO_OWNER = env(
    'MISSION_PARSER_GITHUB_REPO_OWNER',
    app.config['DEFAULT_GITHUB_REPO_OWNER'])

GITHUB_ACCESS_TOKEN = env(
    'MISSION_PARSER_GITHUB_ACCESS_TOKEN',
    app.config['DEFAULT_GITHUB_ACCESS_TOKEN'])

GITHUB_REPO_NAME = env(
    'MISSION_PARSER_GITHUB_REPO_NAME',
    'il2fb-mission-parser')


# -----------------------------------------------------------------------------
# Google Drive
# -----------------------------------------------------------------------------

GOOGLE_DRIVE_FOLDER_ID = env('MISSION_PARSER_GOOGLE_DRIVE_FOLDER_ID')
