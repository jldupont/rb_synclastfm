"""
    Helpers

    @author: jldupont
"""
import rhythmdb #@UnresolvedImport


class EntryHelper(object):
    """
    Helper functions for song database entries
    """
    props = {   "artist_name": rhythmdb.PROP_ARTIST
                ,"album_name": rhythmdb.PROP_ALBUM
                ,"duration":   rhythmdb.PROP_DURATION
                ,"track_name": rhythmdb.PROP_TITLE
                ,"track_mbid": rhythmdb.PROP_MUSICBRAINZ_TRACKID
                ,"duration":   rhythmdb.PROP_DURATION
                ,"playcount":  rhythmdb.PROP_PLAY_COUNT
                ,"rating":     rhythmdb.PROP_RATING
                ,"rbid":       rhythmdb.PROP_ENTRY_ID
             }
    
    @classmethod
    def track_details(cls, shell, entry):
        """
        Retrieves details associated with a db entry
        
        @return: (artist, title)
        """
        db = shell.props.db
        result={}
        try:
            for prop, key in cls.props.iteritems():
                result[prop]=db.entry_get(entry, key)
        except:
            pass
        return result
   
    @classmethod
    def track_details2(cls, db, entry):
        """
        Retrieves details associated with a db entry
        
        @return: (artist, title)
        """
        result={}
        try:
            for prop, key in cls.props.iteritems():
                result[prop]=db.entry_get(entry, key)
        except:
            pass
        return result
