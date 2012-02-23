"""
Represent mapping between Twitter API error codes and responses to Exceptions
"""
_mapping = {}

class Meta(type):
    def __new__(mcs, name, bases, dict):
        c = type.__new__(mcs, name, bases, dict)
        print dict
        s = dict['status']
        print 'meta', name, repr(s)
        if s is not None:
            _mapping[s] = c
        return c

class BaseTwitterError(Exception):
    status = None
    __metaclass__ = Meta

    def __init__(self, message, response):
        self.message = message
        self.response = response

class TwitterError(BaseTwitterError):
    status = None

    def __init__(self, status, message, response):
        self.status = status
        self.message = message
        self.response = response

class RateLimitExceeded(BaseTwitterError):
    status = 400

class Unauthorized(BaseTwitterError):
    status = 401

class NotFound(BaseTwitterError):
    status = 403

class NotAcceptable(BaseTwitterError):
    status = 406

class StreamingRateLimitExceeded(BaseTwitterError):
    status = 420

class InternalServerError(BaseTwitterError):
    status = 500

class BadGateway(BaseTwitterError):
    status = 502

class Unavailable(BaseTwitterError):
    status = 503


def http2error(status, message, response=''):
    return _mapping[status](message, response) if status in _mapping else \
            TwitterError(status, message, response)

