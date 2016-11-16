# -*- coding: utf-8 -*-
import flask_restful

import api
import api.v1
from api.v1.daos import API_VERSION, StatusCode
from api.v1.daos import InfoDAO

class Info(flask_restful.Resource):
    def get(self):
        datamanager = api.getdatamanager()
        return InfoDAO(datamanager.withmetadata(lambda meta: meta.status.code == StatusCode.QUEUED.name), API_VERSION).toDict()