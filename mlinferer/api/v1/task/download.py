# -*- coding: utf-8 -*-
import os
from zipfile import ZipFile

import flask_restful
from flask import make_response

import api


class Download(flask_restful.Resource):
    def get(self, uuid, asset):
        datamanager = api.getdatamanager()
        # TODO: check here that uuid and asset doesn't contains ".." in the path.
        # Otherwise it would be a security flaw
        assert asset == 'all.zip', "{} asset not available. Asset can be only all.zip by now".format(asset)

        zipPath = os.path.join(datamanager.path(uuid), asset)
        with ZipFile(zipPath, 'w') as myzip:
            for file in datamanager.files(uuid):
                if not file.lower().endswith('.zip'):
                    myzip.write(os.path.join(datamanager.path(uuid), file), file)

        with open(zipPath, "rb") as f:
            content = f.read()
        response = make_response(content)

        response.headers['content-type'] = 'application/zip'
        response.headers['Content-Disposition'] = 'inline; filename="{}"'.format(asset)
        return response
