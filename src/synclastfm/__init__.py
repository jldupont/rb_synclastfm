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
    
"""
import rhythmdb, rb #@UnresolvedImport

from config import ConfigDialog
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
        sp = shell.get_player ()
        self.cb = (
                   sp.connect ('playing-song-changed', 
                               self.playing_song_changed)
                   )

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
        



class EntryHelper:
    """
    Helper functions for song database entries
    """
    props = {   "artist":    rhythmdb.PROP_ARTIST
                ,"album":    rhythmdb.PROP_ALBUM
                ,"duration": rhythmdb.PROP_DURATION
                ,"track":    rhythmdb.PROP_TITLE
                ,"mb_id":    rhythmdb.PROP_MUSICBRAINZ_TRACKID
                ,"duration": rhythmdb.PROP_DURATION
             }
    
    @classmethod
    def track_details(cls, shell, entry):
        """
        Retrieves details associated with a db entry
        
        @return: (artist, title)
        """
        db = shell.props.db
        result={}
        for prop, key in cls.props.iteritems():
            result[prop]=db.entry_get(entry, key)
        return result
    
