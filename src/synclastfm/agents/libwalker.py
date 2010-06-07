"""
    LibWalker Agent
    
    Responsible for traversing the RB database
    This function helps the [artist;track_name] resolution process
    throughout the system.
    
    Features:
    - Rate limited / self calibrating
    
    Messages In:
    - "rb_shell"
    - "tick"
    - "last_db_mtime"
    - "track?"
    
    Messages Out:
    - "ctrack"
    - "last_db_mtime?"
    
    
    @author: jldupont
    @date: Jun 4, 2010
"""
import rhythmdb #@UnresolvedImport
from synclastfm.system.mbus import Bus

class LibWalker(object):

    ### in seconds
    PERIOD=360
    JOBS_PERIOD=PERIOD*1.5

    def __init__(self):
        self.freq=0
        self.count=0
        self.db=None
        self.budget=0
        self.last_db_mtime=0
        self.mb_detected=False
        
        Bus.subscribe(self.__class__, "tick",          self.h_tick)
        Bus.subscribe(self.__class__, "rb_shell",      self.h_rb_shell)
        Bus.subscribe(self.__class__, "last_db_mtime", self.h_last_db_mtime)
        Bus.subscribe(self.__class__, "musicbrainz_proxy_detected", self.h_musicbrainz_proxy_detected)

        Bus.publish(self.__class__, "last_db_mtime?")

    def h_musicbrainz_proxy_detected(self, state):
        """
        Musicbrainz Proxy DBus
        
        No use running this agent if the MB proxy
        isn't available
        """
        self.mb_detected=state

    def hq_track(self, *_):
        """
        Used in the self calibration loop
        """
        self.budget -= 1


    def h_last_db_mtime(self, value):
        self.last_db_mtime=value

    def h_rb_shell(self, _shell, db, _sp):
        """
        Grab RB objects references (shell, db, player)
        """
        self.db=db

    def h_tick(self, freq, count):
        """
        """
        self.freq=freq
        self.count=count
     
    def getTracks(self, mtime):
        """
        Retrieves a group of db_entry based on PROP_MTIME
        i.e. last modified time
        """
        ## a bit too fast maybe...
        ## this might be paranoia anyhow...
        if self.db is None:
            return None
        
        s=(rhythmdb.QUERY_PROP_GREATER, rhythmdb.PROP_MTIME, mtime)
        query = self.db.query_new()
        self.db.query_append(query, s)
        query_model = self.db.query_model_new_empty() 
        self.db.do_full_query_parsed(query_model, query)
        return query_model
     

_=LibWalker()

