#!/usr/bin/env python

import sys
import oauth2
from twisted.web import client
from twisted.internet import reactor

from atwitter import twitterrq
from atwitter.adapters import adapter_twisted

consumer = oauth2.Consumer(sys.argv[1], sys.argv[2])
if len(sys.argv) > 3:
    token = oauth2.Token(sys.argv[3], sys.argv[4])
else:
    token = None
factory = twitterrq.TwitterRequestFactory(consumer, token)
agent = client.Agent(reactor)

def got(x):
    print 'Got', x

agent.request(*adapter_twisted.request(factory.rate_limit_status())).addCallback(
    adapter_twisted.response_callback()).addCallback(
    got).addBoth(lambda x: reactor.stop())

reactor.run()
