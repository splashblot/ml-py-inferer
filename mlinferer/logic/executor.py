import logging
import multiprocessing
import pprint
from abc import ABCMeta, abstractmethod
from multiprocessing import Process
from multiprocessing import Queue

import atexit
from typing import List

logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

class Worker(metaclass=ABCMeta):
    _process = None

    """"
    Worker class to be used with @Executor. Implement it with your own processing code.
    """

    @abstractmethod
    def process(self, *args, **kwargs):
        """
        Override this method with your custom logic
        """
        pass

    @abstractmethod
    def shutdown(self):
        """
        Override for cleanly shutting down resources.
        """
        pass

    def _start(self, queue:Queue, name:str):
        if self._process != None:
            raise AlreadyStartedException()
        self._queue = queue
        self._process = Process(target=self._run, name=name)
        self._process.start()

    def _run(self):
        while True:
            ret = self._queue.get()
            if (ret == None):
                logger.info("Exiting")
                break
            (args, kwargs) = ret
            strparams = pprint.pformat(args, compact=True) + ' ' + pprint.pformat(kwargs, compact=True)
            logger.info("Executing. Params {}".format(strparams))
            try:
                self.process(*args, **kwargs)
            except Exception as e:
                logger.exception("Exception when executing with params " + strparams)
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
            logger.warning("Executor already stopped")
            return
        atexit.unregister(self.stop)
        # Sending poisons so that workers die
        for i in range(len(self._workers)):
            self._queue.put_nowait(None)

        for w in self._workers:
            try:
                w._join(5)
            except TimeoutError:
                logger.error("Timout waiting for finalization of worker " + w._process.name)
                # should terminate be called here?

class AlreadyStartedException(Exception):
    pass


class AlreadyStoppedException(Exception):
    pass

