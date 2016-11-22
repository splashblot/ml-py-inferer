# -*- coding: utf-8 -*-
import flask
import flask_restful


class Options(flask_restful.Resource):
    def get(self):
        return [o.toDict() for o in
                flask.current_app.config['PY_FASTER_RCNN_OPTIONS']]
