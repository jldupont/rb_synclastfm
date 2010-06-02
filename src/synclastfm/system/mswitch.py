"""
    Message Switch
    
    @author: jldupont
    @date: May 17, 2010
"""

from threading import Thread
from Queue import Queue

__all__=["publish", "subscribe"]


class BasicSwitch(Thread):
    """
    Simple message switch
    
    Really just broadcasts the received
    message to all 'clients' in 'split horizon'
    i.e. not sending back to originator
    """
    def __init__(self):
        Thread.__init__(self)
        
        self.clients=[]
        self.iq=Queue()
    
    def run(self):
        """
        Main loop
        """
        while True:
            envelope=self.iq.get(block=True)
            mtype, payload=envelope
            
            if mtype=="__sub__":
                q=payload
                self.do_sub(q)
            else:
                self.do_pub(mtype, payload)
                
            ## We needed to give a chance to
            ## all threads to exit before
            ## committing "hara-kiri"
            if mtype=="__quit__":
                break
               
                
    def do_sub(self, q):
        """
        Performs subscription
        """
        self.clients.append(q)
        
    def do_pub(self, mtype, payload):
        """
        Performs message distribution
        """
        #print "do_pub: mtype: %s  payload: %s" % (mtype, payload)
        for q in self.clients:
            #print "switch.do_pub: q, mtype: ", q, mtype
            q.put((mtype, payload))
    


## ===============================================================  
## =============================================================== API functions
## =============================================================== 
        

def publish(orig, msgType, msg=None, *pargs, **kargs):
    """
    Publish a 'message' of type 'msgType' to
    all registered 'clients'
    """
    _switch.iq.put((msgType, (orig, msg, pargs, kargs)))
    
    
def subscribe(q):
    """
    Subscribe a 'client' to all the switch messages
     
    @param q: client's input queue
    """
    _switch.iq.put(("__sub__", q))
    



_switch=BasicSwitch()
_switch.start()
