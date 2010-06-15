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
import time
import dbus.service

from synclastfm.system.base import AgentThreadedBase
from synclastfm.track import Track
from synclastfm.system.mbus import Bus
        
   

class DbusInterface(dbus.service.Object):
    """
    DBus interface - listening for signals from Lastfm Proxy Dbus
    """
    PATH="/Records"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)
        dbus.Bus().add_signal_receiver(self.sRecordsLatest, 
                               signal_name="RecordsLatest", 
                               dbus_interface="com.jldupont.lastfm.proxy", 
                               bus_name=None, 
                               path="/Records")

    @dbus.service.signal(dbus_interface="com.jldupont.lastfm.proxy", signature="vv")
    def qRecordsLatest(self, ts, limit):
        """
        Signal Emitter - qRecords
        """

    def sRecordsLatest(self, records):
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

            #print "entry: artist(%s) track(%s) playcount(%s)" % (entry["artist_name"], entry["track_name"], entry["playcount"])
            track=Track(entry)
            Bus.publish(self.__class__, "track", track)

        Bus.publish(self.__class__, "lastfm_proxy_detected", True)
        
        

class LastfmProxy(AgentThreadedBase):
    """
    Updates various properties
    """
    BATCH_SIZE=60
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.dbusif=DbusInterface()
        self.detected=False
        
        self.canStart=False

        self.state=0
        
        self.ptrTs=time.time()
        self.lowestTs=None
        
        self.lday=None
        self.cday=0

    def h_timer_day(self, *_):
        """
        Each day, perform a complete sync
        
        This process is helpful because resolving [artist;track]
        to RB database entries can be fraught with problems i.e.
        it may take several iterations through Musicbrainz / RB
        to increase resolution accuracy to a workable level.
        """
        self.cday += 1
        
    def h_timer_minute(self, *_):
        """
        Each minute, send more records to process
        """
        #if not self.canStart:
        #    return
        
        #print "==> state: %s, ptrTs: %s lowestTs: %s" % (self.state, self.ptrTs, self.lowestTs)
        
        ## state 0: check if we can start a cycle
        if self.state==0:
            if self.lday is None:
                self.state=1
            if self.lday != self.cday:
                self.state=1
                self.lday=self.cday

        if self.state==1:
            print "starting!"
            self.ptrTs=time.time()
            self.lowestTs=None
            self._doProcess()
            self.state=2
            return

        if self.state==2:
            ## 1) we got nothing... maybe Lastfm-proxy-dbus
            ## isn't available... retry later
            ## 2) Or we have finished a cycle
            if self.lowestTs is None:
                print "finished!"
                self.state=0
            
            if self.lowestTs is not None:
                self.ptrTs=self.lowestTs
                self.lowestTs=None
                self._doProcess()
                
    
    def h_track(self, track, *_):
        """
        Intercept the 'track' message in order to grab the
        'updated' field
        """
        try: updated=track.details["updated"]
        except: updated=None
        if updated is None:
            return
        
        #print "(updated(%s))" % updated
        
        if self.lowestTs is None:
            self.lowestTs = updated
        if updated < self.lowestTs:
            self.lowestTs=updated
    
    
    ## ================================================================ TRIGGERS
    
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


            
    def h_libwalker_start(self, start):
        """
        If 'libwalking' isn't performed, then we can proceed
        """
        if start:
            self.canStart=True
        
    def h_libwalker_done(self, *_):
        """
        Our other trigger to start processing
        """
        self.canStart=True
        
        
    ## ================================================================ HELPERS
        
    def _doProcess(self):
        print "asking for records, ptrTs(%s)" % self.ptrTs
        self.dbusif.qRecordsLatest(self.ptrTs, self.BATCH_SIZE)
        
        

_=LastfmProxy()
_.start()
