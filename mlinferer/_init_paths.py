"""Set up paths."""

import faulthandler
import os.path as osp
import signal
import sys

faulthandler.register(signal.SIGUSR2, all_threads=True)


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


this_dir = osp.dirname(__file__)

# Add caffe to PYTHONPATH
caffe_path = osp.join(this_dir, '..', 'py-faster-rcnn', 'caffe-fast-rcnn', 'python')
add_path(caffe_path)

# Add lib to PYTHONPATH
lib_path = osp.join(this_dir, '..', 'py-faster-rcnn', 'lib')
add_path(lib_path)
