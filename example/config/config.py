from os import path

DEBUG = False
PORT = 5001
HOST = '0.0.0.0'
URL_PREFIX = ''
PROJECT_ROOT = '/data/ml-py-inferer'
TASKS_STORAGE_ROOT = path.join(PROJECT_ROOT, "tasks_data")
PY_FASTER_RCNN_MODELS = {
        'nectarine-6000': {
            'inferer': {
                'caffemodel': PROJECT_ROOT + "/models/nectarines/vgg16_faster_rcnn_iter_6000.caffemodel",
                'prototxt': PROJECT_ROOT + "/models/nectarines/VGG16/faster_rcnn_end2end/test.prototxt",
                'cfgfile': PROJECT_ROOT + "/models/nectarines/cfgs/faster_rcnn_end2end.yml",
                'usecpu': True
            },
            'default': True
        }
#,
#        'nectarine-18000': {
#            'inferer': {
#                'caffemodel': PROJECT_ROOT + "/models/nectarines/vgg16_faster_rcnn_iter_18000.caffemodel",
#                'prototxt': PROJECT_ROOT + "/models/nectarines/VGG16/faster_rcnn_end2end/test.prototxt",
#                'cfgfile': PROJECT_ROOT + "/models/nectarines/cfgs/faster_rcnn_end2end.yml",
#                'usecpu': True
#            },
#        }
}
EXECUTOR_WORKERS = 2
EXECUTOR_QUEUE_SIZE = 50  # Backpressure queue

