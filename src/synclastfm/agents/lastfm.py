""" 
    LastFm related classes

    @author: jldupont
"""
import gobject  #@UnresolvedImport

from synclastfm.system.bus import Bus
from synclastfm.system.rbloader import RbLoader

from synclastfm.sapi import Sapi
import synclastfm.rapi as rapi

__all__ = []


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
            #print "!! LastFmResponseCallback: user_track_info: " + str(track_info)            
        except Exception,e:
            print "LastFmResponseCallback: Exception: " + str(e)
            Bus.emit("lastfm_request_failed")
        


class LastFmResponseCallbackGeneric(object):
    """
    Generic Contextual callback 
    
    @param track: Track instance
    """
    def __init__(self, track):
        self.track=track

    def __call__(self, response):
        try:
            track_info=rapi.processResponse(response)
            self.track.lastfm_info=track_info
            Bus.emit("track_info", self.track)
            #print "!! LastFmResponseCallback: track_info: " + str(track_info)            
        except Exception,e:
            print "LastFmResponseCallback: Exception: " + str(e)
            Bus.emit("lastfm_request_failed")


 
class LastFmAgent(gobject.GObject):    #@UndefinedVariable
    def __init__(self, sapi):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._sapi = sapi
        self._lfmusername=""
        
        Bus.add_emission_hook("q_track_info",            self.hq_track_info)
        Bus.add_emission_hook("playing_song_changed",    self.on_playing_song_changed)
        Bus.add_emission_hook("lastfm_username_changed", self.on_lastfm_username_changed)
        
    def on_lastfm_username_changed(self, _signal, username):
        """
        GObject handler
        """        
        self._lfmusername=username
        return True #required for gobject
        
    def on_playing_song_changed(self, _signal, track):
        """
        GObject handler
        
        @param: an instance of the Track class
        """
        cb=LastFmResponseCallback(track)
        self._fetch(cb, track)
        return True #required for gobject


    def hq_track_info(self, _, track):
        """
        Attempts to pull more information on a track
        from Last.fm
        
        The track 'mbid' is what we are after mainly.
        """
        cb=LastFmResponseCallbackGeneric(track)
        self._fetch(cb, track)
            
    def _fetch(self, cb, track):
        
        self._sapi(callback=cb, 
                   method="track.getinfo", 
                   artist=track.details["artist"], 
                   track=track.details["track"],
                   username=self._lfmusername)
        
        


gobject.type_register(LastFmAgent) #@UndefinedVariable


## Inits
## =====
loader=RbLoader()
sapi=Sapi("c02a90944e26d104c77e018bb6157456", loader)
_=LastFmAgent(sapi)

