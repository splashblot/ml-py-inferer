import atexit
import logging
import pprint
import threading
from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Thread
from typing import List

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


def get_logger():
    return _logger


class Worker(metaclass=ABCMeta):
    """"
    Worker class to be used with @Executor. Implement it with your own processing code.
    """

    @abstractmethod
    def process(self, *args, **kwargs):
        """
        Override this method with your custom logic
        """
        pass

    def shutdown(self):
        """
        Override for cleanly shutting down resources.
        """
        pass

    def getLogger(self):
        """
        :return: a logger ready to be used
        """
        return threading.get_logger()

    def _start(self, queue:Queue, name:str):
        if hasattr(self, '_process'):
            raise AlreadyStartedException()
        self._queue = queue
        self._process = Thread(target=self._run, name=name, daemon=True)
        self._process.start()

    def _run(self):
        while True:
            ret = self._queue.get()
            if (ret == None):
                _logger.info("Exiting")
                break
            (args, kwargs) = ret
            strparams = pprint.pformat(args, compact=True) + ' ' + pprint.pformat(kwargs, compact=True)
            _logger.info("Executing. Params {}".format(strparams))
            try:
                self.process(*args, **kwargs)
            except Exception as e:
                _logger.exception("Exception when executing with params " + strparams)
        self.shutdown()

    def _join(self, *args, **kwargs):
        if self._process != None:
            self._process.join(*args, **kwargs)

class Executor():
    _TIMEOUT = 5

    """
    Allows to execute tasks in parallel, keeping track about what is going on.
    :arg queue_size Set queue to some size if backpressure is needed.
    """
    def __init__(self, workers:List[Worker], queue_size:int = -1, name="Executor"):
        self._name = name
        self._workers = workers
        self._queue = Queue(queue_size)
        self._start()

    def _start(self):
        workers = self._workers
        for i in range(len(workers)):
            workers[i]._start(self._queue, self._name + "-" + str(i))
        self._started = True
        atexit.register(self.stop)

    def process(self, *args, **kwargs):
        """
        Call for processing a given task
        """
        if self._started:
            self._queue.put((args, kwargs))
        else:
            raise AlreadyStoppedException("Trying to execute something but executor is already stopped.")

    def stop(self):
        """
        Stop the executor. Should be executed by the same process that created it.
        """
        if not self._started:
            _logger.warning("Executor already stopped")
            return
        atexit.unregister(self.stop)
        # Sending poisons so that workers die
        for i in range(len(self._workers)):
            self._queue.put_nowait(None)

        for w in self._workers:
            try:
                w._join(5)
            except TimeoutError:
                _logger.error("Timout waiting for finalization of worker " + w._process.name)
                # should terminate be called here?

    def queue_size(self):
        return self._queue.qsize()

class AlreadyStartedException(Exception):
    pass


class AlreadyStoppedException(Exception):
    pass

