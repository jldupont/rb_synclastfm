"""
    Updater module

    1) if "rating" is 0.0
          if "love" is True
             update rating
             
    2) take last.fm's playcount and
       update local playcount of track

    MESSAGES IN:
    - "track_entry"
    - "rb_shell"
    - "user_track_info"
    - "mb_entry"
    
    MESSAGES OUT:
    - "track_updated"


    @author: jldupont
"""
import rhythmdb #@UnresolvedImport

from synclastfm.system.mbus import Bus


class Updater(object): #@UndefinedVariable
    """
    Updates various properties
    """
    def __init__(self):
        self._shell=None
        self._db=None
        
        Bus.subscribe("Updater", "track_entry",     self.on_track_entry)
        Bus.subscribe("Updater", "user_track_info", self.on_user_track_info)
        Bus.subscribe("Updater", "rb_shell",        self.on_rb_shell)
        
    def on_rb_shell(self, shell, db, _sp):
        """
        Grab RB objects references (shell, db, player)
        """
        self._shell=shell
        self._db=db
        
    def on_track_entry(self, trackWrapper):
        """
        Note: track_entry is defined in "Finder"
        """
        te=trackWrapper.track_entry
        dbe=trackWrapper.db_entry
        
        #print "te.details: %s" % te.details
        
        ## If Finder didn't find an entry in the database,
        ## we can't do much at this point
        if dbe is None:
            return
        
        ## The 'track_entry' should contain a field 'lfid'
        ##  and the value should be formatted:
        ##   lfid:'id':'playcount'
        try:    lfid=te.details["lfid"]
        except: lfid=None
        
        if lfid is None:
            return
        
        try:    pieces=lfid.split(":")
        except: pieces=None
        
        if pieces is None:
            print "Can't extract 'lfid' fields!"
            return
        
        
        try: playcount=long(pieces[2])
        except:
            print "** Playcount not found"
            return
        
        print "updating: lfid(%s)" % lfid
        
        try:
            self._db.set(dbe, rhythmdb.PROP_PLAY_COUNT, playcount)
            self._db.commit()
        except Exception,e:
            print "ERROR: updating 'playcount' for track: %s" % e
        
        Bus.publish("Updater", "track_updated", te)
        
        
        
    def on_user_track_info(self, track):
        """
        track.details : dict with extracted information from track.entry
        track.entry: an RB DB entry
        track.lastfm_info
        
        @param track: a Track object instance 
        """

        ## Since the 'track' message can originate from many
        ##  different agents, we must check the contents to make
        ##  sure we can do something about the message        
        rating=track.details.get("rating", None)
        if rating is None:
            return
        
        ## These might be missing
        try:    love=int(track.lastfm_info.get("track.userloved", 0))
        except: love=0
        try:    lfmpc=int(track.lastfm_info.get("track.userplaycount", 0))
        except: lfmpc=0
        
        print ">> rating(%s) love(%s) lastfm playcount(%s)" % (rating, love, lfmpc)
        
        try:    track_mbid=str(track.lastfm_info.get("track.mbid", ""))
        except: track_mbid=""
       
        try:
            changed=False
        
            ## Update the track's mbid if we can
            if track_mbid != "":
                self._db.set(track.entry, rhythmdb.PROP_MUSICBRAINZ_TRACKID, track_mbid)
                changed=True
                #print "% track_mbid: %s" % track_mbid
                
            
            ## Only update local "playcount" if we have a meaningful 
            ## playcount from Last.fm
            if lfmpc > 0:
                self._db.set(track.entry, rhythmdb.PROP_PLAY_COUNT, lfmpc)
                changed=True
                #print ">> Updating playcount to: %s" % lfmpc
            
            ## Only update the "rating" if we have no rating yet locally
            if love:
                if rating == 0: #works with float
                    self._db.set(track.entry, rhythmdb.PROP_RATING, 5.0)
                    changed=True
                    #print ">> Updating rating to 5.0"
                    
            if changed:
                #print ">> Committing change to database"
                self._db.commit()
                
        except Exception, e:
            print "!! Exception whilst updating track, msg=%s" % str(e)


_=Updater()
