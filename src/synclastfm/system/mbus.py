"""
    Simple "Bus" based message publish/subscribe

    - Announces "client" subscriptions through
      a special message "_sub"
      
    - "Promiscuous" subscription supported
      through using the "*" as message type upon
      performing subscription
      
    Created on 2010-01-28
    @author: Jean-Lou Dupont
"""

__all__=["Bus"]

class BusLogger(object):
    """ Simplistic Bus `Logger`
    """
    def __call__(self, *p):
        print "BusLogger: ", p


class Bus(object):
    """
    Simple publish/subscribe "message bus"
    with configurable error reporting
    
    Message delivery is "synchronous i.e. the caller of
    the "publish" method blocks until all the subscribers
    of the message have been "called-back".
    
    Any "callback" can return "True" for stopping the
    calling chain.
    """
    debug=False
    logger=BusLogger()
    ftable={}
    sendMsgType=False
    callstack=[]

    @classmethod
    def _maybeLog(cls, msgType, msg):
        """
        Private - Logging helper
        """
        if not cls.debug:
            return
        
        if msgType=="%log":
            return
        
        if cls.logger:
            cls.logger(msg)
    
    @classmethod
    def reset(cls):
        """ Resets the Bus to a known state
        
            This is especially useful when, as example,
            a process is spawn whilst the parent had a
            configured Bus instance.  The child process
            calls this method upon starting in order to
            fall back to a known state before proceeding
            to accept new subscriptions.
        """
        cls.logger=None
        cls.sendMsgType=False
        cls.callstack=[]
    
    @classmethod
    def sub(cls, subscriber, msgType, callback):
        cls.sub(subscriber, msgType, callback)
    
    @classmethod
    def subscribe(cls, subscriber, msgType, callback):
        """
        Subscribe to a Message Type
        
        The "msgType" can be "*" to accept promiscuous subscriptions.
        
        @param msgType: string, unique message-type identifier
        @param callback: callable instance which will be called upon message delivery  
        """
        ##print "Bus.suscribe, mtype(%s) cb(%s)" % (msgType, callback)
        try:
            cls._maybeLog(msgType, "subscribe: subscriber(%s) msgType(%s)" % (str(callback), msgType))
            subs=cls.ftable.get(msgType, [])
            subs.append((str(subscriber), callback))
            cls.ftable[msgType]=subs
        except Exception, e:
            raise RuntimeError("Bus.subscribe: exception: subscribe: %s" % str(e))
            
        ## Announce the subscriptions
        ##  This step is useful for "message bridges"
        if not msgType.startswith("_"):
            cls.publish("__bus__", "_sub", msgType)
        
    @classmethod
    def pub(cls, acaller, msgType, *pa, **kwa):
        cls.publish(acaller, msgType, *pa, **kwa)
        
    @classmethod
    def publish(cls, acaller, msgType, *pa, **kwa):
        """
        Publish a message from a specific type on the bus
        
        @param msgType: string, message-type
        @param *pa:   positional arguments
        @param **kwa: keyword based arguments
        """
        caller=str(acaller)
        
        if msgType in cls.callstack:
            raise RuntimeError("Bus: cycle detected: %s" % cls.callstack)
        
        cls.callstack.extend([msgType])
        
        #if msgType!="mswitch_pump":
        #    print "bus.publish: mtype(%s) caller(%s)" % (msgType, caller)
        cls._maybeLog(msgType, "BUS.publish: type(%s) caller(%s) pa(%s) kwa(%s)" % (msgType, caller, pa, kwa))
        subs=cls.ftable.get(msgType, [])
        if not subs:
            cls._maybeLog(msgType, "Bus.publish: no subs for msgtype(%s)" % str(msgType))
            
        ## First, do the normal subscribers
        cls._doPub(False, subs, caller, msgType, *pa, **kwa)
        
        ## Second, do the "promiscuous" subscribers
        psubs=cls.ftable.get("*", [])
        cls._doPub(True, psubs, caller, msgType, *pa, **kwa)
        
        #print "Bus.Publish: callstack: ", cls.callstack
        cls.callstack.pop()

    @classmethod
    def _doPub(cls, sendMtype, subs, caller, msgType, *pa, **_kwa):
        #print "_doPub, pa:", pa
        for (sub, cb) in subs:
            if sub==caller:  ## don't send to self
                continue
            try:
                if cls.sendMsgType or sendMtype:
                    cb(msgType, *pa)
                else:
                    cb(*pa)
            except IOError:
                raise
            except TypeError,e:
                print "Bus.publish: Exception: %s" % e
                raise
            except Exception,e:
                print "Bus.publish: cb(%s) exception: %s" % (cb, e)
                raise
