"""
    Track class
    @author: jldupont
"""
class Track(object):
    """
    Last.fm Track proxy
    
    @param details: dictionary with the current playing track details
    @param entry: RB database entry corresponding to the current track
    @param lastfm_info: Info retrieved from Last.fm corresponding to the current track  
    
    details:
    ========
    
    "track_name"
    "artist_name"
    "album_name"
    "rbid":        Rhythmdb entry ID
    "track_mbid":  track's Musicbrainz UUID
    "artist_mbid": artist's Musicbrainz UUID
    """
    def __init__(self, details, entry=None, lastfm_info={}):
        self.details=details
        self.lastfm_info=lastfm_info
        
        ## RB database entry
        self.entry=entry

    def merge(self, track):
        """
        Merges the information from another 'track' object in this one
        
        The other object's fields have higher priority than this one's
        """
        self.details.update(track.details)
        self.lastfm_info.update(track.lastfm_info)

    def mergeSpecial(self, track):
        artist_name=self.details["artist_name"]
        track_name=self.details["track_name"]
        self.details.update(track.details)
        self.lastfm_info.update(track.lastfm_info)
        self.details["artist_name"]=artist_name
        self.details["track_name"]=track_name
        