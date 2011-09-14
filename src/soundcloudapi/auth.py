# see http://developers.soundcloud.com/docs/api/authentication
# and http://tools.ietf.org/html/draft-ietf-oauth-v2-10
import re
import urlparse
import json
from restkit import request
from .exceptions import (
    SoundcloudException,
    SoundcloudUnauthorized,
)

URL_STEP1 = 'https://soundcloud.com/connect'
URL_STEP2 = 'https://api.soundcloud.com/oauth2/token'

class AuthInfo(object):
    
    def __init__(self, client_id, client_secret, redirect_uri, token=None,
                 scope='non-expiring', popup=False):
        self.client_id = client_id    
        self.client_secret = client_secret   
        self.redirect_uri = redirect_uri
        self.token = token
        self.scope = scope
        self.popup = popup
        
    @property
    def authenticated(self):
        return self.token is not None
        
    @property
    def _base_params(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        }
        return params
        
    @property
    def redirect_url(self):
        """Step 1"""
        query = self._base_params 
        query['response_type'] = 'code'
        query['scope'] = self.scope
        query = '&'.join(['%s=%s' % (_, query[_]) for _ in sorted(query)])
        return '%s?%s' % (URL_STEP1, query)
    
    def _step2_body(self, code):
        body = self._base_params 
        body['grant_type'] = 'authorization_code'
        body['code'] = code
        body = '&'.join(['%s=%s' % (_, body[_]) for _ in sorted(body)])
        return body
        
    def token_from_code(self, code):
        """Step 2"""
        headers = dict()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        resp = request(URL_STEP2, 'POST', body=self._step2_body(code), 
                       headers=headers)
        body = resp.body_string()
        result = json.loads(body)
        if u'error' in result:
            raise SoundcloudException(result[u'error'])
        # XXX Error handling is missing
        self.token = result[u'access_token']
        return self.token
    
class AuthFilter(object):
    
    def __init__(self, path, authinfo):
        if path.endswith('*'):
            self.match = re.compile("%s.*" % path.rsplit('*', 1)[0])
        else:
            self.match = re.compile("%s$" % path)
        self.authinfo = authinfo
                    
    def on_path(self, request):
        path = request.parsed_url.path or "/"
        return (self.match.match(path) is not None)
    
    def on_request(self, request):
        if not self.on_path(request):
            return
        private = request.parsed_url.path.startswith('/me')
        if private and self.authinfo.authorized:
            request.headers['Authorization'] = 'OAuth %s' % self.authinfo.token
            return
        elif private and not self.authinfo.authorized:
            raise SoundcloudUnauthorized('Theres no authorization token')
        # for non private only append client_id
        if request.method in ('PUT', 'POST'):
            pass
        elif request.method in ('GET', 'DELETE'):
            pass
        else:
            raise SoundcloudException('HTTP method %s not supported' % 
                                      request.method)                        