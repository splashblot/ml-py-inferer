import os

from flask import Flask, current_app, g

from api.v1 import api_v1_bp
from api.v2 import api_v2_bp, API_VERSION_V2
from faster_rcnn.inferer import InfererWorker, InfererHandler
from logic.executor import Executor
from logic.fs import Fs


def create_app(environment=None, config_file=None):
    app = Flask(__name__)
    with app.app_context():
        if not environment:
            environment = os.environ.get('FLASK_CONFIG', 'development')
        app.config.from_object('config.{}'.format(environment.capitalize()))
        app.config.from_pyfile(
            'config_{}.py'.format(environment.lower()),
            silent=True
        )
        if config_file:
            app.config.from_pyfile(config_file)

        app.register_blueprint(
            api_v1_bp,
            url_prefix='{prefix}'.format(
                prefix=app.config['URL_PREFIX']))

        app.register_blueprint(
            api_v2_bp,
            url_prefix='{prefix}/v{version}'.format(
                prefix=app.config['URL_PREFIX'],
                version=API_VERSION_V2))

        # For storing FS into flask.g we use the property app_ctx_globals_class

        app.app_ctx_globals_class.datamanager = Fs(current_app.config['TASKS_STORAGE_ROOT'])

        workers = app.config['EXECUTOR_WORKERS']
        inferer_handler = InfererHandler(app.config)
        executor = Executor(
            [InfererWorker(inferer_handler) for i in range(workers)],
            app.config['EXECUTOR_QUEUE_SIZE'],
            "Inference Executor"
        )
        app.app_ctx_globals_class.executor = executor

        return app


def get_datamanager() -> Fs:
    """
    Opens a new datamanager if there is none yet for the
    current application context.
    """
    return g.datamanager


def get_executor() -> Executor:
    """"
    Returns the executor that can be used for enqueue data
    """
    return g.executor
