"""
    LibWalker Agent
    
    Responsible for traversing the RB database
    This function helps the [artist;track_name] resolution process
    throughout the system.
    
    Features:
    - Rate limited
    
    Messages In:
    - "song_entries"
    - "entry_added"
    - "rb_shell"
    - "tick"
    - "last_db_mtime"
    - "ptrack"
    - "musicbrainz_proxy_detected"
    
    Messages Out:
    - "ctrack"
    - "last_db_mtime?"
    
    
    @author: jldupont
    @date: Jun 4, 2010
"""
from synclastfm.system.mbus import Bus
from synclastfm.track import Track
from synclastfm.helpers import EntryHelper

class LibWalker(object):

    ### in seconds
    PERIOD=1
    
    ### cache id string
    CACHE_ID_STRING="dbid"

    ### maximum number of jobs per period
    JOBS_PERIOD_MAX=100
    
    ### integration period
    INTEG_PERIOD=5
    
    ### mode switch threshold
    MODE_THRESHOLD=0.75
    
    MODE_LOW  = 0
    MODE_HIGH = 1

    JOBS_PARAMS = { MODE_LOW:  PERIOD*1
                   ,MODE_HIGH: PERIOD*100 }

    def __init__(self):
        self.freq=0
        self.count=0
        self.db=None
        self.last_db_mtime=0
        self.mb_detected=False
        self.song_entries=[]
        
        ## Integration
        self.icount=0
        self.mode = self.MODE_LOW
        
        ## stats
        self.jobs=0
        self.hits=0
        self.responses=0
        
        Bus.subscribe(self.__class__, "tick",          self.h_tick)
        Bus.subscribe(self.__class__, "tick_params",   self.h_tick_params)
        Bus.subscribe(self.__class__, "rb_shell",      self.h_rb_shell)
        Bus.subscribe(self.__class__, "mb_track",      self.h_mb_track)
        Bus.subscribe(self.__class__, "entry_added",   self.h_entry_added)
        Bus.subscribe(self.__class__, "song_entries",  self.h_song_entries)
        Bus.subscribe(self.__class__, "musicbrainz_proxy_detected", self.h_musicbrainz_proxy_detected)

        #Bus.publish(self.__class__, "last_db_mtime?")

    ## ========================================================================= handlers

    def h_entry_added(self, id, _entry):
        self.song_entries.append(id)

    def h_song_entries(self, entries):
        self.song_entries=entries

    def h_musicbrainz_proxy_detected(self, state):
        """
        Musicbrainz Proxy DBus
        
        No use running this agent if the MB proxy
        isn't available
        """
        self.mb_detected=state

    def h_mb_track(self, source, key, _track):
        """
        Used in the self calibration loop
        """

        try:    strid, id=key.split("=")
        except:
            strid=None
            id=None

        #print "mb_track: source(%s) key(%s) idstr(%s) id(%s)" % (source, key, strid, id)
        
        ## not from us... no concern            
        if strid!=self.CACHE_ID_STRING:
            return
        
        self.responses += 1

        if source=="cache":
            self.hits += 1

    #def h_last_db_mtime(self, value):
    #    self.last_db_mtime=value

    def h_rb_shell(self, _shell, db, _sp):
        """
        Grab RB objects references (shell, db, player)
        """
        self.db=db

    def h_tick_params(self, freq):
        """
        Grab 'tick' parameters
        """
        self.freq=freq
        self.ticount=freq*self.INTEG_PERIOD

    def h_tick(self, count):
        """
        'tick' timebase handler
        """
        
        ## not much we can do with Musicbrainz Proxy
        if not self.mb_detected:
            return
        
        self._doIntegration(count)
        
        
        l=len(self.song_entries)
        
        ## nothing more todo!
        if l==0:
            return
        
        ## not the time to issue requests
        if (count % self.freq)!=0:
            return
            
        jobs_todo=self.JOBS_PARAMS[self.mode]
        #print "jobs_todo(%s)" % jobs_todo

        while jobs_todo:
            self.jobs += 1
            jobs_todo -= 1
            try:    id=self.song_entries.pop(0)
            except: id=None
            if id is None:
                break
            track=self.getTrackByDbId(id)
            
            key="%s=%s" % (self.CACHE_ID_STRING, id)
            Bus.publish(self.__class__, "track", track, False, key)
     
    ## ========================================================================= helpers
     
    def _doIntegration(self, _count):
        """
        Manages the stats integration activity
        
        This functionality analyzes the received responses in order
        to determine which 'mode' of operation to adopt i.e.
        - "slow" or "high"
        """
        self.icount += 1
        if self.icount < self.ticount:
            return
        
        try:    ratio= float(self.hits) / float(self.responses)
        except: ratio= 0.0
     
        crossing = ratio > self.MODE_THRESHOLD
        #print "hits(%s) responses(%s) ratio(%s) crossing(%s)" % (self.hits, self.responses, ratio, crossing)

        ## reset
        self.icount = 0
        self.jobs   = 0
        self.hits   = 0
        self.responses = 0
          
        if self.mode == self.MODE_LOW:
            if crossing:
                print "libwalker: switching to MODE_HIGH"
                self.mode = self.MODE_HIGH
        else:
            if not crossing:
                print "libwalker: switching to MODE_LOW"
                self.mode = self.MODE_LOW


     
    def getTrackByDbId(self, id):
        """
        Forms a Track object based on an RB db entry id
        """
        entry=self.getEntryById(id)
        details=EntryHelper.track_details2(self.db, entry)
        track=Track(details)
        return track
        
     
    def getEntryById(self, id):
        """
        Retrieves an db entry by id
        """
        return self.db.entry_lookup_by_id(id)
     

_=LibWalker()

