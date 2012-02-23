"""
Adapter of atwitter.twitterrq.TwitterRequest to twisted.web. machinery
"""

from zope.interface import implements
from twisted.web.http_headers import Headers
from twisted.web import iweb, error
from twisted.web.client import _parse, ResponseDone
from twisted.web.http import PotentialDataLoss, OK
from twisted.internet import protocol, defer

from atwitter import error as terror


class StringProducer(object):
    implements(iweb.IBodyProducer)

    def __init__(self, data):
        self.data = data
        self.length = len(data)

    def startProducing(self, consumer):
        consumer.write(self.data)
        return defer.succeed(True)

    def stopProducing(self):
        pass

    def pauseProducing(self):
        pass
    
    def resumeProducing(self):
        pass


def request(rq):
    headers = Headers(dict((k, [v]) for k, v in rq.headers.iteritems()))
    scheme, host, port, path = _parse(rq.url)
    headers.setRawHeaders('Host', [host])
    return (rq.method, rq.url,
            headers,
            StringProducer(rq.data) if rq.data else None)


class ResponseProtocol(protocol.Protocol):
    def __init__(self, response):
        self.response = response
        self.deferred = defer.Deferred()
        self._buffer = []

    def dataReceived(self, data):
        self._buffer.append(data)

    def connectionLost(self, reason):
        if reason.check(ResponseDone, PotentialDataLoss):
            data = ''.join(self._buffer)
            try:
                if self.response.code == OK:
                    self.deferred.callback(self.factory.callback_result(data, self.response))
                else:
                    self.deferred.errback(self.factory.errback_result(error.Error(self.response.code, response=data), self.response))
            except Exception, e:
                self.deferred.errback(e)
        else:
            self.deferred.errback(self.factory.errback_result(reason, response))


class ProtocolFactory(protocol.Factory):
    """
    Factory to build protocol which will receive data from response
    """
    protocol = ResponseProtocol

    def __init__(self, parser=None):
        self.parser = parser

    def buildProtocol(self, response):
        p = self.protocol(response)
        p.factory = self
        return p

    def parse(self, data):
        return self.parser.parse(data) if self.parser else data

    def errback_result(self, e, response):
        if isinstance(e, error.Error):
            e = terror.http2error(e.status, e.message, self.parse(e.response))
        return e

    def callback_result(self, data, response):
        return self.parse(data)


def response_callback(pf=ProtocolFactory()):
    def callback(response):
        p = pf.buildProtocol(response)
        response.deliverBody(p)
        return p.deferred
    return callback

