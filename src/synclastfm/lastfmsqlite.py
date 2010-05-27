"""
    LastfmSqlite DBus interface
    
    Emits:
    - "entry"
    - "lastfmsqlite_detected"
    

    @author: jldupont
    @date: May 27, 2010
"""
import dbus.service
#import rhythmdb  #@UnresolvedImport

import gobject #@UnresolvedImport
from bus import Bus


class Records(gobject.GObject):        #@UndefinedVariable
    """
    Basic wrapper for Records
    """
    def __init__(self, source_obj):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.obj=source_obj

        
class TrackEntry(gobject.GObject):     #@UndefinedVariable
    def __init__(self):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.props={}
        
    def __setitem__(self, key, value):
        self.props[key]=value
        
    def __getitem__(self, key):
        return self.props.get(key, None)
    
    def keys(self):
        return self.props.keys()

    

class DbusInterface(dbus.service.Object):
    """
    DBus interface - listening for signals from LastfmSqlite
    """
    PATH="/Records"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)

    @dbus.service.signal(dbus_interface="com.jldupont.lastfmsqlite", signature="vv")
    def qRecords(self, ts, limit):
        """
        Signal Emitter - qRecords
        """

    def sRecords(self, records):
        """
        Signal Receptor - Records
        """
        for record in records:
            entry=TrackEntry()

            keys=record.keys()
            for key in keys:
                entry[str(key)]=record[str(key)]

            Bus.emit("entry", entry)
            
        Bus.emit("lastfmsqlite_detected", True)
        
        

dbusif=DbusInterface()
dbus.Bus().add_signal_receiver(dbusif.sRecords, 
                               signal_name="Records", 
                               dbus_interface="com.jldupont.lastfmsqlite", 
                               bus_name=None, 
                               path="/Records")
    


class LastfmSqlite(gobject.GObject): #@UndefinedVariable
    """
    Updates various properties
    """
    FETCH_LIMIT=100
    
    def __init__(self, dbusif):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._shell=None
        self._db=None
        self._sp=None
        self._robjects=None
        self.dbusif=dbusif
        
        Bus.add_emission_hook("rb_shell",  self.on_rb_shell)
        Bus.add_emission_hook("last_ts",   self.h_last_ts)
        
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
        to LastfmSqlite
        """
        self.dbusif.qRecords(ts, self.FETCH_LIMIT)
                
        
    def on_playing_song_changed(self, *_):
        """
        We need to grab the latest "timestamp" we have
        so that we can ask for the correct "range" of records
        with LastfmSqlite
        """
        Bus.emit("q_last_ts")

        
        
    def on_load_complete(self, *_):
        """
        """
        Bus.emit("q_last_ts")


gobject.type_register(LastfmSqlite) #@UndefinedVariable
_=LastfmSqlite(dbusif)
