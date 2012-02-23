"""
Represent mapping between Twitter API error codes and responses to Exceptions
"""
_mapping = {}

class Meta(type):
    def __new__(mcs, name, bases, dict):
        c = type.__new__(mcs, name, bases, dict)
        s = dict['status']
        print 'meta', repr(s)
        if s is not None:
            _mapping[s] = c
        return c

class TwitterError(Exception):
    status = None
    __metaclass__ = Meta

    def __init__(self, message, response):
        self.message = message
        self.response = response

class RateLimitExceeded(TwitterError):
    status = 400

class Unauthorized(TwitterError):
    status = 401

class NotFound(TwitterError):
    status = 403

class NotAcceptable(TwitterError):
    status = 406

class StreamingRateLimitExceeded(TwitterError):
    status = 420

class InternalServerError(TwitterError):
    status = 500

class BadGateway(TwitterError):
    status = 502

class Unavailable(TwitterError):
    status = 503


def http2error(status, message, response=''):
    return _mapping[status](message, response) if status in _mapping else \
            TwitterError(status, message, response)

