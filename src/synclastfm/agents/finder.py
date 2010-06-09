"""
    Finds an "entry" in the database

    MESSAGES IN:
    - "ptrack"
    
    MESSAGES OUT:
    - "track_entry"
    - "track_updated"
    

    @author: jldupont
    @date: May 27, 2010
"""
import rhythmdb #@UnresolvedImport

from synclastfm.system.mbus import Bus


class TrackEntryWrapper(object):
    def __init__(self, track, db_entry): 
        self.track=track
        self.db_entry=db_entry
        

class FinderAgent(object):

    def __init__(self): 
        self.db=None

        Bus.subscribe(self.__class__, "ptracak",      self.h_ptrack)
        Bus.subscribe(self.__class__, "rb_shell",     self.on_rb_shell)

    def on_rb_shell(self, _shell, db, _sp):
        """
        Grab RB objects references (shell, db, player)
        """
        self.db=db
    

    def h_ptrack(self, _source, _ukey, track):
        """
        For each 'mb_track' received, try to find a corresponding
        rb db entry and issue a "track_entry" message.
        
        This should help 'Updater' to do its job.
        """
        artist_name= str(track.details["artist_name"])
        track_name = str(track.details["track_name"])
        
        #print "meta_track: %s" % track
        
        s1=(rhythmdb.QUERY_PROP_LIKE, rhythmdb.PROP_ARTIST, artist_name)
        s2=(rhythmdb.QUERY_PROP_LIKE, rhythmdb.PROP_TITLE, track_name)
        query = self.db.query_new()
        self.db.query_append(query, s1)
        self.db.query_append(query, s2)
        query_model = self.db.query_model_new_empty() 
        self.db.do_full_query_parsed(query_model, query)
        
        dbe=None
        for e in query_model:
            dbe=e[0]
            print "++ FOUND: artist(%s) track(%s)" % (artist_name, track_name)            
            break  ## not elegant but it works
            
        if dbe is None:
            print "-- NOT FOUND: artist(%s) track(%s)" % (artist_name, track_name)
            
        te=TrackEntryWrapper(track, dbe)
        Bus.publish(self.__class__, "track_entry", te, artist_name, track_name)
    

_=FinderAgent()
