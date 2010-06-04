"""
    Message Bridge
    
    Performs "bridging" of messages between the shared Bus (mbus)
    living on the main-thread and the other threads hanging off
    the "mswitch"

    @author: jldupont
    @date: Jun 3, 2010
"""
from Queue import Queue, Empty

from synclastfm.system.mbus import Bus
from synclastfm.system import mswitch


class BridgeAgent(object):
    def __init__(self):
        self.iq=Queue()
        Bus.subscribe("__bridge__", "*", self.h_msg)
        
    def h_msg(self, mtype, *pa):
        
        #if mtype!="tick":
        #    print "to mswitch: mtype(%s) pa:%s" % (mtype, pa)
        mswitch.publish("__bridge__", mtype, *pa)

        if mtype=="tick":
            while True:
                try:   msg=self.iq.get(block=False)
                except Empty:
                    break
                
                (mtype, payload) = msg
                orig, pargs = payload
    
                if orig!="__bridge__":
                    #if mtype != "tick":
                    #    print "!! from mswitch: orig(%s) mtype(%s) pargs(%s)" % (orig, mtype, pargs)
                    Bus.publish("__bridge__", mtype, *pargs)
            
            

_=BridgeAgent()
mswitch.subscribe(_.iq)
