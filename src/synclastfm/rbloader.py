"""
    Rhythmbox URL loader 
    Helpers 
    
    Created on 2010-01-13

    @author: jldupont
"""

import rb #@UnresolvedImport

class RbLoader(object):
    """
    Convenience class for accessing Rhythmbox's 
    URL loading facility 
    """
    def __init__(self):
        self._loader= rb.Loader()
    
    def __call__(self, url, callback):
        self._loader.get_url(url, callback)
