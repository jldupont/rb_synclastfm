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
    
    ### make sure not to bust the cache
    ### as to not leave any space for other requests....
    JOBS_PERIOD=PERIOD*2

    ### cache id string
    CACHE_ID_STRING="dbid"

    def __init__(self):
        self.freq=0
        self.count=0
        self.db=None
        self.budget=self.JOBS_PERIOD
        self.last_db_mtime=0
        self.mb_detected=False
        self.song_entries=[]
        self.response_count=0
        
        Bus.subscribe(self.__class__, "tick",          self.h_tick)
        Bus.subscribe(self.__class__, "tick_params",   self.h_tick_params)
        Bus.subscribe(self.__class__, "rb_shell",      self.h_rb_shell)
        #Bus.subscribe(self.__class__, "last_db_mtime", self.h_last_db_mtime)
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

    def h_ptrack(self, key, _track):
        """
        Used in the self calibration loop
        """
        try:    strid, id=key.split("=")
        except:
            strid=None
            id=None

        ## not from us... no concern            
        if strid is None or strid!=self.CACHE_ID_STRING or id is None:
            return
        
        self.response_count += 1


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

    def h_tick(self, count):
        """
        'tick' timebase handler
        """
        
        ## not much we can do with Musicbrainz Proxy
        if not self.mb_detected:
            return
        
        l=len(self.song_entries)
        
        ## nothing more todo!
        if l==0:
            return
        
        ## not the time to issue requests
        if (count % self.freq)!=0:
            return
            
        jobs_todo=self.JOBS_PERIOD
        while jobs_todo:
            jobs_todo -= 1
            try:    id=self.song_entries.pop(0)
            except: id=None
            if id is None:
                break
            track=self.getTrackByDbId(id)
            
            key="%s=%s" % (self.CACHE_ID_STRING, id)
            Bus.publish(self.__class__, "track", track, key)
     
    ## ========================================================================= helpers
     
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

