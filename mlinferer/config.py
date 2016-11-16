#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path


class Config(object):
    DEBUG = False
    PORT = 5000
    HOST = '0.0.0.0'
    URL_PREFIX = ''
    PROJECT_ROOT = path.abspath(path.dirname(__file__))
    TASKS_STORAGE_ROOT = path.join(PROJECT_ROOT, "tasks_data")
    # TEMPLATE_FOLDER = path.join(PROJECT_ROOT, 'templates')
    # MYSQL_DATABASE_HOST = '127.0.0.1'
    # MYSQL_DATABASE_DB = 'default_db'
    # MYSQL_DATABASE_USER = 'default_user'
    # MYSQL_DATABASE_PASSWORD = 'password'


class Development(Config):
    DEBUG = True
    TASKS_STORAGE_ROOT = "/tmp/ml-py-inferer/tasks_data"

class Production(Config):
    pass

class Testing(Config):
    TASKS_STORAGE_ROOT = "/tmp/ml-py-inferer/tasks_data"
    TESTING = True
