"""
    Track class
    @author: jldupont
"""

import gobject

class Track(gobject.GObject):
    """
    Last.fm Track proxy
    """
    def __init__(self, details):
        gobject.GObject.__init__(self)
        self.details=details
        
    
    
