"""
    SyncLastFM - Rhythmbox plugin

    @author: Jean-Lou Dupont
    
    Feature 1: Fill "rating" from "Love" field
    Feature 2: Update local "play count" 
    
    Implementation:
    ===============
    
    - On "playing_changed" event, fetch "track info" from Last.fm
      - Update "rating" field
      - Update "play count" field
    
    Failure modes:
    ==============
    - Username for Last.fm account can't be found
    - Failure to communicate with Last.fm
    - Track cannot be found on Last.fm 
      - Wrong/insufficient detail locally
    
"""
import rhythmdb, rb #@UnresolvedImport

from bus import Bus
from helpers import EntryHelper, WrapperGObject

import lastfm
from updater import upd

from user import lfmuser
from config import ConfigDialog
from track import Track

PLUGIN_NAME="synclastfm"

class SyncLastFMDKPlugin (rb.Plugin):
    """
    Must derive from rb.Plugin in order
    for RB to use the plugin
    """
    def __init__ (self):
        rb.Plugin.__init__ (self)
        self.current_entry=None

    def activate (self, shell):
        self.shell = shell
        sp = shell.get_player()
        
        ## We might have other signals to connect to in the future
        self.cb = (
                   sp.connect ('playing-song-changed', 
                               self.playing_song_changed),
                   )
        ## Distribute the shell around
        rbobjects=WrapperGObject(shell=self.shell, 
                                 db=self.shell.props.db, 
                                 player=self.shell.get_player())
        Bus.emit("rb_shell", rbobjects)
        
    def deactivate (self, shell):
        self.shell = None
        sp = shell.get_player()
        
        for id in self.cb:
            sp.disconnect (id)

    def create_configure_dialog(self, dialog=None):
        """
        This method is called by RB when "configure" button
        is pressed in the "Edit->Plugins" menu.
        """
        if not dialog:
            glade_file_path=self.find_file("config.glade")
            proxy=ConfigDialog(glade_file_path)
            dialog=proxy.get_dialog() 
        dialog.present()
        return dialog

            
    def playing_song_changed (self, sp, entry):
        """
        Just grab the current playing entry
        The rest of the work will be done through the
        event "playing_changed"
        """
        self.current_entry = sp.get_playing_entry()
        details=EntryHelper.track_details(self.shell, entry)
        if details:
            track=Track(details=details, entry=self.current_entry)
            Bus.emit("playing_song_changed", track)



