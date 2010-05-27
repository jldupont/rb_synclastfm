"""
    Finds an "entry" in the database

    @author: jldupont
    @date: May 27, 2010
"""

import gobject  #@UnresolvedImport

from bus import Bus


class FinderAgent(gobject.GObject):  #@UndefinedVariable

    def __init__(self): 
        gobject.GObject.__init__(self) #@UndefinedVariable

        Bus.add_emission_hook("entry", self.h_entry)

    def h_entry(self, _, entry):
        """
        Intercepts an "entry" and attempts to
        locate a corresponding "db entry"
        """
        

        

_=FinderAgent()
