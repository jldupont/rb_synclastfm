"""
    Lastfm Proxy DBus interface

    Processes:
    - "last_ts"
    - "lastfm_proxy_detected?"
    - "libwalker_done"
    
    Emits:
    - "track" (with 'lfid' field)
    - "q_last_ts"
    - "lastfm_proxy_detected"
    

    @author: jldupont
    @date: May 27, 2010
"""
import dbus.service
#import rhythmdb  #@UnresolvedImport

from synclastfm.system.base import AgentThreadedBase
from synclastfm.track import Track

        
   

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
         - "id"
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
    


class LastfmProxy(AgentThreadedBase):
    """
    Updates various properties
    """
    BATCH_SIZE=30
    
    STATES=["waiting", "complete", "partial"]
  
    def __init__(self, dbusif):
        AgentThreadedBase.__init__(self)
        self.dbusif=dbusif
        self.detected=False
        self.lastTs=0
        self.inProgress=False
        self.currentTs=0

    def h_timer_day(self, *_):
        """
        Each day, perform a complete sync
        
        This process is helpful because resolving [artist;track]
        to RB database entries can be fraught with problems i.e.
        it may take several iterations through Musicbrainz / RB
        to increase resolution accuracy to a workable level.
        """
        self.lastTs=0
        
    def h_timer_hour(self, *_):
        """
        Each hour, perform a partial sync
        """
        self._doProcess()
        
    def h_timer_minute(self, *_):
        """
        Each minute, send more records to process
        """
        ### see if something changed: if nothing changed,
        ### then that probably means we have nothing to
        ### do for the moment
        if self.currentTs == self.lastTs:
            return

        self._doProcess()
        
    def h_track(self, track, *_):
        """
        Extract the 'updated' field from the 'track' message.
        If it isn't present, then we have nothing to do with
        the message.  On the contrary, we update the 'last_ts'
        local tracker.
        """
        try:    updated=track["updated"]
        except: return
        
        self.lastTs = updated
        
    def h_lastfm_proxy_detected(self, detected):
        """
        Grab this status from the Dbus agent
        """
        self.detected=detected

    def hq_lastfm_proxy_detected(self, *_):
        """
        Respond to other agents e.g. Config 
        """
        self.pub("lastfm_proxy_detected", self.detected)
        
    def h_libwalker_done(self, *_):
        """
        Our trigger to start processing
        """
        self._doProcess()
        
    def _doProcess(self):
        print "asking for records, lastTs(%s)" % self.lastTs
        self.currentTs=self.lastTs
        self.dbusif.qRecords(self.lastTs, self.BATCH_SIZE)
        
        

_=LastfmProxy(dbusif)
_.start()
