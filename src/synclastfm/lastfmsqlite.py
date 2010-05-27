"""
    @author: jldupont
    @date: May 27, 2010
"""
import dbus.service
#import rhythmdb  #@UnresolvedImport

import gobject #@UnresolvedImport
from bus import Bus

class DbusInterface(dbus.service.Object):
    """
    """
    PATH="/Records"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)

    @dbus.service.signal(dbus_interface="com.jldupont.lastfmsqlite", signature="vv")
    def qRecords(self, ts, limit):
        """
        """

    def sRecords(self, records):
        """
        """
        print "Records: %s" % str(records)
        

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
    def __init__(self, dbusif):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._shell=None
        self._db=None
        self._sp=None
        self._robjects=None
        self.dbusif=dbusif
        
        Bus.add_emission_hook("rb_shell",        self.on_rb_shell)
        
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
        
    def on_playing_song_changed(self, *_):
        self.dbusif.qRecords(0, 100)
        
        
    def on_load_complete(self, *_):
        """
        """
        print "LastfmSqlite.on_load_complete"
        self.dbusif.qRecords(0, 100)


gobject.type_register(LastfmSqlite) #@UndefinedVariable
_=LastfmSqlite(dbusif)
