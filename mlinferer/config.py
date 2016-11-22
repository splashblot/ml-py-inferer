#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path

from logic.daos import OptionDAO, OptionType


class Config(object):
    DEBUG = False
    PORT = 5000
    HOST = '0.0.0.0'
    URL_PREFIX = ''
    PROJECT_ROOT = path.abspath(path.dirname(__file__))
    TASKS_STORAGE_ROOT = path.join(PROJECT_ROOT, "tasks_data")
    PY_FASTER_RCNN_MODELS = {}
    PY_FASTER_RCNN_OPTIONS = [
        OptionDAO(
            domain="String",
            help="Name of the model to be used",
            name="model",
            # types: int, float,string, bool
            type=OptionType.string,
            value=""),
        OptionDAO(
            domain="Float number between 0 and 1",
            help="Only consider as detections objects with probability bigger than the given threshold",
            name="prob_threshold",
            # types: int, float,string, bool
            type=OptionType.float,
            value="0.5"),
        OptionDAO(
            domain="Float number between 0 and 1",
            help="Threshold for Non Minimal Supression. Used for deduplicate different detections for the same object (boxes deduplication).",
            name="nms_threshold",
            # types: int, float,string, bool
            type=OptionType.float,
            value="0.3")
    ]
    EXECUTOR_WORKERS = 5
    EXECUTOR_QUEUE_SIZE = 50  # Backpressure queue


class Development(Config):
    DEBUG = True
    TASKS_STORAGE_ROOT = "/tmp/ml-py-inferer/tasks_data"
    _faster_root = "../py-faster-rcnn-charm"
    PY_FASTER_RCNN_MODELS = {
        'nectarine-6000': {
            'inferer': {
                'caffemodel': _faster_root + "/output/faster_rcnn_end2end/nectarines_trainval/vgg16_faster_rcnn_iter_6000.caffemodel",
                'prototxt': _faster_root + "/models/nectarines/VGG16/faster_rcnn_end2end/test.prototxt",
                'cfgfile': _faster_root + "/experiments/cfgs/faster_rcnn_end2end.yml",
                'usecpu': True
            },
            'default': True
        }
    }


class Production(Config):
    pass


class Testing(Config):
    TASKS_STORAGE_ROOT = "/tmp/ml-py-inferer/tasks_data"
    TESTING = True
