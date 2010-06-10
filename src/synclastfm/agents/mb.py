"""
    Musicbrainz Agent
    
    Responsible for fetching the UUID associated with tracks
    from the Musicbrainz Proxy DBus application
    
    * The currently playing is examined for a "track mbid":
      if this UUID isn't found, try fetching it from MB Proxy
      
    
    MESSAGES IN:
    - "rb_shell"
    - "track?"
    - "ctrack"   (mainly from lastfm_proxy)
    
    
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
import dbus.service

from synclastfm.track import Track
from synclastfm.system.base import AgentThreadedBase

class DbusInterface(dbus.service.Object):
    """
    DBus interface - listening for signals from Musicbrainz Proxy DBus
    """
    PATH="/Tracks"
    
    def __init__(self, agent):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)
        self.agent=agent
        dbus.Bus().add_signal_receiver(self.sTracks, 
                               signal_name="Tracks", 
                               dbus_interface="com.jldupont.musicbrainz.proxy", 
                               bus_name=None, 
                               path="/Tracks")


    @dbus.service.signal(dbus_interface="com.jldupont.musicbrainz.proxy", signature="vvv")
    def qTrack(self, _ref, _artist_name, _track_name):
        """
        Signal Emitter - qTrack
        """
        

    def sTracks(self, source, ref, tracks):
        """
        Signal Receptor - Track
        
        Verify the "ref" parameter to make sure it is
        in reponse to a 'question' we asked
        """
        
        try:    
            rbstr, ukey=ref.split(":")
            rb=(rbstr=="rb")
        except:
            ## entirely possible that no unique key was
            ## used as reference in the query
            if ref=="rb":
                ukey=None
                rb=True

        ## we are not interested in response to requests of others
        if not rb:
            return
        
        ## Don't forget to add the 'ref' field back!
        for track_details in tracks:
            track=Track(track_details)
            self.agent.pub("mb_track", source, ukey, track)
            #print "mb_track: source(%s) ref(%s) - artist(%s) title(%s)" %  (source, ref, track.details["artist_name"], track.details["track_name"])
            
        self.agent.pub("musicbrainz_proxy_detected", True)
        self.agent.detected=True
        





class MBAgent(AgentThreadedBase):

    def __init__(self): 
        AgentThreadedBase.__init__(self)
        self.dbusif=DbusInterface(self)
        self.detected=False
        
    def h_tick_params(self, *_):
        """
        Kickstart
        """
        self.dbusif.qTrack("rb", "Depeche Mode", "Little 15")
        
    def hq_musicbrainz_proxy_detected(self):
        self.pub("musicbrainz_proxy_detected", self.detected)
        
    def hq_track(self, track):
        """
        Helps the track resolving functionality
        """
        self.h_ctrack(None, track)
        
    def h_ctrack(self, ukey, track):
        """
        'ctrack' message handler - from CacheTrack Agent
        
        if 'track_mbid' is already set, don't lookup with proxy.
        
        If 'track_mbid' isn't set, the message probably comes
        from 'lastfm_proxy agent' and thus a lookup should
        be performed.
        """
        #print "h_ctrack, ukey(%s)" % ukey
        
        try:    
            track_mbid= track.details["track_mbid"]
            if track_mbid is None:
                track_mbid= ""
        except: track_mbid= ""
            
        if len(track_mbid) < 36:
            self._loopkup(ukey, track)
        
              
    def _loopkup(self, ukey, track):
        """
        Sends the signal 'qTrack' over DBus to Musicbrainz-Proxy
        """
        try: 
            track_name= track.details["track_name"]
            artist_name=track.details["artist_name"]
            track_mbid= track.details["track_mbid"]
        except Exception, e:
            print "error retrieving track info: %s " % e
            return
        
        try:    l=len(str(track_mbid))
        except: l=0

        ## to account for the mess I might have put the database into...
        if l == 36:
            print "track_mbid already present: %s, %s" % (artist_name, track_name)
            return
        
        ## just in case some other agent(s) require our
        ## service but aren't needing a unique key for
        ## tracking their request
        if ukey is not None:
            ref="rb:%s" % str(ukey)
        else:
            ref="rb"
        
        ### Ask Musicbrainz Proxy for some more info
        self.dbusif.qTrack(ref, artist_name, track_name)


## Kick start the agent        
_=MBAgent()
_.start()
