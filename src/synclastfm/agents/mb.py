"""
    Musicbrainz Agent
    
    Responsible for fetching the UUID associated with tracks
    from the Musicbrainz Proxy DBus application
    
    * The currently playing is examined for a "track mbid":
      if this UUID isn't found, try fetching it from MB Proxy
      
    
    MESSAGES IN:
    - "rb_shell"
    
    
    MESSAGES OUT:
    - "musicbrainz_proxy_detected"
    - "mb_entry"
    

    @author: jldupont
    @date: May 31, 2010
"""
import gobject
import dbus.service


from synclastfm.system.bus import Bus

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

    def sTrack(self, source, ref, track_details):
        """
        Signal Receptor - Track
        """
        print "mb.sTrack: source(%s), ref(%s)" % (source, ref)
        
        ## Make sure it is a signal that answers a question we asked
        ##  in the first place
        try:
            rb_id_str, rb_entryid =ref.split(":")
            if rb_id_str != "rbid":
                return
        except:
            return

        Bus.emit("mb_entry", MBEntry(source, rb_entryid, track_details))
            
        Bus.emit("musicbrainz_proxy_detected", True)
        
        

dbusif=DbusInterface()
dbus.Bus().add_signal_receiver(dbusif.sTrack, 
                               signal_name="Track", 
                               dbus_interface="com.jldupont.musicbrainz.proxy", 
                               bus_name=None, 
                               path="/Tracks")



class MBAgent(gobject.GObject):  #@UndefinedVariable

    def __init__(self, dbusif): 
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.dbusif=dbusif

        #Bus.add_emission_hook("entry",    self.h_entry)
        #Bus.add_emission_hook("rb_shell", self.on_rb_shell)

        Bus.add_emission_hook("playing_song_changed",    self.on_playing_song_changed)
        
    def on_playing_song_changed(self, _, track):
        """
        Trigger for updating some database tracks
        """
        #print "mb.on_playing_song_changed: track: %s " % track
        try: 
            track_name= track.details["track"]
            artist_name=track.details["artist"]
            track_mbid= track.details["track_mbid"]
            rbid=track.details["rbid"]
        except Exception, e:
            print "mb.on_playing_song_changed: error retrieving track info: %s " % e
            return True
        
        try:    l=len(str(track_mbid))
        except: l=0

        if l != 0:
            print "mb.on_playing_song_changed: track_mbid already present: %s, %s" % (artist_name, track_name)
            return True
        
        ref="rbid:%s" % rbid
        self.dbusif.qTrack(ref, artist_name, track_name)
        
        return True
        

## Kick start the agent
_=MBAgent(dbusif)
