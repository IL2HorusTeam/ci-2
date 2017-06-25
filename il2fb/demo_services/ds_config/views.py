# coding: utf-8

import configparser
import io
import logging

from aiohttp import web

from il2fb.config.ds import ServerConfig

from il2fb.demo_services.core.response.rest import RESTBadRequest, RESTSuccess

from .constants import ALLOWED_CONTENT_TYPES, ALLOWED_EXTENSIONS


LOG = logging.getLogger(__name__)


async def http_health(request):
    pretty = 'pretty' in request.query
    return RESTSuccess(payload={'status': 'alive'}, pretty=pretty)


class DefaultView(web.View):

    async def get(self):
        pretty = 'pretty' in self.request.query
        return RESTSuccess(
            payload={
                'data': ServerConfig.default().to_primitive(),
            },
            pretty=pretty,
        )


class ParseFileView(web.View):

    async def post(self):
        pretty = 'pretty' in self.request.query

        try:
            payload = await self.request.post()
            config = payload['file']
            self.file_name = config.filename
            self.content_type = config.content_type
        except Exception as e:
            LOG.exception("failed to upload config")
            return RESTBadRequest(
                detail=f"Oops! Failed to upload config: {e}",
            )

        try:
            self.validate()
        except ValueError as e:
            LOG.error(
                f"uploaded config '{self.file_name}' is invalid: {e}"
            )
            return RESTBadRequest(
                detail=f"Oops! Uploaded config is invalid: {e}",
            )

        try:
            self.content = config.file.read().decode()
            ini = configparser.ConfigParser()
            ini.readfp(io.StringIO(self.content))
        except Exception as e:
            LOG.exception(
                f"failed to read config '{self.file_name}'"
            )
            return RESTBadRequest(
                detail=f"Oops! Failed to read config: {e}",
            )

        try:
            data = ServerConfig.from_ini(ini).to_primitive()
        except Exception:
            LOG.exception(
                f"failed to parse config '{self.file_name}'"
            )
            payload = await self.on_parsing_error()
            return RESTBadRequest(
                payload=payload,
                detail=f"Oops! Failed to parse config '{self.file_name}'.",
                pretty=pretty,
            )

        if not data:
            return RESTBadRequest(
                detail=(
                    "Oops! Your config is blank or does not contain any "
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
        return {}
