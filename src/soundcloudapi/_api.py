import json
import urllib
from restkit import Resource
from restkit.forms import multipart_form_encode 
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

def private_chooser(filter, request):
    return request.method.upper != 'GET' \
           or request.parsed_url.path.startswith('/me')    

def public_chooser(filter, request):
    return not private_chooser(filter, request)

def soundcloud_flat_dict(data):
    newdata = dict()
    for key in data:
        if not isinstance(data[key], dict):
            newdata[key] = data[key]
            continue
        for subkey in data[key]:
            newdata['%s[%s]' % (key, subkey)] = data[key][subkey]
    return newdata

class Base(object):

    def __init__(self, authinfo):
        self._baseuri = BASEURI
        self.authinfo = authinfo
        self._instance = None
        self._private_filter = PrivateAuth(authinfo, private_chooser)
        self._public_filter = PrivateAuth(authinfo, public_chooser)
        
    @property
    def _subpath(self):
        raise NotImplementedError('Abstract')
            
    @property
    def _uri(self):
        return '/'.join([self._baseuri, self._subpath])
    
    @property
    def _resource(self):                
        return Resource(self._uri, filters=[self._private_filter, 
                                            self._public_filter])

    def _check_response(self, response, errormsg, code=200):
        if response.status_int != code:
            raise SoundcloudException, '%s Status %i' % (errormsg, 
                                                     response.status_int)
            
    def _to_dict(self, resp):
        return json.loads(resp.body_string())
    
    def _get(self, path):
        resp = self._resource.get(path=path)
        self._check_response(resp, 'GET %s' % path)
        return self._to_dict(resp)
    
    def _delete(self, path):
        resp = self._resource.delete(path=path)
        self._check_response(resp, 'DELETE %s' % path)
        return self._to_dict(resp)
    
    def _prepare_payload(self, data):
        data = soundcloud_flat_dict(data)
        return multipart_form_encode(data, {},
            '----------ThIs_Is_tHe_bouNdaRY_f0r_ThE_$0uNdC10uD----------------')
    
    def _put(self, path, data):
        payload, headers = self._prepare_payload(data)
        resp = self._resource.put(path=path, headers=headers, payload=payload)
        self._check_response(resp, 'PUT %s with %s' % path, data)
        return self._to_dict(resp)
    
    def _post(self, path, data):
        payload, headers = self._prepare_payload(data)
        resp = self._resource.post(path=path, headers=headers, payload=payload)
        self._check_response(resp, 'POST %s with %s' % path, data)
        return self._to_dict(resp)
    
    def _subresource_dispatcher(self, subpath, scid=None, delete=False, 
                                data=None, metadata=None, 
                                allowed_methods=['GET']):
        path = '%s/%s/%s.json' % (self.id, subpath, scid)
        if delete:
            if 'DELETE' not in allowed_methods:
                 raise SoundcloudException('DELETE is not permitted.')
            # DELETE
            if scid is None:
                raise SoundcloudException('ID is missing for DELETE.')
            return self._delete(path)
        if metadata is None and data is None:
            # GET
            if 'GET' not in allowed_methods:
                raise SoundcloudException('GET is not permitted.')
            if scid is None:
                return self._get('%s/%s.json' % (self.id, subpath))
            return self._get(path)
        if metadata is not None and data is not None:
            raise SoundcloudException('Provide metadata or data, not both.')
        if metadata is not None:
            if 'PUT' not in allowed_methods:
                raise SoundcloudException('PUT is not permitted.')
            return self._put(path, data)
        if 'POST' not in allowed_methods:
            raise SoundcloudException('POST is not permitted.')
        return self._post(path, data)    
                            
class IdBase(Base):            

    def __init__(self, authinfo, scid):
        super(IdBase, self).__init__(authinfo)
        self.id = scid
    
            
class IdXorFilterBase(IdBase):

    def __init__(self, authinfo, scid=None, filter=None):
        if bool(scid) != bool(filter): # xor
            raise ValueError('user xor filter')
        super(IdOrFilterBase, self).__init__(authinfo, scid)
        self.task = scid and USERID or FILTER          
        self.filter = filter
                            
            
class Users(IdBase):
    
    _subpath = 'users'
    
    def __call__(self):
        return self._get('%s.json' % self.id)

    def tracks(self):
        return self._get('%s/tracks.json' % self.id)
    
    def playlists(self):
        return self._get('%s/playlists.json' % self.id)
    
    def followings(self, scid=None, delete=False, metadata=None):
        self._subresource_dispatcher('followings', scid=scid, delete=delete, 
                                data=None, metadata=metadata, 
                                allowed_methods=['GET', 'PUT', 'DELETE'])
    def followers(self, scid=None):
        self._subresource_dispatcher('followings', scid=scid)
    
    def comments(self):
        return self._get('%s/comments.json' % self.id)
    
    def favorites(self, scid=None, delete=False, metadata=None):
        self._subresource_dispatcher('favorites', scid=scid, delete=delete, 
                                data=None, metadata=metadata, 
                                allowed_methods=['GET', 'PUT', 'DELETE'])
    
    def groups(self):
        return self._get('%s/groups.json' % self.id)
    
           
class Tracks(IdXorFilterBase):

    _subpath = 'tracks/'

    def __call__(self, ):
        return self._get('%s.json' % self.id)
    


class Playlists(IdXorFilterBase):

    _subpath = 'playlists/'

class Groups(IdXorFilterBase):

    _subpath = 'groups/'


class Comments(IdBase):
    
    _subpath = 'comments'

class Me(Base):
    
    _subpath = 'me'                


class Apps(Base):
    
    _subpath = 'apps'                

class Resolve(Base):
    
    _subpath = 'resolve'                
            