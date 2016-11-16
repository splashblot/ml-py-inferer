#!/usr/bin/python
# -*- coding: utf-8 -*-

from api import create_app
import unittest
import flask
import json


class APIV2TestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(environment="Testing")

    def test_hello_version(self):
        data = json.loads(self.app.test_client().get('/v2/helloworld').get_data(as_text=True))
        assert data.get('VERSION') == 2
        assert data.get('HELLO') == 'WORLD'


if __name__ == '__main__':
    unittest.main()
