# -*- coding: utf-8 -*-
import flask_restful

import api
import api.v1
from logic.daos import InfoDAO
from logic.daos import StatusCode

class Info(flask_restful.Resource):
    def get(self):
        datamanager = api.get_datamanager()
        return InfoDAO(datamanager.withmetadata(
            lambda meta: meta.status.code == StatusCode.QUEUED.name),
            api.v1.API_VERSION).toDict()
