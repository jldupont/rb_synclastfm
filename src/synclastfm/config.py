"""
    Configuration Dialog
    
    At this point, just status reporting really 

    Created on 2010-01-13
    @author: jldupont
    
    - displays if user's Last.fm username is found

"""

import gtk
import gobject

from system.bus import Bus

class ConfigDialog(gobject.GObject): #@UndefinedVariable
    
    __gsignals__ = {
        "lastfm_username_changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)) #@UndefinedVariable
        }
    
    def __init__(self, glade_file, testing=False):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self.testing=testing
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.dialog = self.builder.get_object("config_dialog")
        self.dialog._testing=testing
        self.dialog._builder=self.builder
        
        self._dowiring()
        
        self.builder.connect_signals(self.dialog, self.dialog)
        
        Bus.add_emission_hook("lastfm_username_changed",    self.on_username_changed)
        Bus.add_emission_hook("lastfm_proxy_detected",      self.on_lastfm_proxy_detected)
        Bus.add_emission_hook("musicbrainz_proxy_detected", self.on_musicbrainz_proxy_detected)

        self.mb_proxy_detected=False
        self.lb_proxy_detected=False

    def _dowiring(self):
        """
        Wires the GTK dialog to the signal handlers
        provided in this class
        """
        for name, m in self.__class__.__dict__.items():
            if name.startswith("on_"):
                self.dialog.__dict__[name]=m

    def get_dialog(self):
        return self.dialog

    ## ===================================== Signal Handlers
    def on_username_changed(self, _username, data=None):
        """
        GObject handler
        """        
        #print "Config.on_username_changed  data=%s" % str(data)
        t=self.builder.get_object("lastfm_username_entry")
        t.set_text(data)
        return True

    def on_show(self, *_):
        print "on_show"
        Bus.emit("lastfm_proxy_detected?")
        Bus.emit("musicbrainz_proxy_detected?")
        self._upLfProxy()
        self._upMbProxy()

    def on_close_clicked(_el, dialog): #@NoSelf
        dialog.hide()
        if dialog._testing:
            gtk.main_quit()

    def on_config_dialog_destroy(_el, dialog): #@NoSelf
        dialog.hide()
        if dialog._testing:
            gtk.main_quit()
    
    def on_musicbrainz_proxy_detected(self, _state, data=None):
        print "on_musicbrainz_proxy_detected: data: %s" % data
        
        active=data==True or data=="1" or data=="True"
        self.mb_proxy_detected=active
        self._upMbProxy()
        
    def _upMbProxy(self):
        t=self.builder.get_object("musicbrainz_proxy_detected_button")
        t.set_sensitive(True)
        t.set_active(self.mb_proxy_detected)
        t.set_sensitive(False)

    def on_lastfm_proxy_detected(self, _state, data=None):
        print "on_lastfm_proxy_detected: data: %s" % data
        
        active=data==True or data=="1" or data=="True"
        self.lb_proxy_detected=active
        self._upLfProxy()
        
    def _upLfProxy(self):
        t=self.builder.get_object("lastfm_proxy_detected_button")
        t.set_sensitive(True)
        t.set_active(self.lb_proxy_detected)
        t.set_sensitive(False)
        

