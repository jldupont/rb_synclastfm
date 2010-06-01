"""
    Finds an "entry" in the database

    MESSAGES IN:
    - "meta_track"
    - "track"
    
    MESSAGES OUT:
    - "track_entry"
    

    @author: jldupont
    @date: May 27, 2010
"""
import rhythmdb #@UnresolvedImport
import gobject

from synclastfm.system.bus import Bus


class TrackEntryWrapper(gobject.GObject):       #@UndefinedVariable
    def __init__(self, track_entry, db_entry): 
        gobject.GObject.__init__(self)          #@UndefinedVariable
        self.track_entry=track_entry
        self.db_entry=db_entry
        

class FinderAgent(gobject.GObject):  #@UndefinedVariable

    def __init__(self): 
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.db=None

        Bus.add_emission_hook("meta_track",   self.h_meta_track)
        Bus.add_emission_hook("rb_shell",     self.on_rb_shell)

    def on_rb_shell(self, _signal, rbobjects):
        """
        Grab RB objects references (shell, db, player)
        
        GObject handler
        """
        self._robjects=rbobjects
        self.db=self._robjects.db
        return True        
    

    def h_meta_track(self, _, track):
        """
        For each 'meta_track' received, try to find a corresponding
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
        Bus.emit("track_entry", te)
            
        return True
    

_=FinderAgent()
