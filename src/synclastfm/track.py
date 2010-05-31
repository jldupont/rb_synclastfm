"""
    Track class
    @author: jldupont
"""

import gobject

class Track(gobject.GObject): #@UndefinedVariable
    """
    Last.fm Track proxy
    
    @param details: dictionary with the current playing track details
    @param entry: RB database entry corresponding to the current track
    @param lastfm_info: Info retrieved from Last.fm corresponding to the current track  
    """
    def __init__(self, details, entry=None, lastfm_info=None):
        gobject.GObject.__init__(self) #@UndefinedVariable

        self.details=details
        self.entry=entry
        self.lastfm_info=lastfm_info
