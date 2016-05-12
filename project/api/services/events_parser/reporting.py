# coding: utf-8

from project.bug_reporter import BugReporter

from . import settings


reporter = BugReporter(
    settings.GITHUB_ACCESS_TOKEN,
    settings.GITHUB_REPO_OWNER,
    settings.GITHUB_REPO_NAME
) if settings.GITHUB_REPORT_ISSUES else None
