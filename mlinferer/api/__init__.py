import os

import flask
from flask import Flask, current_app, g

from api.v1 import api_v1_bp
from api.v2 import api_v2_bp, API_VERSION_V2
from logic.fs import Fs

def create_app(environment=None):
    app = Flask(__name__)
    with app.app_context():
        if not environment:
            environment = os.environ.get('FLASK_CONFIG', 'development')
        app.config.from_object('config.{}'.format(environment.capitalize()))
        app.config.from_pyfile(
            'config_{}.py'.format(environment.lower()),
            silent=True
        )

        app.register_blueprint(
            api_v1_bp,
            url_prefix='{prefix}'.format(
                prefix=app.config['URL_PREFIX']))

        app.register_blueprint(
            api_v2_bp,
            url_prefix='{prefix}/v{version}'.format(
                prefix=app.config['URL_PREFIX'],
                version=API_VERSION_V2))

        # setattr(flask.g, 'datamanager', Fs(app.config['TASKS_STORAGE_ROOT']))

        return app


def getdatamanager() -> Fs:
    """Opens a new datamanager if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'datamanager'):
        g.datamanager = Fs(flask.current_app.config['TASKS_STORAGE_ROOT'])
    return g.datamanager