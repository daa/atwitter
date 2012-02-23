"""
Adapter of atwitter.twitterrq.TwitterRequest to twisted.web. machinery
"""

from zope.interface import implements
from twisted.web.http_headers import Headers
from twisted.web import iweb, error
from twisted.web.client import _parse, ResponseDone
from twisted.web.http import PotentialDataLoss, OK
from twisted.internet import protocol, defer


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


class TwitterResponseProtocol(protocol.Protocol):
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
                parsed = self.factory.parse(data)
                if self.response.code == OK:
                    self.deferred.callback(parsed)
                else:
                    self.deferred.errback(error.Error(self.response.code, response=parsed))
            except Exception, e:
                self.deferred.errback(e)
        else:
            self.deferred.errback(reason)


class ProtocolFactory(protocol.Factory):
    """
    Factory to build protocol which will receive data from response
    """
    protocol = TwitterResponseProtocol

    def __init__(self, parser=None):
        self.parser = parser

    def buildProtocol(self, response):
        p = self.protocol(response)
        p.factory = self
        return p

    def parse(self, data):
        return self.parser.parse(data) if self.parser else data


def response_callback(pf=ProtocolFactory()):
    def callback(response):
        p = pf.buildProtocol(response)
        response.deliverBody(p)
        return p.deferred
    return callback

