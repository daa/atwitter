"""
Based on twitty-twister but contains only functions that i need
and only generates HTTP requests with method, url, headers, data,
which later may be executed
"""

import oauth2
import base64
from urllib import urlencode

from .util import ensure_utf8, encode_multipart


SIGNATURE_METHOD = oauth2.SignatureMethod_HMAC_SHA1()

BASE_URL = 'https://api.twitter.com/1'
UPLOAD_URL = 'https://upload.twitter.com/1'
SEARCH_URL = 'http://search.twitter.com/search.json'

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


class TwitterRequestFactory(object):
    agent = "atwitter"

    def __init__(self, consumer, token, signature_method=SIGNATURE_METHOD,
            base_url=BASE_URL, search_url=SEARCH_URL, upload_url=UPLOAD_URL,
            client_info = None):

        self.base_url = base_url
        self.upload_url = upload_url
        self.search_url = search_url

        self.client_info = None

        self.rate_limit_limit = None
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

        self.consumer = consumer
        self.token = token
        self.signature_method = signature_method

        self.client_info = client_info

    def api_url(self, call, base_url=None):
        return (self.base_url if base_url is None else base_url).rstrip('/') + '/' + call.lstrip('/')

    def user_agent_header(self):
        return {'User-Agent': self.agent} if self.agent else {}

    def oauth_header(self, method, url, parameters={}):
        oauth_request = oauth2.Request.from_consumer_and_token(self.consumer,
            token=self.token, http_method=method, http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.token)
        return dict((ensure_utf8(k), ensure_utf8(v)) for k, v in oauth_request.to_header().iteritems())

    def _urlencode(self, params):
        return urlencode([
                (unicode(k).encode('utf-8'), unicode(v).encode('utf-8')) for k, v in params.iteritems()])

    def get(self, call, params=None):
        url = self.api_url(call)
        headers = self.user_agent_header()
        headers.update(self.oauth_header('GET', url, params or {}))
        return TwitterRequest('GET',
                url + '?' + self._urlencode(params) if params else url,
                headers)

    def post(self, call, params, data=None):
        url = self.api_url(call)
        if headers is None:
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
        headers.update(self.user_agent_header())
        headers.update(self.oauth_header('POST', url, params))
        if self.client_info:
            headers.update(self.client_info.headers())
            params['source'] = self.client_info.source()
        return TwitterRequest('POST',
                url, headers, self._urlencode(params))

    def post_multipart(self, call, params={}, files=(), base_url=None):
        url = self.api_url(call, base_url)
        boundary, body = encode_multipart(params.items(), files)
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
        headers.update(self.user_agent_header())
        headers.update(self.oauth_header('POST', url))
        if self.client_info:
            headers.update(self.client_info.headers())
            params['source'] = self.client_info.source()
        return TwitterRequest('POST', url, headers, body)

    def configuration(self):
        return self.get('/help/configuration.json')

    def show_user(self, screen_name=None, user_id=None, include_entities=True):
        """
        Get the info for a specific user.
        """
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
        """
        Update your status.
        """
        params = params.copy()
        params['status'] = status
        return self.post('/statuses/update.json', params)

    def update_with_media(self, status, media, **kw):
        """
        Updates the authenticating user's status and attaches media for upload.
        """
        kw['status'] = status
        return self.post_multipart('/statuses/update_with_media.json', kw, [('media[]', f, v) for f, v in media],
            base_url=self.upload_url)

    def update_profile_image(self, image, image_filename, include_entities=None, skip_status=None):
        params = {}
        if include_entities is not None:
            params['include_entities'] = str(include_entities).lower()
        if skip_status is not None:
            params['skip_status'] = str(skip_status).lower()
        return self.post_multipart('/account/update_profile_image.json', params,
            [('image', image_filename, image)])

