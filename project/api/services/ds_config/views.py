# coding: utf-8

import ConfigParser
import io

from flask import request
from flask.views import MethodView

from project.api.blueprints import RESTBlueprint
from project.api.response.rest import (
    RESTSuccess, RESTBadRequest, RESTInternalServerError,
)

from il2fb.config.ds import ServerConfig


rest = RESTBlueprint(r'ds-config', __name__)


@rest.route(r'/default', methods=['GET'])
def get_default():
    return RESTSuccess({
        'data': ServerConfig.default().to_primitive(),
    })


class ConfigParseView(MethodView):

    def post(self):
        f = request.files['file']
        content = f.read()

        ini = ConfigParser.ConfigParser()
        ini.readfp(io.BytesIO(content))

        data = ServerConfig.from_ini(ini).to_primitive()

        return RESTSuccess({
            'file_name': f.filename,
            'data': data,
        })


rest.add_view_url_rule('/parse', ConfigParseView)
