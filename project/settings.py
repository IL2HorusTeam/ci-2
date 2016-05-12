# coding: utf-8

import os

env = os.getenv

#------------------------------------------------------------------------------
# Flask
#------------------------------------------------------------------------------

DEBUG = int(env('FLASK_DEBUG', 0)) == 1
SECRET_KEY = env('FLASK_SECRET_KEY', '^vl#9lg@xm1@+6s*fb!lym0l#n#v5&6xp')

#------------------------------------------------------------------------------
# Github
#------------------------------------------------------------------------------

DEFAULT_GITHUB_REPO_OWNER = 'IL2HorusTeam'
DEFAULT_GITHUB_REPORT_ISSUES = int(env('DEFAULT_GITHUB_REPORT_ISSUES', 0)) == 1
