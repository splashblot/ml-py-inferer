# -*- coding: utf-8 -*-

import flask_restful
from flask_restful import reqparse

from logic.daos import ResponseDAO

parser = reqparse.RequestParser()
parser.add_argument('uuid', type=str, required=True, help='UUID of the task')

class Cancel(flask_restful.Resource):
    def post(self):
        args = parser.parse_args()
        return ResponseDAO(success=False, error="Not implemented").toDict()
