"""
    Lastfm Proxy DBus interface

    Processes:
    - "last_ts"
    
    Emits:
    - "track" (with 'lfid' field)
    - "q_last_ts"
    - "lastfm_proxy_detected"
    

    @author: jldupont
    @date: May 27, 2010
"""
import dbus.service
#import rhythmdb  #@UnresolvedImport

import gobject
from synclastfm.system.bus import Bus
from synclastfm.track import Track

class Records(gobject.GObject):        #@UndefinedVariable
    """
    Basic wrapper for Records
    """
    def __init__(self, source_obj):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.obj=source_obj

        
   

class DbusInterface(dbus.service.Object):
    """
    DBus interface - listening for signals from Lastfm Proxy Dbus
    """
    PATH="/Records"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)

    @dbus.service.signal(dbus_interface="com.jldupont.lastfm.proxy", signature="vv")
    def qRecords(self, ts, limit):
        """
        Signal Emitter - qRecords
        """

    def sRecords(self, records):
        """
        Signal Receptor - Records
        
        Fields in each 'record':
         - "id"         --> lfid
         - "created"
         - "updated"
         - "playcount"
         - "track_name"
         - "track_mbid"
         - "artist_name"
         - "artist_mbid"
         - "album_name"
         - "album_mbid"      
        """
        for record in records:
            entry={}

            keys=record.keys()
            for key in keys:
                if key=="id":
                    ## Prepare a 'ref' field with some context:
                    ##  This is essential for processing the response signal
                    ##  ref:  lfid:'id':'playcount'
                    playcount=long(record["playcount"])
                    id=str(record["id"])
                    entry["lfid"]="%s:%s" % (id, playcount)
                else:
                    entry[str(key)]=record[str(key)]

            track=Track(entry)
            Bus.emit("track", track)
            
        Bus.emit("lastfm_proxy_detected", True)
        
        

dbusif=DbusInterface()
dbus.Bus().add_signal_receiver(dbusif.sRecords, 
                               signal_name="Records", 
                               dbus_interface="com.jldupont.lastfm.proxy", 
                               bus_name=None, 
                               path="/Records")
    


class LastfmProxy(gobject.GObject): #@UndefinedVariable
    """
    Updates various properties
    """
    FETCH_LIMIT=10
    
    def __init__(self, dbusif):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._shell=None
        self._db=None
        self._sp=None
        self._robjects=None
        self.dbusif=dbusif
        self.detected=False
        
        Bus.add_emission_hook("lastfm_proxy_detected",   self.h_lastfm_proxy_detected)
        Bus.add_emission_hook("lastfm_proxy_detected?",  self.hq_lastfm_proxy_detected)
        Bus.add_emission_hook("rb_shell",  self.on_rb_shell)
        Bus.add_emission_hook("last_ts",   self.h_last_ts)
        
    def h_lastfm_proxy_detected(self, _, state):
        self.detected=state
        
    def hq_lastfm_proxy_detected(self, *_):
        Bus.emit("lastfm_proxy_detected", self.detected)
        
    def on_rb_shell(self, _signal, rbobjects):
        """
        Grab RB objects references (shell, db, player)
        
        GObject handler
        """
        self._robjects=rbobjects
        self._db=self._robjects.db
        self._sp=self._robjects.player
        
        self._db.connect("load-complete", self.on_load_complete)
        self._sp.connect("playing-song-changed", self.on_playing_song_changed)
        return True
        
    def h_last_ts(self, _, ts):
        """
        Receive the "last_ts" message
        and asks for a "range" of records over DBus
        to Lastfm Proxy DBus
        """
        #print "last_ts: %s" % ts
        self.dbusif.qRecords(ts, self.FETCH_LIMIT)
        return True
            
        
    def on_playing_song_changed(self, *_):
        """
        We need to grab the latest "timestamp" we have
        so that we can ask for the correct "range" of records
        with LastfmSqlite
        """
        Bus.emit("q_last_ts")
        return True

        
        
    def on_load_complete(self, *_):
        """
        """
        Bus.emit("q_last_ts")
        return True

gobject.type_register(LastfmProxy) #@UndefinedVariable
_=LastfmProxy(dbusif)
