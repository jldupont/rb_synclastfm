""" 
    LastFm related classes

    @author: jldupont
"""
import gobject  #@UnresolvedImport

from bus import Bus
from rbloader import RbLoader
from sapi import Sapi
import rapi

__all__ = ["lfmagent"]


class LastFmResponseCallback(object):
    """
    Contextual callback - holds a reference 
    to a Track object instance
    
    @param track: Track instance
    """
    def __init__(self, track):
        self.track=track

    def __call__(self, response):
        try:
            track_info=rapi.processResponse(response)
            self.track.lastfm_info=track_info
            Bus.emit("user_track_info", self.track)
            #print "!! LastFmResponseCallback: track_info: " + str(track_info)            
        except Exception,e:
            print "LastFmResponseCallback: Exception: " + str(e)
            Bus.emit("lastfm_request_failed")
        
        
 
class LastFmAgent(gobject.GObject):    #@UndefinedVariable
    def __init__(self, sapi):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._sapi = sapi
        self._lfmusername=""
        Bus.add_emission_hook("playing_song_changed",    self.on_playing_song_changed)
        Bus.add_emission_hook("lastfm_username_changed", self.on_lastfm_username_changed)
        
    def on_lastfm_username_changed(self, _signal, username):
        """
        GObject handler
        """        
        self._lfmusername=username
        print "LastFmAgent: username=%s" % username
        return True #required for gobject
        
    def on_playing_song_changed(self, _signal, track):
        """
        GObject handler
        
        @param: an instance of the Track class
        """
        #print "LastFmAgent: on_playing_song_changed, username=%s, track=%s," % (self._lfmusername, str(track))
        cb=LastFmResponseCallback(track)
        self._sapi(callback=cb, 
                   method="track.getinfo", 
                   artist=track.details["artist"], 
                   track=track.details["track"],
                   username=self._lfmusername)
        return True #required for gobject


gobject.type_register(LastFmAgent) #@UndefinedVariable


## Inits
## =====
loader=RbLoader()
sapi=Sapi("c02a90944e26d104c77e018bb6157456", loader)
lfmagent=LastFmAgent(sapi)

