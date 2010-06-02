"""
    State Agent
    
    MESSAGES IN:
    - "last_ts?"
    
    MESSAGES OUT:
    - "last_ts"

    @author: jldupont
    @date: May 27, 2010
"""
import gconf
import gobject

## locals
from synclastfm.system.bus import Bus


class StateAgent(gobject.GObject):  #@UndefinedVariable

    PATH="/apps/rhythmbox/synclastfm/%s"
    
    def __init__(self): 
        gobject.GObject.__init__(self) #@UndefinedVariable

        self.last_ts=0
        Bus.add_emission_hook("q_last_ts",     self.q_last_ts)
        Bus.add_emission_hook("track_updated", self.h_track_updated)

        self.gclient=gconf.client_get_default()

    def h_track_updated(self, _, track):
        """
        Adjust 'last_ts' information
        """
        try:    updated=long(track.details["updated"])
        except:
            print "Can't get 'updated' field!"
            return True
        
        if updated > self.last_ts:
            print "updated 'last_ts' to: %s" % updated
            self.gclient.set_int(self.PATH % "last_ts", updated)
            self.last_ts=updated
        
        return True

    def q_last_ts(self, *_):
        """
        Question: what is the "last timestamp" updated?
       
        Reset to a sensible default (0) on error
        """
        try:  value=long(self.gclient.get_int(self.PATH % "last_ts"))
        except:
            print "Expecting an integer 'last_ts' in gconf"
            self.gclient.set_int(self.PATH % "last_ts", 0)
            return True
        
        self.last_ts=value
        if self.last_ts is None:
            self.last_ts=0
            
        Bus.emit("last_ts", self.last_ts)
        return True
        

_=StateAgent()
