""" 
    LastFm related classes

    @author: jldupont
"""
from synclastfm.system.mbus import Bus
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
            Bus.publish(self, "user_track_info", self.track)
            #print ">> user_track_info: " + str(track_info)            
        except Exception,e:
            print "LastFmResponseCallback: Exception: " + str(e)
            Bus.publish(self, "lastfm_request_failed")
        


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
            Bus.publish(self, "track_info", self.track)
            #print "track_info: " + str(track_info)            
        except Exception,e:
            print "LastFmResponseCallback: Exception: " + str(e)
            Bus.publish(self, "lastfm_request_failed")


 
class LastFmAgent(object):
    def __init__(self, sapi):
        self._sapi = sapi
        self._lfmusername=""
        
        ##Bus.add_emission_hook("q_track_info",            self.hq_track_info)
        Bus.subscribe("track?",                  self.hq_track)
        Bus.subscribe("lastfm_username_changed", self.on_lastfm_username_changed)
        
    def on_lastfm_username_changed(self, username):
        """
        GObject handler
        """        
        self._lfmusername=username
        return True #required for gobject
        
    def hq_track(self, track):
        """
        GObject handler
        
        @param: an instance of the Track class
        """
        cb=LastFmResponseCallback(track)
        self._fetch(cb, track)
        return True #required for gobject


    #def hq_track_info(self, _, track):
        """
        Attempts to pull more information on a track
        from Last.fm
        
        The track 'mbid' is what we are after mainly.
        """
        #cb=LastFmResponseCallbackGeneric(track)
        #self._fetch(cb, track)
            
    def _fetch(self, cb, track):
        
        self._sapi(callback=cb, 
                   method="track.getinfo", 
                   artist=track.details["artist_name"], 
                   track=track.details["track_name"],
                   username=self._lfmusername)
        
        


## Inits
## =====
loader=RbLoader()
sapi=Sapi("c02a90944e26d104c77e018bb6157456", loader)
_=LastFmAgent(sapi)

