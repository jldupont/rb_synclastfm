"""
    Created on 2010-01-13

    @author: jldupont
"""
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import StringIO
    
__all__=["processResponse"]

def processResponse(data):
    """
    Processes a response from Last.fm API
    
    @return: dict or None on error 
    """
    bus=HandlerBus()
    tih=TrackInfoHandler()
    bus.add(tih)
    
    par=make_parser()
    par.setContentHandler(bus)
    sio=StringIO.StringIO(data)
    
    try:
        par.parse(sio)
        return tih.props
    except:
        return None
    

class HandlerException(Exception):
    """
    Generic Handler exception
    """

class HandlerBus(ContentHandler):
    """
    Distributes the XML parsing events 
    to the registered objects
    """
    def __init__(self):
        self._regs=[]
        
    def add(self, reg):
        self._regs.append(reg)
        
    def startElement(self, name, attrs):
        for r in self._regs:
            r.startElement(name, attrs)
    
    def characters(self, ch):
        for r in self._regs:
            r.characters(ch)
                
    def endElement(self, name):
        for r in self._regs:
            r.endElement(name)
            

class TrackInfoHandler(object):
    """
    TrackInfo response handler
    """
    
    def __init__(self):
        self._state="begin"
        self._acc=""
        self.valid=False
        self.props={"track.tags":[]}
    
    ## ================================== Event callbacks
    
    def startElement(self, tag, attrs):
        self._dispatch(("startElement", tag, attrs))
    
    def characters(self, ch):
        self._acc+=ch
                
    def endElement(self, tag):
        self._dispatch(("endElement", tag, self._acc.strip()))
        self._acc=""
    
    ## ===================================
    def _missingState(self, _event):
        raise HandlerException("missing state(%s)" % self._state)
    
    def _dispatch(self, event):
        methodName="_st_"+self._state
        getattr(self, methodName, self._missingState)(event)
        
    ## =================================== State related handlers
    
    def _st_begin(self, (e, name, _)):
        """
        Initial state
        lfm -> skip to track
        """
        if (e != "startElement"):
            self._state="stop"
            return
        
        if (name != "lfm"):
            self._state="stop"
            return
        
        self._state="wait_track"
        
    def _st_wait_track(self, (e, name, _v)):
        if (e!="startElement"):
            self._state="stop"
            return
        if (name!="track"):
            self._state="stop"
            return
            
        self._state="wait_track_child"
        
    _track_childs = ["id", "name", "mbid", "url",
                     "duration", "userplaycount", "userloved"
                     ]
        
    def _st_wait_track_child(self, (e, name, v)):
        #print "wait_track_child: e(%s) name(%s) v(%s)" % (e, name, v)
        if (e=="endElement"):
            if name in self._track_childs:
                self.props["track.%s" % name] = v
                self.valid=True                
                return

        if (e=="startElement"):
            if (name=="artist"):
                self._state="wait_track_artist"
                return
            if (name=="album"):
                self._state="wait_track_album"
                return
            if (name=="toptags"):
                self._state="wait_tags"
                return

    _track_artist_childs = ["name", "mbid", "url"]

    def _st_wait_track_artist(self, (e, name, v)):
        if (e=="endElement"):
            if (name=="artist"):
                self._state="wait_track_child"
                return

            if name in self._track_artist_childs:
                self.props["track.artist.%s" % name] = v
                self.valid=True
                return

    _track_album_childs= ["artist", "title", "mbid", "url"]
                
    def _st_wait_track_album(self, (e, name, v)):
        if (e=="endElement"):
            if (name=="album"):
                self._state="wait_track_child"
                return

            if name in self._track_album_childs:
                self.props["track.album.%s" % name] = v
                self.valid=True
                return

    def _st_wait_tags(self, (e, name, v)):
        if (e=="endElement"):
            if (name=="toptags"):
                self._state="wait_track_child"
                return
        
        if (e=="endElement"):
            if (name=="name"):
                self.props["track.tags"].append(v)


    def _st_stop(self, _event):
        pass
        
    


class gHandler(ContentHandler):
    """
    Generic handler - not used at the moment
    
    The OP must be a callable object instance i.e.
    implement the __call__ method.
    """
    
    def __init__(self, output, dropTopLevel=True):
        """
        @param output: output handler, callable
        """
        self.output=output
        self.acc=""
        self.stack=[]
        self.current=None
        self.count=0
        self.prev=[]
        self.attrs=None
        self.topLevel=True
        self.dropTopLevel=dropTopLevel
      
    def startElement(self, _name, _attrs):
        
        self.attrs=_attrs
        # just in case somebody at somepoint
        # slips/forgets a case...
        name=_name.lower()


        #adjust tag occurence context        
        try:    prev=self.prev.pop()
        except: prev=(None, 0)
        
        pName, pCount = prev

        if name==pName:
            self.count=pCount+1
        else:
            self.count=0
            
        self.stack.append((name, self.count))
        
        #Top level related
        if self.topLevel and self.dropTopLevel:
            self.output((self.stack, _attrs, None))
            self.stack.pop()
            self.attrs = None
        self.topLevel=False
        
                
    def characters(self, ch):
        """
        Run an accumulator because we can't trust
        the SAX parser to return all the 'characters'
        of an element in one go
        """
        self.acc+=ch


    def endElement(self, _name):
        self.acc = self.acc.strip()
        
        if self.acc:
            self.output((self.stack, self.attrs, self.acc))
            self.acc=""
        
        self.attrs= None
        
        #top level might have been dropped
        try:    self.prev.append( self.stack.pop() )
        except: pass
        




## ================================================== Tests

if __name__=="__main__":

    r_track_info = """
<lfm status="ok">
<track>
    <id>12150</id>
    <name>Little 15</name>
    <mbid></mbid>
    <url>http://www.last.fm/music/Depeche+Mode/_/Little+15</url>
    <duration>255000</duration>
    <streamable fulltrack="0">0</streamable>    
    <listeners>98391</listeners>
    <playcount>400988</playcount>
    <userplaycount>9</userplaycount>    
    <userloved>0</userloved>
    <artist>
        <name>Depeche Mode</name>
        <mbid>8538e728-ca0b-4321-b7e5-cff6565dd4c0</mbid>
        <url>http://www.last.fm/music/Depeche+Mode</url>
    </artist>
    <album position="5">
        <artist>Depeche Mode</artist>
        <title>Music for the Masses</title>
        <mbid>8d059e75-d9bb-4d90-97a9-1cb6ed7472c6</mbid>
        <url>http://www.last.fm/music/Depeche+Mode/Music+for+the+Masses</url>        
        <image size="small">http://userserve-ak.last.fm/serve/64s/27272219.jpg</image>
        <image size="medium">http://userserve-ak.last.fm/serve/126/27272219.jpg</image>
        <image size="large">http://userserve-ak.last.fm/serve/174s/27272219.jpg</image>
        <image size="extralarge">http://userserve-ak.last.fm/serve/300x300/27272219.jpg</image>
    </album>
    <toptags>
        <tag>
          <name>electronic</name>
          <url>http://www.last.fm/tag/electronic</url>
        </tag>
        <tag>
          <name>new wave</name>
          <url>http://www.last.fm/tag/new%20wave</url>
        </tag>
        <tag>
          <name>synthpop</name>
          <url>http://www.last.fm/tag/synthpop</url>
        </tag>
        <tag>
          <name>80s</name>
          <url>http://www.last.fm/tag/80s</url>
        </tag>
        <tag>
          <name>depeche mode</name>
          <url>http://www.last.fm/tag/depeche%20mode</url>
        </tag>
      </toptags>
    </track></lfm>
"""


    r_user_getrecenttracks = """
<lfm status="ok">
    <recenttracks user="jldupont" page="1" perPage="10" totalPages="2508">
        <track nowplaying="true"> 
            <artist mbid="8385f26a-f374-4a04-9aad-4442ce24db2b">VNV Nation</artist>
            <name>Electronaut</name>
            <streamable>0</streamable>
            <mbid></mbid>
            <album mbid="df74a01a-ba9f-45a7-a71f-e6b624777a24">Futureperfect</album>
            <url>http://www.last.fm/music/VNV+Nation/_/Electronaut</url>
            <image size="small">http://userserve-ak.last.fm/serve/34s/8634449.jpg</image>
            <image size="medium">http://userserve-ak.last.fm/serve/64s/8634449.jpg</image>
            <image size="large">http://userserve-ak.last.fm/serve/126/8634449.jpg</image>
            <image size="extralarge">http://userserve-ak.last.fm/serve/300x300/8634449.jpg</image>
        </track>
        <track> 
            <artist mbid="8385f26a-f374-4a04-9aad-4442ce24db2b">VNV Nation</artist>
            <name>Airships</name>
            <streamable>0</streamable>
            <mbid></mbid>
            <album mbid="df74a01a-ba9f-45a7-a71f-e6b624777a24">Futureperfect</album>
            <url>http://www.last.fm/music/VNV+Nation/_/Airships</url>
            <image size="small">http://userserve-ak.last.fm/serve/34s/8634449.jpg</image>
            <image size="medium">http://userserve-ak.last.fm/serve/64s/8634449.jpg</image>
            <image size="large">http://userserve-ak.last.fm/serve/126/8634449.jpg</image>
            <image size="extralarge">http://userserve-ak.last.fm/serve/300x300/8634449.jpg</image>
            <date uts="1263411156">13 Jan 2010, 19:32</date>
        </track>
</recenttracks></lfm>
"""

    """
    class DebugProc():
        def __call__(self, (key, attrs, value)):
            print "key: %s, value:%s" % (key, value)
            
    from xml.sax import make_parser 
    par=make_parser()
    
    dp=DebugProc()
    gh=gHandler(dp)
    
    par.setContentHandler(gh)
    
    import StringIO
    sio=StringIO.StringIO(r_track_info)
    par.parse(sio)
    
    """
    bus=HandlerBus()
    tih=TrackInfoHandler()
    bus.add(tih)
    
    par=make_parser()
    par.setContentHandler(bus)
    sio=StringIO.StringIO(r_track_info)
    #sio=StringIO.StringIO(r_user_getrecenttracks)
    par.parse(sio)
    
    print tih.props
