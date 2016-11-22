# -*- coding: utf-8 -*-

import flask_restful
from flask_restful import reqparse

import api
from logic.daos import ResponseDAO

parser = reqparse.RequestParser()
parser.add_argument('uuid', type=str, required=True, help='UUID of the task')

class Remove(flask_restful.Resource):
    def post(self):
        args = parser.parse_args()
        datamanager = api.get_datamanager()
        datamanager.delete(args['uuid'])
        return ResponseDAO(success=True).toDict()
        #return {'success': True}