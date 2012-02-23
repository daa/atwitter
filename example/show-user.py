#!/usr/bin/env python

import sys
import oauth2
from twisted.web import client
from twisted.internet import reactor

from atwitter import twitterrq
from atwitter.adapters import twisted_adapter

consumer = oauth2.Consumer(sys.argv[1], sys.argv[2])
token = oauth2.Token(sys.argv[3], sys.argv[4])
factory = twitterrq.TwitterRequestFactory(consumer, token)
agent = client.Agent(reactor)

def got(x):
    print 'Got', x

agent.request(
    *twisted_adapter.request(factory.show_user(screen_name=sys.argv[5]))).addCallback(
    twisted_adapter.response_callback()).addCallback(
    got).addBoth(lambda x: reactor.stop())

reactor.run()

