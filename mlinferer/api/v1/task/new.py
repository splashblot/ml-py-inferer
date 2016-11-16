# -*- coding: utf-8 -*-
import datetime
import json
import os

import flask_restful
import werkzeug
from flask import current_app
from flask_restful import reqparse

import api
import api.v1
from api.v1.daos import Response200DAO, StatusCode, optionDAO, StatusDAO
from logic.metadata import Metadata

parser = reqparse.RequestParser()
parser.add_argument('images', type=werkzeug.datastructures.FileStorage, required=True,
                    help='Images to process', location='files', action="append")
parser.add_argument('name', type=str, location='form', help="An optional name to be associated with the task", )
parser.add_argument('options', type=str, location='form',
                    help="""Serialized JSON string of the options to use for processing, as an array of the format:
                     [{name: option1, value: value1}, {name: option2, value: value2}, …]. F
                     or example, [{"name":"cmvs-maxImages","value":"500"},{"name":"time","value":true}]. F
                     or a list of all options, call /options """)

class New(flask_restful.Resource):
    def post(self):
        args = parser.parse_args()

        datamanager = api.getdatamanager()
        (id, path) = datamanager.new()

        # Writing images
        print("name: " + args['name'])
        for image in args.images:
            image.save(os.path.join(path, image.filename))

        try:
            options_str = args['options']
            options = json.loads(options_str)
            options = [optionDAO(**o) for o in options]
        except KeyError:
            # Key is not present
            pass

        # Writting metadata
        metadata = Metadata(
            name = args['name'],
            images = [image.filename for image in args.images],
            options = options,
            creation_date = datetime.datetime.now(),
            status = StatusDAO(StatusCode.QUEUED),
            processingTime=-1
        )
        datamanager.setstatus(id, json.dumps(metadata.toDict()))

        current_app.logger.info("task/new request with meta {}".format(json.dumps(metadata.toDict(), separators=(',',':'))))
        return Response200DAO(id).toDict()
