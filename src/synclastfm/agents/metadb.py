"""
    MetaDB Agent
    
    Responsible for storing associations of the form:
    [artist_name; track_name; track_mbid]
    
    @author: jldupont
    @date: Jun 1, 2010
"""
import os
import gobject
import sqlite3
import time

## locals
from synclastfm.system.bus import Bus


FIELDS=["id", "created", "updated", 
        "track_name",  "track_mbid",
        "artist_name"]

def makeTrackDict(track_tuple):
    if track_tuple is None:
        return {}
    dic={}
    index=0
    for el in track_tuple:
        key=FIELDS[index]
        dic[key]=el
        index += 1
    return dic


class MetaDBAgent(gobject.GObject):  #@UndefinedVariable

    PATH="~/rb_synclastfm.sqlite"
    
    def __init__(self): 
        gobject.GObject.__init__(self) #@UndefinedVariable

        self._path=os.path.expanduser(self.PATH)
        self.conn=sqlite3.connect(self._path, check_same_thread=False)
        self.c = self.conn.cursor()
        
        self.c.execute("""create table if not exists tracks (id integer primary key,
                            created integer,
                            updated integer,
                            track_name text,  track_mbid text,
                            artist_name text)
                        """)

        Bus.add_emission_hook("mb_track", self.h_mb_track)

    def h_mb_track(self, _, track):
        """
        Updates/Inserts a track in the database
        
        Used both forms associated with the track i.e.
        - the original [artist;track]: this information comes from either Lastfm or directly from RB
        - the musicbrainz's reference 
        """
        track_mbid=track.details.get("track_mbid", "")
        
        ## Filter out bad track_mbid... it can happen
        if track_mbid is None:
            return True
        
        if len(track_mbid) < 36:
            return True
                
        ## store based on the original request
        artist_name=unicode(track.details["artist_name"])
        track_name=unicode(track.details["track_name"])
        self._updateOrInsert(artist_name, track_name, track_mbid)
        
        ## store based on the musicbrainz's record
        mb_artist_name=unicode(track.details["mb_artist_name"])
        mb_track_name=unicode(track.details["mb_track_name"])
        
        if mb_artist_name != "" and mb_track_name != "":
            self._updateOrInsert(mb_artist_name, mb_track_name, track_mbid)       
        return True
        
    ## ========================================================= PRIVATE
    
    def _updateOrInsert(self, artist_name, track_name, track_mbid):
        """
        Updates the track OR inserts it
        """
        new=False
        now=time.time()        

        ## If we don't have a 'track_mbid', no use sticking around!
        if track_mbid is None:
            return True

        self.c.execute("""UPDATE tracks SET 
                        track_mbid=?,
                        updated=? 
                        WHERE artist_name=? AND track_name=?""", 
                        (track_mbid,
                         now,
                        artist_name, track_name,
                        ))
        
        if self.c.rowcount != 1:
            self.c.execute("""INSERT INTO tracks (created, updated,  
                            track_name, track_mbid,
                            artist_name
                            ) VALUES (?, ?, ?, ?, ?)""", 
                            (now, 0, 
                             track_name, track_mbid,
                            artist_name) )
            new=True
            
        if new:
            print "inserted: artist(%s) track(%s)" % (artist_name, track_name)
        else:
            print "updated: artist(%s) track(%s)" % (artist_name, track_name)
            
        self.conn.commit()
        return new
        
        
        
    def _findTrack(self, artist_name, track_name):
        """
        Locates a 'track'
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_name=? AND artist_name=?""", 
                           (unicode(track_name), unicode(artist_name)))
            track_tuple=self.c.fetchone()
        except:
            track_tuple=None
            
        track=makeTrackDict(track_tuple)
        return track

    def _findWithTrackMbid(self, track_mbid):
        """
        Attempts to locate an entry based on 
        a track's UUID
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_mbid=?""", 
                           (track_mbid))
            track_tuple=self.c.fetchone()
        except:
            track_tuple=None
            
        track=makeTrackDict(track_tuple)
        return track
        
        

_=MetaDBAgent()
