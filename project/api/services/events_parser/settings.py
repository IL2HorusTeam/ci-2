# -*- coding: utf-8 -*-

import os

from project.app import app


env = os.getenv


GITHUB_REPO_NAME = env(
    'EVENTS_PARSER_GITHUB_REPO_NAME',
    'il2fb-events-parser')
GITHUB_REPO_OWNER = (
    env('EVENTS_PARSER_GITHUB_REPO_OWNER')
    or app.config.get('DEFAULT_GITHUB_REPO_OWNER', 'IL2HorusTeam'))

_github_report_issues = env('EVENTS_PARSER_GITHUB_REPORT_ISSUES')
GITHUB_REPORT_ISSUES = (
    int(_github_report_issues) == 1
    if _github_report_issues is not None else
    app.config.get('DEFAULT_GITHUB_REPORT_ISSUES', False))

GITHUB_ACCESS_TOKEN = env('EVENTS_PARSER_GITHUB_ACCESS_TOKEN')
