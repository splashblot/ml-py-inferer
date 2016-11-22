# -*- coding: utf-8 -*-
"""
Api matching spec at https://github.com/pierotofy/node-OpenDroneMap/blob/5a91ec4d764cf448f990ff8c35a89725f3884181/docs/index.adoc
with Version 1.0.1
"""
import flask_restful
from flask import Blueprint

from api.v1.info import Info
from api.v1.options import Options
from api.v1.task.cancel import Cancel
from api.v1.task.download import Download
from api.v1.task.info import Info as TaskInfo
from api.v1.task.new import New
from api.v1.task.output import Output
from api.v1.task.remove import Remove
from api.v1.task.restart import Restart
from logic.daos import custom_errors

API_VERSION_V1 = 1
API_VERSION = API_VERSION_V1

api_v1_bp = Blueprint('api_v1', __name__)
api_v1 = flask_restful.Api(api_v1_bp, errors=custom_errors)

api_v1.add_resource(Info, "/info")
api_v1.add_resource(Options, "/options")
api_v1.add_resource(Cancel, "/task/cancel")
api_v1.add_resource(New, "/task/new")
api_v1.add_resource(Remove, "/task/remove")
api_v1.add_resource(Restart, "/task/restart")
api_v1.add_resource(Download, "/task/<string:uuid>/download/<string:asset>")
api_v1.add_resource(TaskInfo, "/task/<string:uuid>/info", endpoint="task_info")
api_v1.add_resource(Output, "/task/<string:uuid>/output")


