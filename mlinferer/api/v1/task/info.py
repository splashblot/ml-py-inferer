# -*- coding: utf-8 -*-
import json

import flask_restful

import api
from logic import Metadata
from logic.daos import TaskInfoDAO


class Info(flask_restful.Resource):
    def get(self, uuid):
        metadata = self.loadmetadata(uuid)
        resp = self.metadatatoinfo(metadata)
        return resp.toDict()

    def loadmetadata(self, uuid):
        datamanager = api.get_datamanager()
        return Metadata.fromDict(json.loads(datamanager.getstatus(uuid)))

    def metadatatoinfo(self, metadata: Metadata) -> TaskInfoDAO:
        return TaskInfoDAO(
            dateCreated=metadata.creation_date.timestamp(),
            imagesCount=len(metadata.images),
            name=metadata.name,
            options=metadata.options,
            processingTime=metadata.processingTime,
            status=metadata.status,
            uuid=metadata.uuid
        )

