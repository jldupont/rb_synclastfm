"""
    Custom Data Types
    
    @author: jldupont
    @date: Jun 1, 2010
"""
import uuid

__all__=["BoundedDict", "SimpleStore"]

class BoundedDict(object):
    """
    >>> bd=BoundedDict(2)
    >>> bd["e1"]="element1"
    >>> bd["e2"]="element2"
    >>> print bd["e1"]
    element1
    >>> print bd["e2"]
    element2
    >>> bd["e1"]="element1"
    >>> bd["e2"]="element2"
    >>> bd["e3"]="element3"
    
    Element was bumped & flushed:
    >>> print bd["e1"]
    Traceback (most recent call last):
        ...
    KeyError: 'e1'
    >>> print bd["e2"]
    element2
    >>> print bd["e3"]
    element3
    
    Destructive get already performed:
    >>> print bd["e2"]
    Traceback (most recent call last):
        ...
    KeyError: 'e2'
    """
    
    def __init__(self, size=10, destructive=True):
        self.size=size
        self.dic={}
        self.lru=[]
        self.destructive=destructive
       
    def __getitem__(self, key):
        """
        Destructive 'get'
        """
        ## fail if we don't have the element 
        el=self.dic[key]
        
        ## but clean-up nicely if necessary
        if self.destructive:
            try:    
                self.lru.remove(key)
                del self.dic[key]
            except: pass
        
        return el
        
    def __setitem__(self, key, value):
        """
        Set item whilst checking for overflow
        
        Flush the 'least recently used' entry on overflow
        """
        ## check overflow first:
        ##  if we don't have any slot, bump the lru
        if len(self.lru) >= self.size:
            self._flushOne()
    
        self.lru.append(key)
        self.dic[key]=value
            
    def _flushOne(self):
        key=self.lru.pop(0)
        
        ## shouldn't occur... paranoia
        try:    del self.dic[key]
        except: pass
    
    def csize(self):
        return len(self.lru)
    

class SimpleStore(object):
    """
    >>> ss=SimpleStore(2)
    >>> key=ss.store("zelement")
    >>> print ss.retrieve(key)
    zelement
    >>> print ss.retrieve(key)         # doctest:+ELLIPSIS
    Traceback (most recent call last):
        ...
    KeyError: ...
    """
    def __init__(self, size=10, destructive=True):
        self.bd=BoundedDict(size, destructive)
        
    def store(self, element, key=None):
        """
        Store an 'element' with a unique key
        
        The key can either be specified or chosen
        randomly.
        
        @param element: an element to store
        @param key: a unique key OR None
        @return ukey: unique key
        """
        if key is None:
            ukey=str(uuid.uuid4())
        else:
            ukey=key

        self.bd[ukey]=element
        return ukey
    
    def retrieve(self, key):
        """
        Retrieves an 'element'
        
        >>> ss=SimpleStore(2)
        >>> ss.csize()
        0
        
        Raises 'KeyError' exception if not found
        """
        return self.bd[key]
    
    def csize(self):
        return self.bd.csize()
        
if __name__=="__main__":
    
    import doctest
    doctest.testmod()
    
    
    