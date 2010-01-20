""" 
    GObject message Bus
    
    @author: jldupont
"""

import gobject

class Signals(gobject.GObject):
    """
    List of the application level signals
    """
    __gsignals__ = {
        "lastfm_username_changed":  (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)) 
        ,'lastfm_password_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
        ,'lastfm_request_failed':   (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
        ,"playing_song_changed":    (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))
        ,"user_track_info":         (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))                
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        
        
class Bus(object):
    """
    Message Bus
    
    Borg Pattern
    """
    _signals=Signals()

    @classmethod
    def emit(cls, name, *pa, **kwa):
        cls._signals.emit(name, *pa, **kwa)

    @classmethod
    def add_emission_hook(cls, name, callback):
        gobject.add_emission_hook(cls._signals, name, callback)
    
mbus=Bus()


## =============================================================== Tests


if __name__=="__main__":

    def callback(signal, data):
        print "callback: signal=%s, data=%s" % (signal, data)
    
    Bus.add_emission_hook("lastfm_username_changed", callback)
    
    Bus.emit("lastfm_username_changed", "jldupont")
    