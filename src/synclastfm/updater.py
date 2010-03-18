"""
    Updater module

    1) if "rating" is 0.0
          if "love" is True
             update rating
             
    2) take last.fm's playcount and
       update local playcount of track

    @author: jldupont
"""
import rhythmdb #@UnresolvedImport

import gobject #@UnresolvedImport
from bus import Bus


class Updater(gobject.GObject):
    """
    Updates various properties
    """
    def __init__(self):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._shell=None
        self._db=None
        
        Bus.add_emission_hook("user_track_info", self.on_user_track_info)
        Bus.add_emission_hook("rb_shell",        self.on_rb_shell)
        
    def on_rb_shell(self, _signal, rbobjects):
        """
        Grab RB objects references (shell, db, player)
        
        GObject handler
        """
        self._robjects=rbobjects
        self._db=self._robjects.db
        return True
        
    def on_user_track_info(self, _signal, track):
        """
        GObject handler
        
        track.details : dict with extracted information from track.entry
        track.entry: an RB DB entry
        track.lastfm_info
        
        @param track: a Track object instance 
        """
        ## These are always guaranteed to be since
        ## they originate from RB
        rating=track.details["rating"]
        lpc=track.details["playcount"]
        
        ## These might be missing
        try:    love=int(track.lastfm_info.get("track.userloved", 0))
        except: love=0
        try:    lfmpc=int(track.lastfm_info.get("track.userplaycount", 0))
        except: lfmpc=0
        
        print ">> rating(%s) love(%s) local playcount(%s) lastfm playcount(%s)" % (rating, love, lpc, lfmpc)
        
        try:
            changed=False
            
            ## Only update local "playcount" if we have a meaningful playcount from Last.fm
            if lfmpc > 0:
                self._db.set(track.entry, rhythmdb.PROP_PLAY_COUNT, lfmpc)
                changed=True
                print ">> Updating playcount to: %s" % lfmpc
            
            ## Only update the "rating" if we have no rating yet locally
            if love:
                if rating == 0: #works with float
                    self._db.set(track.entry, rhythmdb.PROP_RATING, 5.0)
                    changed=True
                    print ">> Updating rating to 5.0"
                    
            if changed:
                print ">> Committing change to database"
                self._db.commit()
                
        except Exception, e:
            print "!! Exception whilst updating track, msg=%s" % str(e)
            
        return True

gobject.type_register(Updater)

upd=Updater()
