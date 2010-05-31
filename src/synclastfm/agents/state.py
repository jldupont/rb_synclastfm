"""
    State Agent
    
    MESSAGES IN:
    - "last_ts?"
    
    MESSAGES OUT:
    - "last_ts"

    @author: jldupont
    @date: May 27, 2010
"""
import gconf    #@UnresolvedImport
import gobject  #@UnresolvedImport

## locals
from synclastfm.system.bus import Bus


class StateAgent(gobject.GObject):  #@UndefinedVariable

    PATH="/apps/rhythmbox/synclastfm/%s"
    
    def __init__(self): 
        gobject.GObject.__init__(self) #@UndefinedVariable

        self.last_ts=0
        Bus.add_emission_hook("q_last_ts", self.q_last_ts)

    def q_last_ts(self, *_):
        """
        Question: what is the "last timestamp" updated?
       
        """
        client=gconf.client_get_default()
        self.last_ts=client.get_string(self.PATH % "last_ts")
        if self.last_ts is None:
            self.last_ts=0
            
        Bus.emit("last_ts", self.last_ts)
        

_=StateAgent()
