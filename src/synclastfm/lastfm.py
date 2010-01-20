""" 
    LastFm related classes

    @author: jldupont
"""
import gobject

from bus import Bus
from rbloader import RbLoader
from sapi import Sapi
import rapi

__all__ = ["lfmagent"]

 
class LastFmAgent(gobject.GObject):
    def __init__(self, sapi):
        gobject.GObject.__init__(self)
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
        """
        print "LastFmAgent: on_playing_song_changed, username=%s, track=%s," % (self._lfmusername, str(track))
        self._sapi(callback=self._lastfm_response, 
                   method="track.getinfo", 
                   artist=track.details["artist"], 
                   track=track.details["track"],
                   username=self._lfmusername)
        return True #required for gobject

        
    def _lastfm_response(self, response):
        """
        Callback of "sapi" based call
        
        For now, only "track info" can end-up here
        """
        #print response
        try:
            track_info=rapi.processResponse(response)
            Bus.emit("user_track_info", track_info)
        except:
            Bus.emit("lastfm_request_failed")

gobject.type_register(LastFmAgent)


## Inits
## =====
loader=RbLoader()
sapi=Sapi("c02a90944e26d104c77e018bb6157456", loader)
lfmagent=LastFmAgent(sapi)

