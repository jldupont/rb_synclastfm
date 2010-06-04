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
import dbus.service

from synclastfm.track import Track
#from synclastfm.system.dtype import SimpleStore

from synclastfm.system.base import AgentThreadedBase

class DbusInterface(dbus.service.Object):
    """
    DBus interface - listening for signals from Musicbrainz Proxy DBus
    """
    PATH="/Tracks"
    CACHE_ENTRIES=256
    
    
    def __init__(self, agent):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)
        self.agent=agent
        dbus.Bus().add_signal_receiver(self.sTracks, 
                               signal_name="Tracks", 
                               dbus_interface="com.jldupont.musicbrainz.proxy", 
                               bus_name=None, 
                               path="/Tracks")


    @dbus.service.signal(dbus_interface="com.jldupont.musicbrainz.proxy", signature="vvv")
    def qTrack(self, ref, artist_name, track_name):
        """
        Signal Emitter - qTrack
        """

    def sTracks(self, _source, ref, tracks):
        """
        Signal Receptor - Track
        
        Verify the "ref" parameter to make sure it is
        in reponse to a 'question' we asked
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
        if idstr!="rb":
            return
        
        if id is None:
            return
        
        ## Don't forget to add the 'ref' field back!
        for track_details in tracks:
            track=Track(track_details)
            track.details[idstr]=ref
            
            #print "mb_track: source(%s) ref(%s) - artist(%s) title(%s)" %  (_source, ref, track.details["artist_name"], track.details["track_name"])
                    
            self.agent.pub("mb_track", track)
            
        self.agent.pub("musicbrainz_proxy_detected", True)
        
        





class MBAgent(AgentThreadedBase):  #@UndefinedVariable

    def __init__(self): 
        AgentThreadedBase.__init__(self)
        
        self.dbusif=DbusInterface(self)
        self.detected=False
        
    def h_musicbrainz_proxy_detected(self, state):
        self.detected=state

    def hq_musicbrainz_proxy_detected(self, *_):
        Bus.emit("musicbrainz_proxy_detected",self.detected)

    def h_track(self, track):
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
        
                
    def hq_track(self, track):
        """
        See if we need to lookup the track's mbid
        """
        print "mb.hq_track"
        
        try:    track_mbid= str( track.details["track_mbid"] )
        except: track_mbid= ""
            
        if len(track_mbid) < 36:
            self._loopkup(track)
            
        return True
        
    def _loopkup(self, track):
        """
        Sends the signal 'qTrack' over DBus to Musicbrainz-Proxy
        
        
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
_=MBAgent()
_.start()
