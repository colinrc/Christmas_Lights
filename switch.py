#!/bin/python3

import time
import queue
import threading
import datetime

class SwitchOn_Wait_SwitchOff:
    STOP='stop'
    START='start'
    
    def __init__(self, eventQueue, interval):
        self.init()
        self.eventQueue = eventQueue
        self.interval = interval
        self.runFlag = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
    def setInterval(self, interval):
        self.interval = interval
 
    def run(self):
        while self.runFlag:
            s = ""
            try:
                s = self.eventQueue.get(block=True,timeout=0.1)
            except queue.Empty:
                continue
            
            if s==self.STOP:
                self.stop()
                
            if s==self.START:
                self.start()
                
    def init(self):
        """ place your hardware init code here"""
        pass
    
    def close(self):
        """ place your hardware cleanup code here"""
        pass
    
    def terminate(self):
        """shutdown operation"""
        self.runFlag = False
        self.stop()
        self.close()
        
    def stop(self):
        """ terminate a running execution"""
        self._stopTimer()
        #
        # reset output pins
        #
        print("output RESET")
        
    def start(self):
        """ start timing action"""
        self._startTimer()
        #
        # set output pins
        #
        print("output SET")
    
    def _stopSignal(self):
        self.eventQueue.put(self.STOP) 
           
    def _startTimer(self):
        self.timer = threading.Timer(self.interval, self._stopSignal)
        self.timer.start()
        
    def _stopTimer(self):
        try:
            self.timer.cancel()
        except:
            pass
        
class TimeOfDayTrigger:
    """produce an event at a certain minute within 24h"""
    
    def __init__(self, eventQueue, strTime):
        """strTime is start time in 'HH:MM' format, 24hours"""
        self.eventQueue = eventQueue
        self.strTime = strTime
        print("TimeOfDayTrigger will trigger at " + strTime)
        self.runFlag = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
    def run(self):
        while self.runFlag:
            s = datetime.datetime.now().strftime('%H:%M')
            if s == self.strTime:
                self.eventQueue.put( SwitchOn_Wait_SwitchOff .START)
                time.sleep(61)
            time.sleep(0.1)
            
    def terminate(self):
        self.runFlag = False        

eventQueue = queue.Queue()
vt = SwitchOn_Wait_SwitchOff (eventQueue, 3)

# test code
#
print("TEST ########################################")
print("-- simple start")
eventQueue.put(SwitchOn_Wait_SwitchOff .START)
time.sleep(5)

print("TEST ########################################")
print("--  start, stop while running")
eventQueue.put(SwitchOn_Wait_SwitchOff .START)
time.sleep(1)
eventQueue.put(SwitchOn_Wait_SwitchOff .STOP)
# wait another some secs to see if sprious signals are running
time.sleep(5)

print("TEST ########################################")
print(" start a trigger event in two minute or so")
now = datetime.datetime.now()
two_minutes = datetime.timedelta(seconds=120) 
now_plus_two_minutes = now + two_minutes
startTime = now_plus_two_minutes.strftime('%H:%M')
tt = TimeOfDayTrigger(eventQueue, startTime)

print("wait for timer to trigger")
time.sleep(125)

print("TEST ########################################")
print("terminate program")
tt.terminate()
vt.terminate()

print("finished")