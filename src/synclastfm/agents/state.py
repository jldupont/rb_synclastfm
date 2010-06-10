"""
    State Agent
    
    Maintains state information in the gnome configuration registry
    
    MESSAGES IN:
    - "last_db_mtime?"
    - "last_db_mtime"
    - "track_updated"
    - "last_ts?"
    
    MESSAGES OUT:
    - "last_ts"
    - "last_db_mtime"

    @author: jldupont
    @date: May 27, 2010
"""
import gconf

## locals
from synclastfm.system.mbus import Bus


class StateAgent(object):  #@UndefinedVariable

    PATH="/apps/rhythmbox/synclastfm/%s"
    
    def __init__(self): 

        self.last_ts=0
        #Bus.subscribe(self.__class__, "q_last_ts",     self.q_last_ts)
        #Bus.subscribe(self.__class__, "track_updated", self.h_track_updated)
        
        Bus.subscribe(self.__class__, "last_libwalk?",  self.hq_last_libwalk)
        Bus.subscribe(self.__class__, "libwalker_done", self.h_libwalker_done)

        self.gclient=gconf.client_get_default()

    def hq_last_libwalk(self, *_):
        try:    value=self.gclient.get_int(self.PATH % "last_libwalk")
        except: value=0
        Bus.publish(self.__class__, "last_libwalk", value)

    def h_libwalker_done(self, ts):
        try:    value=self.gclient.set_int(self.PATH % "last_libwalk", ts)
        except: 
            print "Can't update 'last_libwalk' config"


    def hq_last_db_mtime(self, *_):
        try:    value=self.gclient.get_int(self.PATH % "last_db_mtime")
        except: value=0
        Bus.publish(self.__class__, "last_db_mtime", value)

    def h_last_db_mtime(self, value):
        try:    self.gclient.set_int(self.PATH % "last_db_mtime", value)
        except: 
            print "Can't update the 'last_db_mtime' field!"

    def h_track_updated(self,track):
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
            
        Bus.publish(self.__class__, "last_ts", self.last_ts)
        return True
        

_=StateAgent()
