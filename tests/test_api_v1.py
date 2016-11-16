#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import pprint
import unittest
from os.path import join
from zipfile import ZipFile

import api
from api import create_app
from api.v1.daos import Response200DAO, ResponseDAO, TaskInfoDAO, StatusCode
from logic import Metadata

CONTENTS = 'my file contents'
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
    CONTENTS = CONTENTS.encode('utf-8')


def fromJson(resp):
    return json.loads(resp.get_data(as_text=True))

class APIV1TestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(environment="Testing")
        self.app.app_context().push()
        self.app.testing = True
        self.url_prefix = self.app.config['URL_PREFIX']
        self.datamanager = datamanager = api.getdatamanager()

    def tearDown(self):
        self.datamanager.deleteall()
        # self.app.app_context().pop()

    #@unittest.skip("demonstrating skipping")
    def test_info(self):
        data = json.loads(self.app.test_client().get('/info').get_data(as_text=True))
        assert data.get('version') == 1
        assert data.get('taskQueueCount') == 0, data.get('taskQueueCount')

    def test_options(self):
        data = json.loads(self.app.test_client().get('/options').get_data(as_text=True))

    def test_task_cancel(self):
        resp = self.app.test_client().post('/task/cancel', data={'uuid': 24})
        data = ResponseDAO(**fromJson(resp))
        assert data.success == True

    def test_task_new(self):
        resp = self.app.test_client().post(self.url_prefix + 'task/new', data={
            'images': [(StringIO(CONTENTS), "image1.jpg"), (StringIO(CONTENTS), "image2.jpg")],
            'name': 'Task1',
            'options': '[{"name": "size", "value": "300"}, {"name": "param1", "value": "tal"}]'
        })
        data = Response200DAO(**fromJson(resp))

        files = self.datamanager.files(data.uuid)
        assert 'image1.jpg' in files
        assert 'image2.jpg' in files
        datastr = self.datamanager.getstatus(data.uuid)
        meta = Metadata.fromDict(json.loads(datastr))
        assert  meta.status.code == StatusCode.QUEUED, meta.status.code

    def test_task_remove(self):
        resp = self.app.test_client().post('/task/remove', data={'uuid': 24})
        data = ResponseDAO(**fromJson(resp))
        assert data.success == True

    def test_task_restart(self):
        resp = self.app.test_client().post('/task/restart', data={'uuid': 24})
        data = ResponseDAO(**fromJson(resp))
        assert data.success == True

    def test_task_download(self):
        (id, path) = self.datamanager.new()
        with open(join(path, "pru.txt"), 'w') as f:
            f.write("hola colega")
        resp = self.app.test_client().get('/task/{}/download/all.zip'.format(id))
        saved = join(path, "saved.zip")
        with open(saved, "wb") as f:
            f.write(resp.get_data())
        with ZipFile(saved, 'r') as z:
            with z.open("pru.txt", 'r') as f:
                read = f.read().decode('utf-8')
                assert read == "hola colega", read

    def test_task_info(self):
        resp = self.app.test_client().post(self.url_prefix + 'task/new', data={
            'images': [(StringIO(CONTENTS), "image1.jpg"), (StringIO(CONTENTS), "image2.jpg")],
            'name': 'Task1',
            'options': '[{"name": "size", "value": "300"}, {"name": "param1", "value": "tal"}]'
        })
        data = Response200DAO(**fromJson(resp))

        resp = self.app.test_client().get('/task/{}/info'.format(data.uuid))
        data = TaskInfoDAO.fromDict(fromJson(resp))
        pprint.pprint(vars(data))

    def test_task_output(self):
        resp = self.app.test_client().get('/task/24j/output')
        assert resp.get_data(as_text=True) == "content,content", resp.get_data(as_text=True)

if __name__ == '__main__':
    unittest.main()
