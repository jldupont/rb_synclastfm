"""
    Configuration Dialog
    
    At this point, just status reporting really 

    Created on 2010-01-13
    @author: jldupont
    
    - displays if user's Last.fm username is found

"""

import gtk


class ConfigDialog(object):
    def __init__(self, glade_file):
        builder = gtk.Builder()
        builder.add_from_file(glade_file)
        self.dialog = builder.get_object("config_dialog")
 
        self._dowiring()
        
        builder.connect_signals(self.dialog, self.dialog)

    def _dowiring(self):
        for name, m in self.__class__.__dict__.items():
            if name.startswith("on_"):
                self.dialog.__dict__[name]=m

    def get_dialog(self):
        return self.dialog

    ## ===================================== Signal Handlers

    def on_close_clicked(el, dialog): #@NoSelf
        dialog.hide()

    def on_config_dialog_destroy(el, dialog): #@NoSelf
        dialog.hide()
    

## ==================================================== Tests

if __name__=="__main__":
    
    window = ConfigDialog("config.glade")
    gtk.main()
    