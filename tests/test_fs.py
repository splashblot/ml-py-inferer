#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import unittest

import shutil

from logic.fs import Fs


class FSTestCase(unittest.TestCase):
    TEST_FOLDER = "/tmp/python-unit-test-Fs" + str(time.time())

    def setUp(self):
        self.fs = Fs(self.TEST_FOLDER)

    def tearDown(self):
        shutil.rmtree(self.TEST_FOLDER)

    def test_info(self):
        fs = self.fs
        (uuid, path) = fs.new()
        assert os.path.join(self.TEST_FOLDER, uuid) == path
        assert os.path.isdir(os.path.join(self.TEST_FOLDER, uuid))
        assert fs.getstatus(uuid) == None
        fs.setstatus(uuid, "status")
        assert fs.getstatus(uuid) == "status"
        files = fs.files(uuid)
        assert files[0] == Fs.STATUS_FILE
        assert fs.folders()[0] == uuid
        fs.delete(uuid)
        assert not os.path.exists(os.path.join(self.TEST_FOLDER, uuid))
        assert os.path.isdir(self.TEST_FOLDER)


if __name__ == '__main__':
    unittest.main()
