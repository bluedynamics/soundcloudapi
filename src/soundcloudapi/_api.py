import restkit

BASEURI = 'http://api.soundcloud.com/'
BASEURI_SSL = 'https://api.soundcloud.com/'

FILTER = 'filter'
USERID = 'id'

class Base(object):

    def __init__(self, configuration):
        self._baseuri = BASEURI
        self.configuration = configuration
        self._instance = None
        
    @property
    def _subpath(self):
        raise NotImplementedError('Abstract')
            
    @property
    def _uri(self):
        return '/'.join([self._baseuri, self._subpath])
    
    @property
    def _resource(self):                
        oauth = restkit.oauth.OAuthFilter('*', consumer)
        return restkit.Resource(self._uri, )

    def _check_response(self, response, exception_class, errormsg, code=200):
        if response.status_int != code:
            raise exception_class, '%s Status %i' % (errormsg, 
                                                     response.status_int)
            
class AuthBase(Base):
    
    def __init__(self, configuration, scid):
        super(AuthBase, self).__init__(configuration)
        self._baseuri = BASEURI
        self.id = scid
        
    @property
    def is_authenticated(self):
        self.configuration.token is not None
        
    def authenticator(self, configuration):
        pass
                
            
class IdBase(Base):            

    def __init__(self, configuration, scid):
        super(IdBase, self).__init__(configuration)
        self.id = scid
            
class IdXorFilterBase(IdBase):

    def __init__(self, configuration, scid=None, filter=None):
        if bool(scid) != bool(filter): # xor
            raise ValueError('user xor filter')
        super(IdOrFilterBase, self).__init__(configuration, scid)
        self.task = scid and USERID or FILTER          
        self.filter = filter                
            
class Users(IdBase):
    
    _subpath = 'users'

        
class Tracks(IdXorFilterBase):

    _subpath = 'tracks'


class Playlists(IdXorFilterBase):

    _subpath = 'playlists'

class Groups(IdXorFilterBase):

    _subpath = 'groups'


class Comments(IdBase):
    
    _subpath = 'comments'

class Me(Base):
    
    _subpath = 'me'                


class Apps(Base):
    
    _subpath = 'apps'                

class Resolve(Base):
    
    _subpath = 'resolve'                
            