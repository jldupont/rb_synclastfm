""" 
    GObject message Bus
    
    @author: jldupont
"""

import gobject #@UnresolvedImport

class Signals(gobject.GObject): #@UndefinedVariable
    """
    List of the application level signals
    """
    __gsignals__ = {
                    
        ## Announces changes in the user's Last.fm properties
        "lastfm_username_changed":  (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))  #@UndefinedVariable 
        ,'lastfm_password_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))  #@UndefinedVariable

        ## Used to signal a change in the currently playing track
        ,"playing_song_changed":    (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable
        
        ## Used to report a failure when accessing Last.fm web service
        ,'lastfm_request_failed':   (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())                      #@UndefinedVariable
        
        ## Used for distributing the results of the query against the Last.fm web service
        ,"user_track_info":         (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable
        
        ## Used to pass around the "shell" global object
        ,"rb_shell":                (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable

        ## Used to pass around "Records" from lastfm proxy dbus
        ,"records":                 (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable
        
        ## Used to signal the detection of Lastfm Proxy DBus
        ,"lastfm_proxy_detected":   (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))  #@UndefinedVariable

        ## Used to signal the detection of Musicbrainz Proxy DBus
        ,"musicbrainz_proxy_detected":   (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))  #@UndefinedVariable
        
        ## Question: What is the "latest timestamp"
        ,"q_last_ts":               (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())  #@UndefinedVariable
        
        ## Response: "last timestamp"
        ,"last_ts":                 (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT,))  #@UndefinedVariable
        
        ## An Entry being worked on
        ,"entry":                   (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable

        ## An Entry which has been updated
        ,"entry_updated":           (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable

        ## Question: track_info
        ##  Response will be through "user_track_info"        
        ,"q_track_info":            (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable

        ## Generated in Finder
        ,"track_entry":             (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable

        ## Emitted by MB Agent        
        ,"mb_entry":                (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,))  #@UndefinedVariable

    }

    def __init__(self):
        gobject.GObject.__init__(self) #@UndefinedVariable
        
        
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
        gobject.add_emission_hook(cls._signals, name, callback) #@UndefinedVariable
    
mbus=Bus()


## =============================================================== Tests


if __name__=="__main__":

    def callback(signal, data):
        print "callback: signal=%s, data=%s" % (signal, data)
    
    Bus.add_emission_hook("lastfm_username_changed", callback)
    
    Bus.emit("lastfm_username_changed", "jldupont")
    