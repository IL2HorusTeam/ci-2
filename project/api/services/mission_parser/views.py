# coding: utf-8

import traceback

from flask import request
from flask.views import MethodView
from werkzeug import secure_filename

from il2fb.parsers.mission import MissionParser
from il2fb.parsers.mission.exceptions import MissionParsingError

from project.app import app
from project.api.blueprints import RESTBlueprint
from project.api.response.rest import (
    RESTSuccess, RESTBadRequest, RESTInternalServerError,
)
from project.utils.google import upload_file_to_google_drive
from project.utils.format import format_remote_file_link

from .reporting import reporter
from . import settings


rest = RESTBlueprint(r'mission-parser', __name__)


class MissionParseView(MethodView):

    def post(self):
        f = request.files['file']

        try:
            self._upload_file(f)
        except ValueError as e:
            return RESTBadRequest(detail=unicode(e))

        try:
            data = self._parse_mission()
        except MissionParsingError as e:
            return RESTInternalServerError(
                payload=self._on_parsing_error(e),
                detail="Failed to parse mission '{}'.".format(f.filename))
        finally:
            self._remove_file()

        if data:
            return RESTSuccess({
                'file_name': f.filename,
                'data': data,
            })
        else:
            return RESTBadRequest(
                detail="Oops! Your mission is blank or does not contain "
                       "any known sections.")

    def _upload_file(self, f):
        self._validate_file(f)
        file_name = secure_filename(f.filename)
        self.file_path = app.config['UPLOAD_FOLDER'].child(file_name)
        f.save(self.file_path)

    def _validate_file(self, f):
        if not f:
            raise ValueError("Please, select a mission for parsing.")

        if not self._file_is_allowed(f):
            raise ValueError("Sorry, invalid file format.")

    def _file_is_allowed(self, f):
        filename = f.filename.lower()
        return (
            '.' in filename
            and filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS
            and f.mimetype in settings.ALLOWED_MIME_TYPES)

    def _parse_mission(self):
        return MissionParser().parse(self.file_path)

    def _on_parsing_error(self, e):
        app.logger.exception("Failed to parse mission.")

        issue_title = repr(e)
        issue = reporter.get_issue(issue_title)
        similar = map(reporter.shorten_issue,
                      reporter.get_similar_issues(title=issue_title))

        if not issue:
            issue = reporter.report_issue(
                title=issue_title,
                description=self._get_issue_info())
        elif reporter.is_valid(issue) and issue['state'] != 'open':
            reporter.reopen_issue(
                issue=issue,
                comment=self._get_issue_info())

        issue = reporter.shorten_issue(issue)
        app.logger.error(
            "Github issue:\n"
            "  Number: {number}.\n"
            "  State: {state}.\n"
            "  Is valid: {is_valid}.\n"
            "  URL: {url}"
            .format(**issue))

        return {
            'similar': similar,
            'traceback': traceback.format_exc(),
            'issue': issue,
        }

    def _get_issue_info(self):
        remote_file = upload_file_to_google_drive(
            file_path=self.file_path,
            folder_id=settings.GOOGLE_DRIVE_FOLDER_ID)
        if remote_file:
            link = format_remote_file_link(remote_file)
            return "Mission file: {}.".format(link)

    def _remove_file(self):
        self.file_path.remove()


rest.add_view_url_rule('/parse', MissionParseView)
