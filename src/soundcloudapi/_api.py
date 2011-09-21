# see https://twimg0-a.akamaihd.net/profile_background_images/25029373/http-headers-status.gif
import json
import urllib
from restkit import Resource
from restkit.errors import ResourceNotFound 
from restkit.forms import multipart_form_encode 
from restkit.datastructures import MultiDict 
from restkit.globals import set_manager, get_manager
try:
    import eventlet
    eventlet.monkey_patch()
    from restkit.manager.meventlet import EventletManager
    set_manager(EventletManager(timeout=60))
except ImportError:
    from restkit import Manager
    set_manager(Manager(max_conn=10))
from .exceptions import SoundcloudException
from .auth import (
    PublicAuth,
    PrivateAuth,
)

BASEURI = 'https://api.soundcloud.com'
FILTER = 'filter'
USERID = 'id'
BOUNDARY = '---==ThIs_Is_tHe_bouNdaRY_f0r_ThE_$0uNdC10uD==--'
SECRET_TOKEN_TPL = "%{stream_url}s?secret_token=%{secret_token}s&client_id="+\
                   "%{client_id}"                
ZEROPUT = {'Content-Length': '0'}
ACCEPT = {'Accept': 'application/json'}                    

def private_chooser(filter, request):
    return request.method.upper != 'GET' \
           or request.parsed_url.path.startswith('/me') \
           or 'secret-token.json' in request.parsed_url.path     

def public_chooser(filter, request):
    return not private_chooser(filter, request) \
           or 'secret-token.json' in request.parsed_url.path


def soundcloud_flat_dict(data, baseprefix):
    new = MultiDict()
    
    def _flattening(current, prefix):    
        if hasattr(current, 'items'): # some kind of dict
            for key, value in current.items():
                _flattening(value, '%s[%s]' % (prefix, key))
        elif hasattr(current, '__iter__'): # some kind of list
            for listvalue in current:
                _flattening(listvalue, '%s[]' % prefix)
        else:
            new.add(prefix, current)
            
    _flattening(data, baseprefix)
    return new

def prepare_payload(data, prefix):
    data = soundcloud_flat_dict(data, prefix)
    return multipart_form_encode(data, {}, BOUNDARY)
     

class Base(object):

    def __init__(self, authinfo):
        self._baseuri = BASEURI
        self.authinfo = authinfo
        self._instance = None
        self._private_filter = PrivateAuth(authinfo, private_chooser)
        self._public_filter = PublicAuth(authinfo, public_chooser)
        
    @property
    def _subpath(self):
        raise NotImplementedError('Abstract')
            
    @property
    def _uri(self):
        return '/'.join([self._baseuri, self._subpath])
    
    @property
    def _prefix(self):
        if self._subpath[-1] == 's':
            return self._subpath[:-1]
        raise NotImplementedError("If subpath does not end with 's' a special "
                                   "implementation is needed")
    
    @property
    def _resource(self):                
        return Resource(self._uri, filters=[self._private_filter, 
                                            self._public_filter])

    def _check_response(self, response, errormsg, codes=[200]):
        if response.status_int not in codes:
            raise SoundcloudException, '%s Status %i' % (errormsg, 
                                                     response.status_int)
            
    def _to_dict(self, resp):
        return json.loads(resp.body_string())
    
    def _get(self, path, data={}):
        try:
            resp = self._resource.get(path=path, params_dict=data, 
                                      headers=ACCEPT)
        except ResourceNotFound, e:
            return {'error': e.response.status, 'status': e.response.status_int}
        else:
            self._check_response(resp, 'GET %s' % path)
        return self._to_dict(resp)
    
    def _delete(self, path):
        resp = self._resource.delete(path=path, headers=ACCEPT)
        self._check_response(resp, 'DELETE %s' % path)
        return self._to_dict(resp)
    
    
    def _put(self, path, data):
        if data is ZEROPUT:
            payload, headers = '', ZEROPUT
        else:
            payload, headers = prepare_payload(data, self._prefix)
        headers.update(ACCEPT)
        resp = self._resource.put(path=path, headers=headers, payload=payload)
        self._check_response(resp, 'PUT %s with %s' % (path, data))
        return self._to_dict(resp)
    
    def _post(self, path, data):
        payload, headers = prepare_payload(data, self._prefix)
        headers.update(ACCEPT)
        resp = self._resource.post(path=path, headers=headers, payload=payload)
        self._check_response(resp, 'POST %s with %s' % (path, data))
        return self._to_dict(resp)
    
    def _subresource_dispatcher(self, 
                                subpath=None, 
                                scid=None, 
                                delete=False, 
                                postdata=None, 
                                putdata=None, 
                                getdata=None,
                                allowed_methods=['GET']):
        path = ''
        if hasattr(self, 'id') and self.id is not None:
            path += '/%s' % self.id
        if subpath is not None:
            path += '/%s'% subpath
        if scid is not None:
            path += '/%s' % scid
        path = path.lstrip('/')
        if delete:
            if 'DELETE' not in allowed_methods:
                 raise SoundcloudException('DELETE is not permitted.')
            if scid is None:
                raise SoundcloudException('ID is missing for DELETE.')
            return self._delete(path)
        if putdata is None and postdata is None:
            if 'GET' not in allowed_methods:
                raise SoundcloudException('GET is not permitted.')
            return self._get(path, data=getdata)
        if putdata is not None and postdata is not None:
            raise SoundcloudException('Provide putdata or postdata, not both.')
        if putdata is not None:
            if 'PUT' not in allowed_methods:
                raise SoundcloudException('PUT is not permitted.')
            return self._put(path, putdata)
        if 'POST' not in allowed_methods:
            raise SoundcloudException('POST is not permitted.')
        return self._post(path, postdata)    
                            
class IdBase(Base):            

    def __init__(self, authinfo, scid):
        super(IdBase, self).__init__(authinfo)
        self.id = scid
    
            
class IdFilterBase(IdBase):

    def __init__(self, authinfo, scid=None, filter=None):
        super(IdFilterBase, self).__init__(authinfo, scid)
        self.task = scid and USERID or FILTER          
        self.filter = filter
        
    def _subresource_dispatcher(self, 
                                subpath=None, 
                                scid=None, 
                                delete=False, 
                                postdata=None, 
                                putdata=None, 
                                getdata=None,
                                allowed_methods=['GET']):
        if not delete and putdata is None and postdata is None and self.filter:
            if getdata is None:
                getdata = dict()
            getdata.update(self.filter)            
        return super(IdFilterBase, self)._subresource_dispatcher(
            subpath, scid, delete, postdata, putdata, getdata, allowed_methods
        )
        
class IdXorFilterBase(IdBase):
        
    def __init__(self, authinfo, scid=None, filter=None):
        super(IdXorFilterBase, self).__init__(authinfo, scid, filter)
        if scid is not None != filter is not None:
             raise SoundcloudException('Filter or Id, not both.')

    def _subresource_dispatcher(self, 
                                subpath=None, 
                                scid=None, 
                                delete=False, 
                                postdata=None, 
                                putdata=None, 
                                getdata=None,
                                allowed_methods=['GET']):
        if self.filter is not None and subpath is not None:
            raise SoundcloudException('Filter or Id, not both.')
        return super(IdXorFilterBase, self)._subresource_dispatcher(
            subpath, scid, delete, postdata, putdata, getdata, allowed_methods
        )
        
        
class SharedToMixin(object):        

    def _shared_to(self, context, data, delete, replace):
        key = context=='email' and 'address' or 'id'
        params = MultiDict() 
        for value in data:
            params.add('%s[][%s]' % (context, key), value)
        return self._subresource_dispatcher(
            'shared-to/%s' % context, 
            scid=scid, 
            delete=delete, 
            postdata=replace and params or None, 
            putdata=not replace and params or None, 
            allowed_methods=['GET', 'DELETE',  'PUT', 'POST',]
        )

    def shared_to_users(self, userids=None, delete=False, replace=False):
        return self.__shared_to('users', userids, delete, replace)

    def shared_to_emails(self, emails=None, delete=False, replace=False):
        return self.__shared_to('emails', emails, delete, replace)
    
class UserMixin(object):    
                                    
    def __call__(self):
        return self._subresource_dispatcher()

    def tracks(self):
        return self._subresource_dispatcher('tracks')
    
    def playlists(self):
        return self._subresource_dispatcher('playlists')
    
    def followings(self, scid=None, delete=False, add=False):
        return self._subresource_dispatcher('followings', 
                                scid=scid, 
                                delete=delete, 
                                postdata=None, 
                                putdata=add and ZEROPUT or None, 
                                allowed_methods=['GET', 'PUT', 'DELETE'])

    def followers(self, scid=None):
        return self._subresource_dispatcher('followings', scid=scid)
    
    def comments(self):
        return self._subresource_dispatcher('comments')
    
    def favorites(self, scid=None, delete=False, add=False):
        return self._subresource_dispatcher('favorites', 
                                scid=scid, 
                                delete=delete, 
                                postdata=None, 
                                putdata=add and ZEROPUT or None, 
                                allowed_methods=['GET', 'PUT', 'DELETE'])
    
    def groups(self):
        return self._subresource_dispatcher('groups')
            
            
class Users(IdFilterBase, UserMixin):
    
    _subpath = 'users'

class Me(Base, UserMixin):
    
    _subpath = 'me'                

    @property
    def _prefix(self):
        return 'user'
    
    
class SecretTokenMixin(object):    

    def secret_token(self, token=None):
        # XXX for some reason this dont work at all. 
        if token is not None:
            raise NotImplementedError('PUT possible, but not implemented due '
                                      'to missing docs at soundcloud.')
        return self._subresource_dispatcher('secret-token')
        
    def secret_stream_url(self):
        data = self.secret_token()
        data['client_id'] = self.authinfo.client_id
        return SECRET_TOKEN_TPL % data
        
           
class Tracks(IdXorFilterBase, SharedToMixin, SecretTokenMixin):

    _subpath = 'tracks'

    def __call__(self, data=None):
        upload = data and self.id is None
        result = self._subresource_dispatcher(
                                putdata=not upload and data or None, 
                                postdata=upload and data or None, 
                                allowed_methods=['GET', 'PUT', 'POST'])
        if upload:
            self.id = result['id']
        return result
    
    def comments(self, scid=None, delete=False, data=None):
        return self._subresource_dispatcher('comments', 
                                scid=scid, 
                                delete=delete, 
                                postdata=None, 
                                putdata=data, 
                                allowed_methods=['GET', 'PUT', 'DELETE'])
        
    def favoriters(self, scid=None):
        return self._subresource_dispatcher('favoriters', scid=scid)


class Playlists(IdXorFilterBase, SharedToMixin, SecretTokenMixin):

    _subpath = 'playlists'


class Groups(IdXorFilterBase):

    _subpath = 'groups'


class Comments(IdBase):
    
    _subpath = 'comments'

    def __call__(self):
        return self._subresource_dispatcher()    

    
class Apps(IdBase):
    
    _subpath = 'apps'                

    def __call__(self):
        return self._subresource_dispatcher()

    def tracks(self):
        return self._subresource_dispatcher('tracks')        


class Resolve(Base):
    
    _subpath = 'resolve'                

    def __call__(self, url):
        return self._subresource_dispatcher()
            