"""
    @author: jldupont
    @date: May 27, 2010
"""
import rhythmdb  #@UnresolvedImport

import gobject #@UnresolvedImport
from bus import Bus


class LastfmSqlite(gobject.GObject): #@UndefinedVariable
    """
    Updates various properties
    """
    def __init__(self):
        gobject.GObject.__init__(self) #@UndefinedVariable
        self._shell=None
        self._db=None
        self._robjects=None
        
        Bus.add_emission_hook("rb_shell",        self.on_rb_shell)
        
    def on_rb_shell(self, _signal, rbobjects):
        """
        Grab RB objects references (shell, db, player)
        
        GObject handler
        """
        self._robjects=rbobjects
        self._db=self._robjects.db
        return True
        


gobject.type_register(LastfmSqlite) #@UndefinedVariable
_=LastfmSqlite()
