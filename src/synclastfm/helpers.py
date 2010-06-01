"""
    Helpers

    @author: jldupont
"""
import gobject

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
   

class WrapperGObject(gobject.GObject): #@UndefinedVariable
    """
    Wrapper for non-gobject objects
    """
    def __init__(self, **kw):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.__dict__.update(kw)

gobject.type_register(WrapperGObject) #@UndefinedVariable


## ===================================================== TESTS

if __name__=="__main__":
    w2=WrapperGObject(key1="value1", key2="value2")
    print w2.__dict__

