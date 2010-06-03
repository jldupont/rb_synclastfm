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
import gobject
import dbus.glib
from dbus.mainloop.glib import DBusGMainLoop

gobject.threads_init()  #@UndefinedVariable
dbus.glib.init_threads()
DBusGMainLoop(set_as_default=True)


import rhythmdb, rb #@UnresolvedImport

from system.mbus import Bus
from helpers import EntryHelper

from config import ConfigDialog
from track import Track

import agents.bridge
import agents.user
import agents.lastfm
import agents.updater

#import agents.lastfm_proxy
#import agents.state
#import agents.finder
#import agents.mb
##import agents.metadb not used since musicbrainz-proxy > v2.x


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
        db=self.shell.props.db
        
        ## We might have other signals to connect to in the future
        self.cb = (
                   sp.connect ('playing-song-changed', 
                               self.playing_song_changed),
                   )
        ## Distribute the vital RB objects around
        Bus.publish(self, "rb_shell", shell, db, sp)
        
    def deactivate (self, shell):
        self.shell = None
        sp = shell.get_player()
        
        for id in self.cb:
            sp.disconnect (id)

    def create_configure_dialog(self, dialog=None):
        """
        This method is called by RB when "configure" button
        is pressed in the "Edit->Plugins" menu.
        
        Note that the dialog *shouldn't* be destroyed but "hidden" 
        when either the "close" or "X" buttons are pressed.
        """
        if not dialog:
            glade_file_path=self.find_file("config.glade")
            proxy=ConfigDialog(glade_file_path)
            dialog=proxy.get_dialog() 
        dialog.present()
        Bus.publish(self, "config?")
        return dialog

            
    def playing_song_changed (self, sp, entry):
        """
        The event that starts the whole "sync" process
        """
        ## unfortunately, I don't have a better process
        ## for keeping the "user parameters" synced just yet...
        Bus.publish(self, "config?")
        
        self.current_entry = sp.get_playing_entry()
        details=EntryHelper.track_details(self.shell, entry)
        if details:
            track=Track(details=details, entry=self.current_entry)
            Bus.publish(self, "track?", track)


count=0
def gen_tick():
    global count
    Bus.publish("__gen_tick__", "tick", count)
    #print "tick: count(%s)" % count
    count += 1
    return True

TICK_FREQ=4
gobject.timeout_add(1000/TICK_FREQ, gen_tick)  #@UndefinedVariable


"""
dir(rhythmdb):
['ENTRY_CONTAINER', 'ENTRY_NORMAL', 'ENTRY_STREAM', 'ENTRY_VIRTUAL', 
'Entry', 'EntryCategory', 'EntryType', 'ImportJob', 

'PROPERTY_MODEL_COLUMN_NUMBER', 'PROPERTY_MODEL_COLUMN_PRIORITY', 
'PROPERTY_MODEL_COLUMN_TITLE', 

'PROP_ALBUM', 'PROP_ALBUM_FOLDED', 
'PROP_ALBUM_GAIN', 'PROP_ALBUM_PEAK', 'PROP_ALBUM_SORTNAME', 'PROP_ALBUM_SORT_KEY', 
'PROP_ARTIST', 'PROP_ARTIST_FOLDED', 'PROP_ARTIST_SORTNAME', 'PROP_ARTIST_SORT_KEY', 
'PROP_BITRATE', 'PROP_COPYRIGHT', 'PROP_DATE', 'PROP_DESCRIPTION', 'PROP_DISC_NUMBER', 
'PROP_DURATION', 
'PROP_ENTRY_ID', 'PROP_FILE_SIZE', 'PROP_FIRST_SEEN', 
'PROP_FIRST_SEEN_STR', 'PROP_GENRE', 'PROP_GENRE_FOLDED', 'PROP_GENRE_SORT_KEY', 
'PROP_HIDDEN', 'PROP_IMAGE', 'PROP_KEYWORD', 'PROP_LANG', 
'PROP_LAST_PLAYED', 'PROP_LAST_PLAYED_STR', 
'PROP_LAST_SEEN', 'PROP_LAST_SEEN_STR', 
'PROP_LOCATION', 'PROP_MIMETYPE', 'PROP_MOUNTPOINT', 'PROP_MTIME', 
'PROP_MUSICBRAINZ_ALBUMARTISTID', 'PROP_MUSICBRAINZ_ALBUMID', 'PROP_MUSICBRAINZ_ARTISTID', 'PROP_MUSICBRAINZ_TRACKID', 
'PROP_PLAYBACK_ERROR', 'PROP_PLAY_COUNT', 'PROP_POST_TIME', 'PROP_RATING', 
'PROP_SEARCH_MATCH', 'PROP_STATUS', 'PROP_SUBTITLE', 'PROP_SUMMARY', 'PROP_TITLE', 
'PROP_TITLE_FOLDED', 'PROP_TITLE_SORT_KEY', 'PROP_TRACK_GAIN', 'PROP_TRACK_NUMBER', 
'PROP_TRACK_PEAK', 'PROP_TYPE', 'PROP_YEAR', 

'PropType', 'PropertyModel', 'PropertyModelColumn', 

'QUERY_DISJUNCTION', 'QUERY_END', 'QUERY_MODEL_LIMIT_COUNT', 'QUERY_MODEL_LIMIT_NONE', 
'QUERY_MODEL_LIMIT_SIZE', 'QUERY_MODEL_LIMIT_TIME', 'QUERY_PROP_CURRENT_TIME_NOT_WITHIN', 
'QUERY_PROP_CURRENT_TIME_WITHIN', 'QUERY_PROP_EQUALS', 'QUERY_PROP_GREATER', 
'QUERY_PROP_LESS', 'QUERY_PROP_LIKE', 'QUERY_PROP_NOT_LIKE', 'QUERY_PROP_PREFIX', 
'QUERY_PROP_SUFFIX', 'QUERY_PROP_YEAR_EQUALS', 'QUERY_PROP_YEAR_GREATER', 
'QUERY_PROP_YEAR_LESS', 'QUERY_SUBQUERY', 

'Query', 'QueryModel', 'QueryModelLimitType', 'QueryResults', 'QueryType', 'RhythmDB', 
'StringValueMap', '__doc__', '__name__', '__package__', '__version__', 
'rhythmdb_compute_status_normal', 'rhythmdb_query_model_album_sort_func', 
'rhythmdb_query_model_artist_sort_func', 'rhythmdb_query_model_date_sort_func', 
'rhythmdb_query_model_double_ceiling_sort_func', 'rhythmdb_query_model_genre_sort_func', 
'rhythmdb_query_model_location_sort_func', 'rhythmdb_query_model_string_sort_func', 
'rhythmdb_query_model_title_sort_func', 'rhythmdb_query_model_track_sort_func', 
'rhythmdb_query_model_ulong_sort_func']
"""