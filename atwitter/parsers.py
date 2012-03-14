"""
Parse response
"""

from json import loads as jloads
from urlparse import parse_qs


class BaseParser(object):
    def parse(self, data):
        raise NotImplementedError('You should define your parse(data)')


class NoopParser(BaseParser):
    def parse(self, data):
        return data


class JSONParser(BaseParser):
    def parse(self, data):
        try:
            return jloads(data) if data else None
        except:
            return {'unparsed': data}


class QueryStringParser(BaseParser):
    def parse(self, data):
        return parse_qs(data)


