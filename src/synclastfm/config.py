"""
    Configuration Dialog
    
    At this point, just status reporting really 

    Created on 2010-01-13
    @author: jldupont
    
    - displays if user's Last.fm username is found

"""

import gtk
import gobject


class ConfigDialog(gobject.GObject):
    
    __gsignals__ = {
        "lastfm_username_changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)) #@UndefinedVariable
        }
    
    def __init__(self, glade_file, testing=False):
        gobject.GObject.__init__(self)
        self.testing=testing
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.dialog = self.builder.get_object("config_dialog")
        self.dialog._testing=testing
        self.dialog._builder=self.builder
        
        self._dowiring()
        
        self.builder.connect_signals(self.dialog, self.dialog)
        
        gobject.add_emission_hook(self, "lastfm_username_changed", self.on_username_changed)

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
    def on_username_changed(self, username, data=None):
        """
        GObject handler
        """        
        print "Config.on_username_changed  data=%s" % str(data)
        t=self.builder.get_object("lastfm_username_entry")
        t.set_text(data)
        return True

    def on_close_clicked(el, dialog): #@NoSelf
        dialog.hide()
        if dialog._testing:
            gtk.main_quit()

    def on_config_dialog_destroy(el, dialog): #@NoSelf
        dialog.hide()
        if dialog._testing:
            gtk.main_quit()
    

## ==================================================== Tests

if __name__=="__main__":
    import user
    u=user.LastFMUser()
    
    
    window = ConfigDialog("config.glade", testing=True)
    d=window.get_dialog()
    #print dir(d)
    #print d.__class__
    #print d._testing
    b=d._builder
    t=b.get_object("lastfm_username_entry")
    #print dir(t)
    t.set_text("test!")
    #usernameObject=window.get_object("lastfm_username_entry")
    
    u.refresh()
    #u.emit("lastfm_username_changed", "jldupont")
    
    gtk.main()