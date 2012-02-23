"""
Based on twitty-twister but contains only functions that i need
and only generates HTTP requests with method, url, headers, data,
which later may be executed
"""

import oauth2
from urllib import urlencode

SIGNATURE_METHOD = oauth2.SignatureMethod_HMAC_SHA1()

BASE_URL="https://api.twitter.com/1"
SEARCH_URL="http://search.twitter.com/search.json"

class TwitterClientInfo(object):
    def __init__(self, name, version=None, url=None):
        self.name = name
        self.version = version
        self.url = url

    def headers(self):
        return dict((k, v) for k, v in [
                ('X-Twitter-Client', self.name),
                ('X-Twitter-Client-Version', self.version),
                ('X-Twitter-Client-URL', self.url)] if not v is None)

    def source(self):
        return self.name

class TwitterRequest(object):
    __slots__ = ['method', 'url', 'headers', 'data']

    def __init__(self, method, url, headers=None, data=None):
        self.method = method
        self.url = url
        self.headers = headers if headers else {}
        self.data = data

    def __str__(self):
        return "<%s>: %s %s\n%s\n%s" % (self.__class__.__name__, self.method, self.url,
                repr(self.headers), repr(self.data))


def ensure_utf8(x):
    return x.encode('utf-8') if isinstance(x, unicode) else x


class TwitterRequestFactory(object):
    agent="atwitter"

    def __init__(self, consumer, token, signature_method=SIGNATURE_METHOD,
            base_url=BASE_URL, search_url=SEARCH_URL, client_info = None):

        self.base_url = base_url
        self.search_url = search_url

        self.client_info = None

        self.rate_limit_limit = None
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

        self.consumer = consumer
        self.token = token
        self.signature_method = signature_method

        self.client_info = client_info

    def api_url(self, call):
        return self.base_url.rstrip('/') + '/' + call.lstrip('/')

    def oauth_header(self, method, url, parameters={}, header={}):
        oauth_request = oauth2.Request.from_consumer_and_token(self.consumer,
            token=self.token, http_method=method, http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.token)
        return dict((ensure_utf8(k), ensure_utf8(v)) for k, v in oauth_request.to_header().iteritems())

    def _urlencode(self, params):
        return urlencode([
                (unicode(k).encode('utf-8'), unicode(v).encode('utf-8')) for k, v in params.iteritems()])

    def get(self, call, params=None):
        url = self.api_url(call)
        return TwitterRequest('GET',
                url + '?' + self._urlencode(params) if params else url,
                self.oauth_header('GET', url, params or {}))

    def post(self, call, params, data=None):
        url = self.api_url(call)
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
        headers.update(self.oauth_header('POST', url, params))
        if self.client_info:
            headers.update(self.client_info.headers())
            params['source'] = self.client_info.source()
        return TwitterRequest('POST',
                url, headers, self._urlencode(params))

    def show_user(self, screen_name=None, user_id=None, include_entities=True):
        """
        Get the info for a specific user.
        Returns a delegate that will receive the user in a callback."""

        params = {}
        if user_id:
            params['user_id'] = user_id
        if screen_name:
            params['screen_name'] = screen_name
        if include_entities:
            params['include_entities'] = str(include_entities).lower()
        return self.get('/users/show.json', params)

    def rate_limit_status(self):
        return self.get('/account/rate_limit_status.json')

    def update(self, status, params={}):
        "Update your status.  Returns the ID of the new post."
        params = params.copy()
        params['status'] = status
        return self.post('/statuses/update.json', params)

