"""
    User Agent
    
    @author: jldupont
"""
import gconf

## locals
from synclastfm.system.mbus import Bus

class LastFmUser(object):  #@UndefinedVariable
    """
    A Last.fm user proxy
    
    Currently, the user parameters are only retrieved 
    from Rhythmbox's Gnome configuration directory 
    """
    PATH="/apps/rhythmbox/audioscrobbler/%s"
    
    def __init__(self, username=None, password=None):
        self._username=username
        self._password=password
        
        Bus.subscribe("config?", self.hq_config)
        
    def _refresh(self):
        """
        Attempts to refresh the user information
        """
        client=gconf.client_get_default()
        self._username=client.get_string(self.PATH % "username")
        self._password=client.get_string(self.PATH % "password")
        self._announceChanges()

    def hq_config(self, *_):
        """
        Config?
        """
        self._refresh()
        self._announceChanges()
      
    def _announceChanges(self):
        Bus.publish(self, "lastfm_username_changed", self._username)
        Bus.publish(self, "lastfm_password_changed", self._password)

      
_=LastFmUser()

