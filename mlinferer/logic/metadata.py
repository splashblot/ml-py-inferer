import datetime

from typing import List, Dict, Any

from api.v1.daos import optionDAO, StatusDAO, StatusCode


class Metadata():
    def __init__(self, name:str, images:List[str], options:optionDAO, creation_date:datetime.datetime, status:StatusDAO, processingTime:int):
        # See http://code.activestate.com/recipes/286185-automatically-initializing-instance-variables-from/#c1
        self.__dict__.update(locals())
        del self.self

    def toDict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'images': self.images,
            'options': [o.toDict() for o in self.options],
            'creation_date': self.creation_date.timestamp(),
            'status' : self.status.toDict(),
            'processingTime': self.processingTime
        }

    @staticmethod
    def fromDict(dict) -> 'Metadata':
        options = None
        if 'options' in dict:
            options = [optionDAO(**o) for o in dict['options']]
        params = dict.copy()
        params['status']['code'] = StatusCode(params['status']['code'])
        params['status'] = StatusDAO(**params['status'])
        params['options'] = options
        params['creation_date'] = datetime.datetime.fromtimestamp(params['creation_date'] / 1e3)
        return Metadata(**params)