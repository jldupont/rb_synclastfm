"""
    Track Caching

    MESSAGES IN:
    - track
    - mb_track
    
    MESSAGES OUT:
    - ctrack : cached track i.e. contains unique 'ref' field
    - ptrack : original track fetched from the cache & merged with "mb_track" information
    

    @author: jldupont
    @date: Jun 4, 2010
"""
import copy

from synclastfm.system.base import AgentThreadedBase
from synclastfm.system.dtype import SimpleStore

class CacheTrackAgent(AgentThreadedBase):

    CACHE_ENTRIES=256

    def __init__(self): 
        AgentThreadedBase.__init__(self)
        self.ss=SimpleStore(size=self.CACHE_ENTRIES, destructive=False)

    def hq_track(self, track):
        """
        Keep the 'track' in cache
        
        Adds the 'ref' field to the track information and generates
        the 'ctrack' message
        
        When an "mb_track" comes back in, pull the original 'track':
        the said 'track' object contains the original contextual information
        """
        
        ukey=self.ss.store(track)
        self.pub("ctrack", ukey, track)

        
    def h_track(self, track):
        """
        Keep the 'track' in cache
        
        Adds the 'ref' field to the track information and generates
        the 'ctrack' message
        
        When an "mb_track" comes back in, pull the original 'track':
        the said 'track' object contains the original contextual information
        """
        ukey=self.ss.store(track)
        self.pub("ctrack", ukey, track)
        
        
    def h_mb_track(self, ukey, mb_track):
        """
        Pull the original 'track' from the cache
        based on the artist:track key
        
        We might be received multiple 'mb_track' messages based on 1
        original "track" message: it is due to the "lookup" process
        performed in the 'musicbrainz-proxy-dbus' where all [artist:track]
        matching the same 'track_mbid' will be returned.  This helps finding
        an entry in the RB database.
        """
        
        ## some agents might used the services of other agents without
        ## needing caching here.
        if ukey is None:
            return
        
        try:    otrack=self.ss.retrieve(ukey)
        except: 
            print "!! Unable to retrieve from cache: key(%s)" % ukey
            return
    
        ptrack=copy.deepcopy(mb_track)
        ptrack.merge(otrack)
        
        self.pub("ptrack", ptrack)

        
            

_=CacheTrackAgent()
_.start()
