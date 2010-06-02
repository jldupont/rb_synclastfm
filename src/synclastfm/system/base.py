"""
    Basic definition of a threaded agent
    
    @author: jldupont
    @date: May 17, 2010
"""

from threading import Thread
from Queue import Queue
import uuid

import mswitch

__all__=["AgentThreadedBase", "debug", "mdispatch"]

debug=False


def mdispatch(obj, obj_orig, envelope):
    """
    Dispatches a message to the target
    handler inside a class instance
    """
    mtype, payload = envelope
    orig, msg, pargs, kargs = payload
    
    ## Avoid sending to self
    if orig == obj_orig:
        return

    if mtype=="__quit__":
        return True

    if mtype.endswith("?"):
        handlerName="hq_%s" % mtype[:-1]
    else:
        handlerName="h_%s" % mtype
    handler=getattr(obj, handlerName, None)
    
    if handler is None:
        handler=getattr(obj, "h_default", None)    
        if handler is not None:
            handler(mtype, msg, *pargs, **kargs)
    else:
        try:
            handler(msg, *pargs, **kargs)
        except TypeError, e:
            raise RuntimeError("Invalid handler for mtype(%s) in obj(%s): %s" % (mtype, str(obj), e))

    if handler is None:
        if debug:
            print "! No handler for message-type: %s" % mtype
    
    return False


class AgentThreadedBase(Thread):
    
    def __init__(self, debug=False):
        Thread.__init__(self)
        
        self.debug=debug
        self.id = uuid.uuid1()
        self.iq = Queue()
        
    def pub(self, msgType, msg, *pargs, **kargs):
        mswitch.publish(self.id, msgType, msg, *pargs, **kargs)
        
    def run(self):
        """
        Main Loop
        """
        ## subscribe this agent to all
        ## the messages of the switch
        mswitch.subscribe(self.iq)
        
        while True:
            envelope=self.iq.get(block=True)
            quit=mdispatch(self, self.id, envelope)
            if quit:
                shutdown_handler=getattr(self, "h_shutdown", None)
                if shutdown_handler is not None:
                    shutdown_handler()
                break
                    


## ============================================================
## ============================================================ TESTS
## ============================================================


if __name__=="__main__":
    
    class Agent1(AgentThreadedBase):
        def __init__(self):
            AgentThreadedBase.__init__(self)
            
        def h_mtype1(self, *pargs, **kargs):
            print "Agent1.h_mtype1: pargs: %s  kargs: %s" % (pargs, kargs)

        def h_mtype2(self, *pargs, **kargs):
            print "Agent1.h_mtype2: pargs: %s  kargs: %s" % (pargs, kargs)
            

    class Agent2(AgentThreadedBase):
        def __init__(self):
            AgentThreadedBase.__init__(self)
            
        def h_mtype1(self, *pargs, **kargs):
            print "Agent2.h_mtype1: pargs: %s  kargs: %s" % (pargs, kargs)
            self.pub("mtype2", "mtype2 message!")

        def h_mtype2(self, *pargs, **kargs):
            print "Agent2.h_mtype2: pargs: %s  kargs: %s" % (pargs, kargs)


    a1=Agent1()
    a2=Agent2()
    
    a1.start()
    a2.start()
    
    mswitch.publish(None, "mtype1", "coucou!")
    mswitch.publish(None, "mtype1", "coucou2!")

    while True:
        pass
