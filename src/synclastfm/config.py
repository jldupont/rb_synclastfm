"""
    Configuration Dialog
    
    At this point, just status reporting really 

    Created on 2010-01-13
    @author: jldupont
    
    - displays if user's Last.fm username is found

"""

import gtk


class ConfigDialog(object):
    def __init__(self, glade_file, testing=False):
        self.testing=testing
        builder = gtk.Builder()
        builder.add_from_file(glade_file)
        self.dialog = builder.get_object("config_dialog")
        self.dialog._testing=testing
        self.dialog._builder=builder
        
        self._dowiring()
        
        builder.connect_signals(self.dialog, self.dialog)

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
        pass


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
    
    window = ConfigDialog("config.glade", testing=True)
    d=window.get_dialog()
    #print dir(d)
    #print d.__class__
    #print d._testing
    b=d._builder
    t=b.get_object("lastfm_username_entry")
    print dir(t)
    t.set_text("test!")
    #usernameObject=window.get_object("lastfm_username_entry")
    gtk.main()
