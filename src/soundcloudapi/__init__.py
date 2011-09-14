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
    
    def __init__(self, configuration):
        self.configuration = configuration
        
    def users(self, scid):
        """A SoundCloud user
        """
        return Users(self.configuration, scid)

    def tracks(self, scid=None, filter=None):
        """A SoundCloud track
        """
        return Tracks(self.configuration, userid=userid, filter=filter)
    
    def playlists(self, scid=None, filter=None):
        """A SoundCloud Set is internally called playlists due to some naming 
        restrictions.
        """
        return Playlists(self.configuration, scid=scid, filter=filter)

    def groups(self, scid):
        """Groups have members and contributed tracks.
        """
        return Groups(self.configuration, sc=scid, filter=filter)

    def comments(self, scid):
        """Comments can be made on tracks by any user who has access to a track, 
        except for non commentable tracks. As you see in the SoundCloud player 
        comments can also be associated with a specific timestamp in a track.
        """
        return Comments(self.configuration, scid)
    
    def me(self):
        """ The /me resource allows you to get information about the 
        authenticated user and easily access his related subresources like 
        tracks, followings, followers, groups and so on.
        """

#/me
#/apps
#/resolve
