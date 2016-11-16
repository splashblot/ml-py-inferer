# -*- coding: utf-8 -*-
import json

import flask_restful

import api
from api.v1.daos import TaskInfoDAO
from logic import Metadata


class Info(flask_restful.Resource):
    def get(self, uuid):
        metadata = self.loadmetadata(uuid)
        datamanager = api.getdatamanager()

        resp = self.metadatatoinfo(metadata, uuid, len(datamanager.files(uuid)))

        return resp.toDict()

    def loadmetadata(self, uuid):
        datamanager = api.getdatamanager()
        print (datamanager.getstatus(uuid) + uuid)
        return Metadata.fromDict(json.loads(datamanager.getstatus(uuid)))

    def metadatatoinfo(self, metadata:Metadata, uuid, imagesCount) -> TaskInfoDAO:
        return TaskInfoDAO(
            dateCreated=metadata.creation_date.timestamp(),
            imagesCount=imagesCount,
            name=metadata.name,
            options=metadata.options,
            processingTime=metadata.processingTime,
            status=metadata.status,
            uuid=uuid
        )

