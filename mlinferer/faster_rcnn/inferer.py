import datetime
import inspect
import json
import os
import traceback
from os.path import isfile
from typing import List, Any, Dict

import cv2
import numpy as np

import caffe
from fast_rcnn.config import cfg, cfg_from_file
from fast_rcnn.test import im_detect
from logic import Metadata
from logic.daos import StatusDAO, StatusCode, optionDAO, OptionType, OptionDAO
from logic.executor import Worker, get_logger
from nms.py_cpu_nms import py_cpu_nms
from utils.timer import Timer

CLASSES = ('__background__',
           'nectarine')

logger = get_logger()


def save_detections(im, class_name, dets, imgName, outputDir, thresh=0.3):
    """Draw detected bounding boxes."""
    import matplotlib.pyplot as plt
    inds = np.where(dets[:, -1] >= thresh)[0]

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=3.5)
        )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.3),
                fontsize=10, color='white')

    ax.set_title(('{} {} detections with '
                  'p({} | box) >= {:.1f}').format(len(inds), class_name, class_name,
                                                  thresh),
                 fontsize=14)
    plt.axis('off')
    plt.tight_layout()

    (ignore, filename) = os.path.split(imgName)
    outfile = os.path.join(outputDir, filename)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    print("Saving test image with boxes in {}".format(outfile))
    plt.savefig(outfile)
    plt.close()


def process_image(net, im_file, outfolder, prob_threshold=0.5, nms_threshold=0.3, imgprefix=""):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print("Detection took {:.3f}s for {:d} object proposals".format(timer.total_time, boxes.shape[0]))

    (dir, name) = os.path.split(im_file)
    imgname = os.path.join(dir, imgprefix + name)

    # Visualize detections for each class
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        # TODO: for some reason native nms is not working properly
        # I have replaced it by the python version by now, but
        # idea in the future would it be to solve it and uncomment the
        # the following line and comment the python nms version.
        # keep = nms(dets, nms_threshold)
        keep = py_cpu_nms(dets, nms_threshold)
        dets = dets[keep, :]
        save_detections(im, cls, dets, imgname, outfolder, thresh=prob_threshold)


class Inferer():
    """
    Makes inference using faster-rcnn. WARNING. A lot of properties in
    caffe & py-faster are singletons, so they are shared. Probably having
    severals models running at the same time won't be possible. To be tested.
    """

    def __init__(self, caffemodel: str, prototxt: str, cfgfile: str, usecpu=True, gpu: int = 0):
        """
        :param caffemodel: Model file to use for inference
        :param prototxt: Prototxt definition of the net.
                For example: models/nectarines/VGG16/faster_rcnn_end2end/test.prototxt
        :param cfgfile: File with configuration for the py-faster-rcnn.
                For example: experiments/cfgs/faster_rcnn_end2end.yml
        :param usecpu: If use only CPU, or GPU
        :param gpu: GPU number to use
        """
        # See http://code.activestate.com/recipes/286185-automatically-initializing-instance-variables-from/#c1
        self.__dict__.update(locals())
        del self.self
        self._init_model()

    def _init_model(self):
        for file in [self.prototxt, self.cfgfile, self.caffemodel]: ensure_file_exists(file)
        cfg_from_file(self.cfgfile)

        if self.usecpu:
            caffe.set_mode_cpu()
        else:
            caffe.set_mode_gpu()
            caffe.set_device(self.gpu)
            cfg.GPU_ID = self.gpu
        self.net = caffe.Net(self.prototxt, self.caffemodel, caffe.TEST)

        print('Loaded network {:s}'.format(self.caffemodel))

        # Warmup on a dummy image
        im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
        for i in range(2):
            _, _ = im_detect(self.net, im)

    def infer(self, imgfolder: str, outfolder: str, imgprefix: str = "", imgset: List[str] = None,
              prob_threshold=0.5, nms_threshold=0.3):
        """
        :param imgfolder: folder where images are located
        :param outfolder: output folder where store resultant images and information
        :param imgprefix: prefix to use with resultant images
        :param imgsetfile: If provided, only images listed in file are processed.
        """
        ensure_dir_exists(imgfolder)

        image_names = []
        if imgset != None:
            im_names = imgset
        else:
            im_names = [f for f in os.listdir(imgfolder)
                        if isfile(os.path.join(imgfolder, f)) and f.lower().endswith(".jpg")]

        for im_name in im_names:
            print('Processing {} from {} and saving into {}'.
                  format(im_name, imgfolder, outfolder))
            process_image(self.net, os.path.join(imgfolder, im_name), outfolder, prob_threshold, nms_threshold,
                          imgprefix=imgprefix)


def ensure_file_exists(file):
    if not os.path.isfile(file):
        raise IOError("File {:s} not found.".format(file))


def ensure_dir_exists(dir):
    if not os.path.isdir(dir):
        raise IOError("Folder {:s} not found.".format(dir))


class InfererException(Exception):
    pass


class InfererHandler():
    """
    Handle many models for making inference. Instance it on main process
    and then share to processes to load once, use in many processes.
    """
    OUT_IMG_PREFIX = "out_"

    def __init__(self, config):
        """
        :param config: Loads config from here.
        """
        self._models = {}
        self._config = config
        self._options = {o.name: o for o in config['PY_FASTER_RCNN_OPTIONS']}
        for mname, mcfg in self._config['PY_FASTER_RCNN_MODELS'].items():
            if 'default' in mcfg and mcfg['default']:
                self._default = mname
            self._models[mname] = Inferer(**mcfg['inferer'])

    def process(self, _img_folder: str, _status_file_path: str):
        with open(_status_file_path, "r") as f:
            metadata = Metadata.fromDict(json.load(f))

        try:
            model_name, options = self.options_to_kwarr(metadata.options)
            try:
                model = self._models[model_name]
            except KeyError:
                raise InfererException("Model '{}' not available".format(model_name))

            model.infer(imgfolder=_img_folder,
                        outfolder=_img_folder,
                        imgprefix=InfererHandler.OUT_IMG_PREFIX,
                        imgset=metadata.images,
                        **options)

            start_time = metadata.creation_date
            end_time = datetime.datetime.now()
            metadata.processingTime = end_time.timestamp() - start_time.timestamp()
            metadata.status = StatusDAO(StatusCode.COMPLETED)
        except Exception as e:
            frame = inspect.currentframe()
            msg = "Error processing with parameters {}.".format(inspect.formatargvalues(*inspect.getargvalues(frame)))
            metadata.status = StatusDAO(StatusCode.FAILED,
                                        "{}. Exception {}".format(
                                            msg,
                                            traceback.format_exc()))
            logger.exception(msg)
        finally:
            try:
                with open(_status_file_path, "w") as f:
                    json.dump(metadata.toDict(), f)
            except:
                pass

    def options_to_kwarr(self, options: List[optionDAO]) -> (str, Dict[str, Any]):
        """
        Converting options list to a dict making the proper type conversion
        and parameter checking, and setting defaults
        :return: (model, dict of options)
        """
        kv = {}
        model = None
        # Converting given options
        for option in options:
            if option.name == 'model':
                model = option.name
                continue

            try:
                option_def = self._options[option.name]
                kv[option.name] = self.convert_option(option.value, option_def)
            except KeyError:
                raise InfererException("Option with name '{}' is not supported".
                                       format(option.name)) from None
        if not model:
            try:
                model = self._default
            except AttributeError:
                raise InfererException("No model is defined") from None

        # Setting defaults
        for name, option_def in self._options.items():
            if not name in kv and not name == 'model':
                kv[name] = self.convert_option(
                    option_def.value, option_def)

        return model, kv

    def convert_option(self, value, option_def: OptionDAO):
        """
        Converting value to proper type
        """
        return {
            OptionType.string: lambda x: x,
            OptionType.int: lambda x: int(x),
            OptionType.float: lambda x: float(x),
            OptionType.bool: lambda x: bool(x)
        }.get(option_def.type)(value)


class InfererWorker(Worker):
    """
    Worker for making inference.
    """

    def __init__(self, inference_handler: InfererHandler):
        self._handler = inference_handler

    def process(self, *args, **kwargs):
        self._handler.process(*args, **kwargs)
