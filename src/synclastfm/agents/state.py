"""
    State Agent
    
    Maintains state information in the gnome configuration registry
    
    MESSAGES IN:
    - "last_libwalk?"
    - "state?"
    - "state"    
    
    MESSAGES OUT:
    - "state"
    - "libwalker_done"


    @author: jldupont
    @date: May 27, 2010
"""
import gconf

if __name__!="__main__":
    from synclastfm.system.mbus import Bus

class StateManager(object):
    
    PATH="/apps/rhythmbox/synclastfm/%s"
        
    def __init__(self):
        self.gclient=gconf.client_get_default()
        
    def save(self, key, value):
        if isinstance(value, int):
            self.gclient.set_int(self.PATH % key, value)
        elif isinstance(value, float):
            self.gclient.set_float(self.PATH % key, value)
        else:
            self.gclient.set_string(self.PATH % key, str(value))
    
    def retrieve(self, key):
        try:    
            value=self.gclient.get_int(self.PATH % key)
        except:
            value=None
            try:
                value=self.gclient.get_string(self.PATH % key)
            except:
                value=self.gclient.get_float(self.PATH % key)
        return value
    
if __name__!="__main__":
    class StateAgent(object):  #@UndefinedVariable
    
        def __init__(self): 
    
            Bus.subscribe(self.__class__, "state?",        self.hq_state)
            Bus.subscribe(self.__class__, "state",         self.h_state)
            
            Bus.subscribe(self.__class__, "last_libwalk?",  self.hq_last_libwalk)
            Bus.subscribe(self.__class__, "libwalker_done", self.h_libwalker_done)
    
            self.sm=StateManager()
    
        def hq_last_libwalk(self, *_):
            value=self.sm.retrieve("last_libwalk")
            Bus.publish(self.__class__, "last_libwalk", value)
    
        def h_libwalker_done(self, ts):
            self.sm.save("last_libwalk", ts)
    
        def h_state(self, key, value):
            """
            Saves a 'state' in gconf
            """
            self.sm.save(key, value)
    
        def hq_state(self, key):
            value=self.sm.retrieve(key)
            Bus.publish(self.__class__, "state", key, value)

    
    _=StateAgent()


if __name__=="__main__":
    sm=StateManager()
    sm.save("a_float", 6.66)
    sm.save("an_int", 666)
    sm.save("a_string", "666")

    print sm.retrieve("a_float")
    print sm.retrieve("an_int")
    print sm.retrieve("a_string")
    