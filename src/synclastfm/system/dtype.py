"""
    Custom Data Types
    @author: jldupont
    @date: Jun 1, 2010
"""

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
    
    def __init__(self, size=10):
        self.size=size
        self.dic={}
        self.lru=[]
       
    def __getitem__(self, key):
        """
        Destructive 'get'
        """
        ## fail if we don't have the element 
        el=self.dic[key]
        
        ## but clean-up nicely if necessary
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
    
        
if __name__=="__main__":
    
    import doctest
    doctest.testmod()
    
    
    