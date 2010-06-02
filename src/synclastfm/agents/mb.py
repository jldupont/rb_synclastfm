"""
    Musicbrainz Agent
    
    Responsible for fetching the UUID associated with tracks
    from the Musicbrainz Proxy DBus application
    
    * The currently playing is examined for a "track mbid":
      if this UUID isn't found, try fetching it from MB Proxy
      
    
    MESSAGES IN:
    - "rb_shell"
    - "track?"
    - "track"   (mainly from lastfm_proxy)
    
    
    MESSAGES OUT:
    - "musicbrainz_proxy_detected"
    - "mb_track"
    
    Fields returned by Musicbrainz Proxy:
     - "artist_name"
     - "track_name"
     - "artist_mbid"
     - "track_mbid"
     - "mb_artist_name"
     - "mb_track_name"
    
    @author: jldupont
    @date: May 31, 2010
"""
import gobject
import dbus.service


from synclastfm.system.bus import Bus
from synclastfm.track import Track

class MBEntry(gobject.GObject): #@UndefinedVariable
    def __init__(self, source, rbid, details):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.source=str(source)
        self.rbid=int(rbid)
        self.details=details
        

class DbusInterface(dbus.service.Object):
    """
    DBus interface - listening for signals from Musicbrainz Proxy DBus
    """
    PATH="/Tracks"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)

    @dbus.service.signal(dbus_interface="com.jldupont.musicbrainz.proxy", signature="vvv")
    def qTrack(self, ref, artist_name, track_name):
        """
        Signal Emitter - qTrack
        """

    def sTracks(self, _source, ref, tracks):
        """
        Signal Receptor - Track
        """
        #print "sTrack: source(%s), ref(%s)" % (source, ref)
        
        ## Make sure it is a signal that answers a question we asked
        ##  in the first place
        try:    pieces=ref.split(":")
        except: pieces=None
        
        ## most probably not ours.
        if pieces is None:
            return
        
        try:    idstr=str(pieces[0])
        except: idstr=None

        try:    id=long(pieces[1])
        except: id=None
               
        ## Yep, not ours.
        if idstr!="rbid" and idstr!="lfid":
            return
        
        if id is None:
            return
        
        ## Don't forget to add the 'ref' field back!
        for track_details in tracks:
            track=Track(track_details)
            track.details[idstr]=ref
            
            #print "mb_track: source(%s) ref(%s) - artist(%s) title(%s)" %  (_source, ref, track.details["artist_name"], track.details["track_name"])
                    
            Bus.emit("mb_track", track)
            
        Bus.emit("musicbrainz_proxy_detected", True)
        
        

dbusif=DbusInterface()
dbus.Bus().add_signal_receiver(dbusif.sTracks, 
                               signal_name="Tracks", 
                               dbus_interface="com.jldupont.musicbrainz.proxy", 
                               bus_name=None, 
                               path="/Tracks")



class MBAgent(gobject.GObject):  #@UndefinedVariable

    def __init__(self, dbusif): 
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.dbusif=dbusif
        self.detected=False
        
        #Bus.add_emission_hook("rb_shell", self.on_rb_shell)
        Bus.add_emission_hook("track?",                  self.hq_track)
        Bus.add_emission_hook("track",                   self.h_track)
        Bus.add_emission_hook("playing_song_changed",    self.on_playing_song_changed)
        Bus.add_emission_hook("musicbrainz_proxy_detected", self.h_musicbrainz_proxy_detected)
        Bus.add_emission_hook("musicbrainz_proxy_detected?", self.hq_musicbrainz_proxy_detected)
        

    def h_musicbrainz_proxy_detected(self, _, state):
        self.detected=state

    def hq_musicbrainz_proxy_detected(self, *_):
        Bus.emit("musicbrainz_proxy_detected",self.detected)

    def on_playing_song_changed(self, _, track):
        """
        Event from RB
        """
        self._loopkup(track)
        return True
       
    def h_track(self, _, track):
        """
        if 'track_mbid' is already set, don't lookup with proxy.
        
        If 'track_mbid' isn't set, the message probably comes
        from 'lastfm_proxy agent' and thus a lookup should
        be performed.
        """
        try:    
            track_mbid= track.details["track_mbid"]
            if track_mbid is None:
                track_mbid= ""
        except: track_mbid= ""
            
        if len(track_mbid) < 36:
            self._loopkup(track)

        return True
        
                
    def hq_track(self, _, track):
        """
        See if we need to lookup the track's mbid
        """
        try:    track_mbid= track.details["track_mbid"]
        except: track_mbid= ""
            
        if len(track_mbid) < 36:
            self._loopkup(track)
            
        return True
        
    def _loopkup(self, track):
        """
        """
        #print "_lookup: track: %s " % track
        try:    reqid="rbid:%s" % track.details["rbid"]
        except:
            try:
                reqid="lfid:%s" % track.details["lfid"]
            except:
                print "invalid id! Expecting 'rbid' or 'lfid'"
                return
        
        try: 
            track_name= track.details["track_name"]
            artist_name=track.details["artist_name"]
            track_mbid= track.details["track_mbid"]
        except Exception, e:
            print "error retrieving track info: %s " % e
            return True
        
        try:    l=len(str(track_mbid))
        except: l=0

        ## to account for the mess I might have put the database into...
        if l == 36:
            print "track_mbid already present: %s, %s" % (artist_name, track_name)
            return True
        
        ### Ask Musicbrainz Proxy for some more info
        self.dbusif.qTrack(reqid, artist_name, track_name)
        
        return True
        

## Kick start the agent
_=MBAgent(dbusif)
