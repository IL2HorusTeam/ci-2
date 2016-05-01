# -*- coding: utf-8 -*-

from project.api.blueprints import RESTBlueprint
from project.api.response.rest import RESTSuccess


rest = RESTBlueprint(r'mission-parser', __name__)


@rest.route(r'/parse', methods=['POST'])
def parse():
    return RESTSuccess(detail="hello!")
