"""
    User class
    
    @author: jldupont
"""
import gconf

class User(object):
    """
    A Last.fm user proxy
    
    Currently, the user parameters are only retrieved 
    from Rhythmbox's Gnome configuration directory 
    """
    
    PATH="/apps/rhythmbox/audioscrobbler/%s"
    
    def __init__(self, username=None, password=None):
        self._username=username
        self._password=password
        
    def refresh(self):
        """
        Attempts to refresh the user information
        """
        client=gconf.client_get_default()
        self._username = client.get_string(self.PATH % "username")
        self._password = client.get_string(self.PATH % "password")
      
    def _setusername(self, value):
        self._username=value
        
    def _setpassword(self, value):
        self._password=value
        
    def _getusername(self):
        if not self._username:
            self.refresh()
        return self._username
    
    def _getpassword(self):
        if not self._password:
            self.refresh()
        return self._password
    
    username=property(fget=_getusername, fset=_setusername)    
    password=property(fget=_getpassword, fset=_setpassword)
    
    

if __name__=="__main__":
    u=User()
    print "Username: %s , password: %s" %( u.username, u.password )
