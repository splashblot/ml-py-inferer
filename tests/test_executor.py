#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import unittest

from multiprocessing import Lock

from multiprocessing import Value

from logic.executor import Worker, Executor
from logic.fs import Fs


class ExecutorTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_executor(self):
        NW = 5
        sum = Value('i', 0)
        numWorkers = Value('i', NW)
        ex = Executor([TestWorker(sum, numWorkers) for i in range(NW)],-1,"EX")

        IT = 10
        SUM = 2
        for i in range(IT):
            ex.process(SUM)
        ex.stop()
        assert sum .value== IT * SUM, sum.value
        assert numWorkers.value == 0, numWorkers.value

class TestWorker(Worker):
    def __init__(self, sum, numWorkers):
        self.sum = sum
        self.numWorkers = numWorkers

    def process(self, sum):
        self.sum.get_lock().acquire()
        self.sum.value += sum
        self.sum.get_lock().release()

    def shutdown(self):
        self.numWorkers.get_lock().acquire()
        self.numWorkers.value += -1
        self.numWorkers.get_lock().release()


if __name__ == '__main__':
    unittest.main()
