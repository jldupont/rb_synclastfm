"""
    User class
    
    @author: jldupont
"""
import gconf    #@UnresolvedImport
import gobject  #@UnresolvedImport

## locals
from bus import Bus

class LastFmUser(gobject.GObject): 
    """
    A Last.fm user proxy
    
    Currently, the user parameters are only retrieved 
    from Rhythmbox's Gnome configuration directory 
    """
    __gproperties__ = {
        "username":  (gobject.TYPE_STRING, "username on Last.fm", 
                     "username property of the user on Last.fm", "", gobject.PARAM_READWRITE)
        ,"password": (gobject.TYPE_STRING, "password on Last.fm", 
                     "password property of the user on Last.fm", "", gobject.PARAM_READWRITE)
        
    }

    PATH="/apps/rhythmbox/audioscrobbler/%s"
    
    def __init__(self, username=None, password=None):
        gobject.GObject.__init__(self)
        self._username=username
        self._password=password
        
    def refresh(self):
        """
        Attempts to refresh the user information
        """
        client=gconf.client_get_default()
        self._username=client.get_string(self.PATH % "username")
        self._password=client.get_string(self.PATH % "password")
        self._announceChanges()
          
    def do_get_property(self, property):
        """
        GObject get
        """
        if property.name == "username":
            if not self._username:
                self.refresh()
            return self._username
        
        if property.name == "password":
            if not self._password:
                self.refresh()
            return self._password
        
        raise AttributeError("unknown property %s" % property.name)

    def do_set_property(self, property, value):
        """
        GObject set
        """
        if property.name == "username":
            self._username = value
            self.emit("lastfm_username_changed", self.get_property("username"))            
            return value
        
        if property.name == "password":
            self._password = value
            self.emit("lastfm_password_changed", self.get_property("password"))            
            return value
        
        raise AttributeError("unknown property %s" % property.name)
      
    def _announceChanges(self):
        Bus.emit("lastfm_username_changed", self.get_property("username"))
        Bus.emit("lastfm_password_changed", self.get_property("password"))
      

gobject.type_register(LastFmUser)
        
lfmuser=LastFmUser()
lfmuser.refresh()


## ==================================================================== TESTS

if __name__=="__main__":
    u=LastFmUser()
    
    print "Username: %s , password: %s" % ( u.get_property("username"), u.get_property("password") )

    def callback(self, data):
        print "callback, data=%s" % str(data)
        
    Bus.add_emission_hook("lastfm_username_changed", callback)
    Bus.add_emission_hook("lastfm_password_changed", callback)
    
    u.refresh()
    
