import json
import logging
import os
import uuid
import shutil

from logic.metadata import Metadata


class Fs():
    STATUS_FILE = "_status_"

    """
    Filesystem folder as a storage place for tasks with ids.
    """
    def __init__(self, path:str):
        self._path = path
        if not os.path.exists(path):
            os.makedirs(path)

    def new(self):
        tid = str(uuid.uuid4())
        path = os.path.join(self._path, tid)
        os.makedirs(path)
        return (tid, path)

    def path(self, uuid):
        assert len(uuid)>0
        assert not uuid.startswith('.')
        assert '/' not in uuid
        return os.path.join(self._path, uuid)

    def folders(self):
        """
        :return: List of existing folders
        """
        files = os.listdir(self._path)
        ret = []
        for f in files:
            if os.path.isdir(os.path.join(self._path, f)):
                ret.append(f)
        return ret

    def delete(self, uuid):
        path = self.path(uuid)
        shutil.rmtree(path)

    def deleteall(self):
        for folder in self.folders():
            shutil.rmtree(self.path(folder))

    def files(self, uuid):
        path = self.path(uuid)
        return [o for o in os.listdir(path) if not o == self.STATUS_FILE]

    def setstatus(self, uuid, status:str):
        path = os.path.join(self.path(uuid), self.STATUS_FILE)
        with open(path, "w") as file:
            file.write(status)

    def getstatus(self, uuid):
        path = os.path.join(self.path(uuid), self.STATUS_FILE)
        if (os.path.exists(path)):
            with open(path, "r") as file:
                return file.read()
        else:
            return None

    def withmetadata(self, booleanfunc):
        count = 0
        for uuid in self.folders():
            statusfile = os.path.join(self.path(uuid), self.STATUS_FILE)
            if os.path.exists(statusfile):
                with open(statusfile, "r") as f:
                    try:
                        meta = Metadata.fromDict(json.load(f))
                        if booleanfunc(meta):
                            count += 1
                    except Exception as e:
                        logging.exception(e)
        return count