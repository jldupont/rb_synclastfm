"""
    Musicbrainz Agent
    
    Responsible for fetching the UUID associated with tracks
    from the Musicbrainz Proxy DBus application
    
    * The currently playing is examined for a "track mbid":
      if this UUID isn't found, try fetching it from MB Proxy
      
    
    MESSAGES IN:
    
    
    MESSAGES OUT:
    - "musicbrainz_proxy_detected"
    

    @author: jldupont
    @date: May 31, 2010
"""
import gobject

from synclastfm.system.bus import Bus

class MBAgent(gobject.GObject):  #@UndefinedVariable

    def __init__(self): 
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.db=None

        Bus.add_emission_hook("entry",    self.h_entry)
        Bus.add_emission_hook("rb_shell", self.on_rb_shell)



## Kick start the agent
_=MBAgent()
