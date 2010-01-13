"""
    Simple Last.fm API
    
    Access to Last.fm web services that do not 
    require "session-level" authentication 

    @author: jldupont
"""

import urllib

class Sapi(object):
    """
    Simple Last.fm API
    """
    AP="http://ws.audioscrobbler.com/2.0/?"
        
    def __init__(self, api_key, loader):
        self._api_key=api_key
        self._loader=loader

    def __call__(self, callback, furl="", **params ):
        for k,v in params.items():
            furl += "%s=%s&" % (k,urllib.quote(v))
        furl += "api_key=%s" % self._api_key
        return self._loader(self.AP+furl, callback)

   
  

   
   
## ===================================================================== TESTS
   
if __name__ == "__main__":
    import urllib2
    
    class loader():
        def __call__(self, url, callback):
            print "loader: url: %s" % url
            r=urllib2.urlopen(url, timeout=5)
            data=r.read()
            callback(data)
    
    def callback(result):
        print "callback: %s" % result
    
    s=Sapi(api_key="b25b959554ed76058ac220b7b2e0a026", loader=loader())
    #s(callback=callback, method="track.getinfo", artist="Depeche Mode", track="Little 15", username="jldupont")
    s(callback=callback, method="user.getRecentTracks", user="jldupont")
