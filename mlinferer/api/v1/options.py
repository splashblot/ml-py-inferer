# -*- coding: utf-8 -*-

import flask_restful

from api.v1.daos import OptionDAO, OptionType


class Options(flask_restful.Resource):
    def get(self):
        return [o.toDict() for o in [OptionDAO("domain1", "help1", "name1", OptionType.int, "value1"),
                                     OptionDAO("domain2", "help2", "name2", OptionType.bool, "value2")]]