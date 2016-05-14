# coding: utf-8

import os

from project.app import app


env = os.getenv


# -----------------------------------------------------------------------------
# Github
# -----------------------------------------------------------------------------

GITHUB_REPO_OWNER = env(
    'EVENTS_PARSER_GITHUB_REPO_OWNER',
    app.config['DEFAULT_GITHUB_REPO_OWNER'])

GITHUB_ACCESS_TOKEN = env(
    'EVENTS_PARSER_GITHUB_ACCESS_TOKEN',
    app.config['DEFAULT_GITHUB_ACCESS_TOKEN'])

GITHUB_REPO_NAME = env(
    'EVENTS_PARSER_GITHUB_REPO_NAME',
    'il2fb-events-parser')
