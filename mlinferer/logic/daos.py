from enum import Enum

from typing import Iterable, Any, Dict

class ResponseDAO:
    def __init__(self, success: bool, error: str = None):
        self.success = success
        self.error = error

    def toDict(self) -> Dict[str, Any]:
        ret = {'success': self.success}
        if not self.success and self.error != None:
            ret['error'] = self.error
        return ret

class InfoDAO():
    def __init__(self, taskQueueCount: int, version: str):
        self.taskQueueCount = taskQueueCount
        self.version = version

    def toDict(self) -> Dict[str, Any]:
        return {
            'taskQueueCount': self.taskQueueCount,
            'version': self.version
        }

class OptionType(Enum):
    int = 1
    float = 2
    string = 3
    bool = 4

class OptionDAO():
    def __init__(self, domain: str, help: str, name: str, type: OptionType, value: str):
        self.domain = domain
        self.help = help
        self.name = name
        self.type = type
        self.value = value

    def toDict(self) -> Dict[str, Any]:
        return {
            'domain': self.domain,
            'help': self.help,
            'name': self.name,
            'type': self.type.name,
            'value': self.value
        }

class Response200DAO():
    def __init__(self, uuid: str):
        self.uuid = uuid

    def toDict(self) -> Dict[str, Any]:
        return {
            'uuid': self.uuid
        }

class StatusCode(Enum):
    QUEUED = 10
    RUNNING = 20
    FAILED = 30
    COMPLETED = 40
    CANCELED = 50

class StatusDAO():
    def __init__(self, code:StatusCode, errorMessage:str=None):
        self.code = code
        self.errorMessage = errorMessage

    def toDict(self) -> Dict[str, Any]:
        ret = {
            'code': self.code.value
        }
        if self.errorMessage:
            ret['errorMessage'] = self.errorMessage
        return ret

    @staticmethod
    def fromDict(dict) -> 'StatusDAO':
        params = dict.copy()
        params['status'] = StatusCode(params['status'])
        return StatusDAO(**params)


class optionDAO():
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def toDict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value
        }

class TaskInfoDAO():
    def __init__(self, dateCreated:int, imagesCount: int, name: str,
                 options: Iterable[optionDAO], processingTime: int,
                 status: StatusDAO, uuid: str):
        # See http://code.activestate.com/recipes/286185-automatically-initializing-instance-variables-from/#c1
        self.__dict__.update(locals())
        del self.self

    def toDict(self) -> Dict[str, Any]:
        return {
            'dateCreated': self.dateCreated,
            'imagesCount': self.imagesCount,
            'name': self.name,
            'options': [o.toDict() for o in self.options],
            'processingTime': self.processingTime,
            'status': self.status.toDict(),
            'uuid': self.uuid
        }

    @staticmethod
    def fromDict(dict) -> 'TaskInfoDAO':
        options = None
        if 'options' in dict:
            options = [optionDAO(**o) for o in dict['options']]
        params = dict.copy()
        params['status'] = StatusDAO(**params['status'])
        params['options'] = options
        return TaskInfoDAO(**params)


# Exceptions and error handling

class ErrorExample(Exception):
    pass

class ErrorDAO:
    def __init__(self, error: str):
        self.error = error

    def toDict(self) -> Dict[str, Any]:
        return {'error': self.error}

# Dict of error messages per each exception.
custom_errors = {
    'ErrorExample': ErrorDAO("Ejemplo de error").toDict()
}

