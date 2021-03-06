#!/usr/bin/python
# -*- coding: utf-8 -*-
import _init_paths
import argparse
import api


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='ml-py-inferer. REST server for doing object detection over images')
    parser.add_argument('--config-file', dest='config_file', help='Path to config file',
                        default=None, type=str)

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()

    app = api.create_app(config_file=args.config_file)
    app.run(host=app.config['HOST'], port=app.config['PORT'])