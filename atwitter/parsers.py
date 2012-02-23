"""
Parse response
"""
import json

class BaseParser(object):
    def parse(self, data):
        raise NotImplementedError('You should define your parse(data)')


class NoopParser(BaseParser):
    def parse(self, data):
        return data


class JSONParser(BaseParser):
    def parse(self, data):
        try:
            return json.loads(data) if data else None
        except:
            return {'unparsed': data}

