# coding: utf-8

import io
import logging
import sys
import traceback

from aiohttp import web

from il2fb.demo_services.core.response.rest import RESTBadRequest, RESTSuccess

from .constants import ALLOWED_CONTENT_TYPES, ALLOWED_EXTENSIONS


LOG = logging.getLogger(__name__)


class ParseView(web.View):

    async def post(self):
        pretty = 'pretty' in self.request.query

        try:
            payload = await self.request.post()
            mission = payload['file']
            self.file_name = mission.filename
            self.content_type = mission.content_type
        except Exception as e:
            LOG.exception("failed to upload mission")
            return RESTBadRequest(
                detail=f"Oops! Failed to upload mission: {e}",
            )

        try:
            self.validate()
        except ValueError as e:
            LOG.error(
                f"uploaded mission '{self.file_name}' is invalid: {e}"
            )
            return RESTBadRequest(
                detail=f"Oops! Uploaded mission is invalid: {e}",
            )

        try:
            self.content = mission.file.read().decode()
        except Exception as e:
            LOG.exception(
                f"failed to read mission '{self.file_name}'"
            )
            return RESTBadRequest(
                detail=f"Oops! Failed to read mission: {e}",
            )

        stream = io.StringIO(self.content)

        try:
            data = self.request.app['mission_parser'].parse(stream)
        except Exception:
            LOG.exception(
                f"failed to parse mission '{self.file_name}'"
            )
            payload = await self.on_parsing_error()
            return RESTBadRequest(
                payload=payload,
                detail=f"Oops! Failed to parse mission '{self.file_name}'.",
                pretty=pretty,
            )

        if not data:
            return RESTBadRequest(
                detail=(
                    "Oops! Your mission is blank or does not contain any "
                    "known sections."
                ),
                pretty=pretty,
            )

        return RESTSuccess(
            payload={
                'file_name': self.file_name,
                'data': data,
            },
            pretty=pretty,
        )

    def validate(self):
        if not (
            '.' in self.file_name and
            self.file_name.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS and
            self.content_type in ALLOWED_CONTENT_TYPES
        ):
            raise ValueError("uploaded file has unsupported type")

    async def on_parsing_error(self):
        etype, value, tb = sys.exc_info()
        reporter = self.request.app['bug_reporter']

        issue_title = repr(value)
        issue = await reporter.get_issue(issue_title)
        mission_info = '\n'.join([
            "",
            f"Mission `{self.file_name}`:",
            f"```\n{self.content}```",
        ])

        if not issue:
            issue = await reporter.report_issue(
                title=issue_title,
                description=mission_info,
            )
        elif reporter.is_valid(issue) and issue['state'] != "open":
            await reporter.reopen_issue(
                issue=issue,
                comment=mission_info,
            )

        issue = reporter.shorten_issue(issue)
        similar = await reporter.get_similar_issues(title=issue_title)
        similar = list(map(reporter.shorten_issue, similar))

        LOG.error(
            '\n'
            .join([
                "GitHub issue:",
                "  Number: {number}",
                "  State: {state}",
                "  Is valid: {is_valid}",
                "  URL: {url}",
            ])
            .format(**issue)
        )

        tb = ''.join(traceback.format_exception(etype, value, tb))
        return {
            'issue': issue,
            'similar': similar,
            'traceback': tb,
        }
