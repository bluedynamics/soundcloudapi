from restkit.globals import set_manager, get_manager
try:
    import eventlet
    eventlet.monkey_patch()
    from restkit.manager.meventlet import EventletManager
    set_manager(EventletManager(timeout=60))
except ImportError:
    from restkit import Manager
    set_manager(Manager(max_conn=10))

from soundcloudapi._api import (
    Users,
    Tracks,
    Playlists,
    Groups,
    Comments,
    Me,
    Apps,
    Resolve,
)

class Soundcloud(object):
    
    def __init__(self, authinfo):
        self.authinfo = authinfo
        
    def users(self, scid):
        """A SoundCloud user
        """
        return Users(self.authinfo, scid)

    def tracks(self, scid=None, filter=None):
        """A SoundCloud track
        """
        return Tracks(self.authinfo, userid=userid, filter=filter)
    
    def playlists(self, scid=None, filter=None):
        """A SoundCloud Set is internally called playlists due to some naming 
        restrictions.
        """
        return Playlists(self.authinfo, scid=scid, filter=filter)

    def groups(self, scid):
        """Groups have members and contributed tracks.
        """
        return Groups(self.authinfo, sc=scid, filter=filter)

    def comments(self, scid):
        """Comments can be made on tracks by any user who has access to a track, 
        except for non commentable tracks. As you see in the SoundCloud player 
        comments can also be associated with a specific timestamp in a track.
        """
        return Comments(self.authinfo, scid)
    
    def me(self):
        """ The /me resource allows you to get information about the 
        authenticated user and easily access his related subresources like 
        tracks, followings, followers, groups and so on.
        """
        return Me(self.authinfo)

    def apps(self, scid):
        """All tracks that are created and uploaded using a published app 
        include a created_with object which describes the app
        """
        return Apps(self.authinfo, scid)
    
    def resolve(self, url):
        """
        """
        return Resolve(self.authinfo, url)()