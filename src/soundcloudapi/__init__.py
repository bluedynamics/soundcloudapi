import _api
from .auth import AuthInfo
from .exceptions import SoundcloudException

class Soundcloud(object):
    
    def __init__(self, authinfo):
        self.authinfo = authinfo
        
    def users(self, scid=None, filter=None):
        """A SoundCloud user
        """
        return _api.Users(self.authinfo, scid=scid, filter=filter)    

    def tracks(self, scid=None, filter=None):
        """A SoundCloud track
        """
        return _api.Tracks(self.authinfo, scid=scid, filter=filter)
    
    def playlists(self, scid=None, filter=None):
        """A SoundCloud Set is internally called playlists due to some naming 
        restrictions.
        """
        return _api.Playlists(self.authinfo, scid=scid, filter=filter)

    def groups(self, scid):
        """Groups have members and contributed tracks.
        """
        return _api.Groups(self.authinfo, sc=scid, filter=filter)

    def comments(self, scid):
        """Comments can be made on tracks by any user who has access to a track, 
        except for non commentable tracks. As you see in the SoundCloud player 
        comments can also be associated with a specific timestamp in a track.
        """
        return _api.Comments(self.authinfo, scid)
    
    def me(self):
        """ The /me resource allows you to get information about the 
        authenticated user and easily access his related subresources like 
        tracks, followings, followers, groups and so on.
        """
        return _api.Me(self.authinfo)

    def apps(self, scid):
        """All tracks that are created and uploaded using a published app 
        include a created_with object which describes the app
        """
        return _api.Apps(self.authinfo, scid)
    
    def resolve(self, url):
        """The resolve resource allows you to lookup and access API resources 
        when you only know the SoundCloud.com URL
        """
        return _api.Resolve(self.authinfo)(url)