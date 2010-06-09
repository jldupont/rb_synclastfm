"""
    Timer Agent
    
    MESSAGES IN:
    - "tick"
    
    MESSAGES OUT:
    - "timer_second"
    - "timer_minute"
    - "timer_hour"
    - "timer_day"

    @author: jldupont

    Created on Jun 9, 2010
"""
from synclastfm.system.mbus import Bus

class Timer(object):

    def __init__(self):
        self.freq=0
        
        self.tcount=0
        self.scount=0
        self.mcount=0
        self.hcount=0
        self.dcount=0
        
        Bus.subscribe(self.__class__, "tick",          self.h_tick)
        Bus.subscribe(self.__class__, "tick_params",   self.h_tick_params)

    def h_tick_params(self, freq):
        self.freq=freq

    def h_tick(self, *_):
        self.tcount += 1
        if self.tcount == self.freq:
            self.tcount = 0
            self.scount += 1
            Bus.publish(self.__class__, "timer_second", self.scount)
        
        if self.scount == 60:
            self.scount = 0
            self.mcount += 1
            Bus.publish(self.__class__, "timer_minute", self.mcount)
            
        if self.mcount == 60:
            self.mcount = 0
            self.hcount += 1
            Bus.publish(self.__class__, "timer_hour", self.hcount)
            
        if self.hcount == 24:
            self.hcount = 0
            self.dcount += 1
            Bus.publish(self.__class__, "timer_day", self.dcount)


_=Timer()
