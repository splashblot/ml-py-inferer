# -*- coding: utf-8 -*-

import flask_restful
from flask import make_response

class Output(flask_restful.Resource):
    def get(self, uuid):
        response = make_response('[]')
        response.headers['content-type'] = 'text/plain'
        return response
