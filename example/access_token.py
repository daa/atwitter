#!/usr/bin/env python

import urllib2
import oauth2

from atwitter import twitterrq
from atwitter.adapters import urllib2_adapter

if __name__ == '__main__':
    import sys
    consumer = oauth2.Consumer(sys.argv[1], sys.argv[2])
    token = oauth2.Token(sys.argv[3], sys.argv[4])
    f = twitterrq.TwitterRequestFactory(consumer, token)
    trq = f.access_token(sys.argv[5])
    urq = urllib2_adapter.request(trq)
    try:
        r = urllib2.urlopen(urq)
        print r.read()
    except urllib2.HTTPError, e:
        print e
        print e.info()
        print e.read()

