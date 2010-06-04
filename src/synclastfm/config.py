"""
    Configuration Dialog
    
    At this point, just status reporting really 

    Created on 2010-01-13
    @author: jldupont
    
    - displays if user's Last.fm username is found

"""
import gobject
import gtk

from system.mbus import Bus

class ConfigDialog(gobject.GObject): #@UndefinedVariable
    
    def __init__(self, glade_file, testing=False):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.testing=testing
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.dialog = self.builder.get_object("config_dialog")
        self.dialog._testing=testing
        self.dialog._builder=self.builder
        self.mb_proxy_detected=False
        self.lb_proxy_detected=False
        
        signals={"visibility-notify-event":        self.on_show,
                 "on_show":                        self.on_show,
                 "on_close_clicked":               self.on_close_clicked,
                 "on_config_dialog_destroy":       self.on_config_dialog_destroy}
        
        self.builder.connect_signals(signals, self)
        
        Bus.subscribe("Config", "lastfm_username_changed",    self.on_username_changed)
        Bus.subscribe("Config", "lastfm_proxy_detected",      self.on_lastfm_proxy_detected)
        Bus.subscribe("Config", "musicbrainz_proxy_detected", self.on_musicbrainz_proxy_detected)

    def get_dialog(self):
        return self.dialog

    ## ===================================== Signal Handlers
    def on_username_changed(self, username):
        #print "Config.on_username_changed  data=%s" % str(data)
        t=self.builder.get_object("lastfm_username_entry")
        t.set_text(username)
        return True

    def on_show(self, *_):
        Bus.publish("Config", "lastfm_proxy_detected?")
        Bus.publish("Config", "musicbrainz_proxy_detected?")
        self._upLfProxy()
        self._upMbProxy()

    def on_close_clicked(self, *_): #@NoSelf
        self.dialog.hide()

    def on_config_dialog_destroy(self, *_):
        self.dialog.hide()
        gtk.main_quit()
    
    def on_musicbrainz_proxy_detected(self, state):
        #print "on_musicbrainz_proxy_detected: self: %s -- state:%s" % (self, state)
        self.mb_proxy_detected=state
        self._upMbProxy()
        
    def _upMbProxy(self):
        t=self.builder.get_object("musicbrainz_proxy_detected_button")
        t.set_sensitive(True)
        t.set_active(self.mb_proxy_detected)
        t.set_sensitive(False)

    def on_lastfm_proxy_detected(self, state):
        #print "on_lastfm_proxy_detected: data: %s" % state
        self.lb_proxy_detected=state
        self._upLfProxy()
        
    def _upLfProxy(self):
        t=self.builder.get_object("lastfm_proxy_detected_button")
        t.set_sensitive(True)
        t.set_active(self.lb_proxy_detected)
        t.set_sensitive(False)
        

