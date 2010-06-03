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
    def __init__(self, details, entry=None, lastfm_info=None):
        self.details=details
        self.entry=entry
        self.lastfm_info=lastfm_info
