"""
Adapter of atwitter.twitterrq.TwitterRequest to urllib2.Request
"""

from urllib2 import Request

def request(rq):
    return Request(rq.url, headers=rq.headers, data=rq.data)

