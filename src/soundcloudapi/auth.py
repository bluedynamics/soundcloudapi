# see http://developers.soundcloud.com/docs/api/authentication
# and http://tools.ietf.org/html/draft-ietf-oauth-v2-10
import urllib
import urlparse
import json
from restkit import request
from restkit.forms import BoundaryItem
from .exceptions import (
    SoundcloudException,
    SoundcloudUnauthorized,
)

URL_STEP1 = 'https://soundcloud.com/connect'
URL_STEP2 = 'https://api.soundcloud.com/oauth2/token'


class AuthInfo(object):
    
    def __init__(self, client_id, client_secret=None, redirect_uri=None, 
                 token=None, scope='non-expiring', popup=False):
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
        if self.popup:
            query['display'] = 'popup'
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
    
    
class BaseAuth(object):
    
    def __init__(self, authinfo, chooser='*'):
        """
        ``chooser`` 
           callable expecting filter and request as params and returns bool if
           this filter applies or not. 
           chooser='*' applies an always True callable.    
        ``authinfo`` an instance of soundcloudapi.auth.AuthInfo
        """
        if chooser == '*':
            self.chooser = lambda filter, request: True
        else:
            self.chooser = chooser
        self.authinfo = authinfo
                    
    def _check_path(self, request):
        return self.chooser(self, request)
    
    def on_request(self, request):
        raise NotImplementedError('Do not use abstract class')
    
    
class PrivateAuth(BaseAuth):
          
    def on_request(self, request):
        if not self._check_path(request):
            return
        if not self.authinfo.authenticated:
            raise SoundcloudUnauthorized('Theres no authorization token')                
        if request.method in ('PUT', 'POST'):
            authboundary = BoundaryItem('oauth_token', self.authinfo.token)
            request.body.boundaries.append(authboundary)
            request.body._clen = None # empty length cache
            request.headers['Content-Length'] = str(request.body.get_size())
        elif request.method in ('GET', 'DELETE'):
            request.headers['Authorization'] = 'OAuth %s' % self.authinfo.token
        else:
            raise SoundcloudException('HTTP method %s not supported' % 
                                      request.method)                            
        
class PublicAuth(BaseAuth):
          
    def on_request(self, request):
        if not self._check_path(request):
            return        
        if request.method in ('PUT', 'POST'):
            pass
        elif request.method in ('GET', 'DELETE'):
            parsed = request.parsed_url
            query = urlparse.parse_qs(parsed.query)
            query['client_id'] = self.authinfo.client_id
            request.url = urlparse.urlunparse((
                parsed.scheme, parsed.netloc, parsed.path, parsed.params, 
                urllib.urlencode(query, True), parsed.fragment))
        else:
            raise SoundcloudException('HTTP method %s not supported' % 
                                      request.method)                        