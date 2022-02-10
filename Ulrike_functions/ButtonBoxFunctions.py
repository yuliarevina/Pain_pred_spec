#!/usr/bin/env python
# -*- coding:utf-8 -*-

#    === Authors ===
# Ulrike Horn
# uhorn@cbs.mpg.de

#    === Description ===
# Functions to use the button boxes with the parallel port in Psychopy
# These button boxes send their signals via the data pins and we can assign
# values 1 to 4 to the four buttons and record reaction times
#
# Example usage:
#
# import ButtonBoxFunctions as bb
# from psychopy import core
#
# timer = core.Clock()
# bbox = bb.ButtonBox(port = 0, clock = timer)
# k = bbox.waitButtons(maxWait=2, timeStamped=timer)
# print(k)

import parallel # for interaction with parallel port
import psychopy # for the clock

class ButtonBox:
    """
    With this class you can store the previous key presses so that
    longer down times are recognized as one event.
    
    """

    def __init__(self, port=0, clock=None):
        # initialize the button box object with a specific parallel port (default first one)
        if isinstance(port, int):
            self.p_port = parallel.Parallel(port = port)
            # The 'out' parameter indicates the desired port direction.  If
            #'out' is true or non-zero, the drivers are turned on (forward
            #direction, for writing); otherwise, the drivers are turned off (reverse
            #direction, so that the peripheral drives the signal).
            self.p_port.PPDATADIR(0)
        elif hasattr(port, 'PPDATADIR'):
            self.p_port = port
        else:
            raise ValueError('You did not enter a valid port object or number!')
        # define a clock that will be linked to the device so that presses can be time stamped
        # you can take your own clock or the one that has been started when initializing the object
        self.timeStamped = True
        if clock:
            if hasattr(clock, 'getTime'):
                self.clock = clock
            else:
                print('The clock is not correctly defined. No time stamps are recorded')
                self.clock = psychopy.core.Clock()
                self.timeStamped = False
        else:
            self.clock = psychopy.core.Clock()
        # initialize presses and down times for all four buttons
        self.keystates = [0]*4
        self.times = [0]*4
        # set a debounce time that tells us how quickly after an event a next event
        # should be recorded to be plausible
        self.debounce = 0.005 # in s


    def reset(self):
        """
        Use this when you reset the timer or clear previous keypresses
        
        """
        # initialize presses and down times for all four buttons
        self.keystates = [0]*4
        self.times = [0]*4

    def getButtons(self, keyList=None, timeStamped=False, reportRelease=False):
        """
        
        Returns a list of button presses (similar to getKeys function in psychopy events)
        keyList is a list of keys you want to watch out for, others are then not reported,
        timeStamped uses the defined clock to return time stamps with the button presses,
        instead of returning the results when a key is pressed one can also report releases,
        then an additional duration value is returned
        
        It is important that we implement a debounce delay that matches the device
        so that mechanically caused noise in the signal (on/off/on although continuously pressing)
        is ignored
        
        :Parameters:
        keyList: **None** or []
            Allows the user to specify a set of keys to check for.
            Only presses from this set of keys will be reported.
            Default is None and all keys will be checked.
        timeStamped: **False** or True or Clock
            If True will return a list of tuples instead of a list of
            keynames with timestamps added.
            The user can also give a specific clock so that the time stamps
            relate to the last reset of that clock. This can be a different clock
            than the one with which it was initialized.
        reportRelease: **False** or True
            If True will return the time when certain buttons were released.
            Default is False and the time of button press is reported.
        
        """
        # user provides a new clock to be associated
        if hasattr(timeStamped, 'getTime'):
            self.clock = timeStamped
            self.timeStamped = True
            timeStamped = True
        # if the clock was not valid do not record time stamps even if demanded
        if not self.timeStamped:
            timeStamped = False
        
        # read data
        input = self.p_port.PPRDATA()
        # store the new keys
        curr_keystates = [0]*4
        # code keys as numbers, zero means press
        for pinNumber in range(2,6):
            pinState = (input >> (pinNumber - 2)) & 1
            if not pinState:
                curr_keystates[pinNumber-2] = 1
        # store time
        curr_time = self.clock.getTime()
        # check whether something has changed
        # and whether the last event has happened more than debounce time ago
        durations = [0]*4
        newKeys = []
        lostKeys = []
        lostKeysFirstPress = []
        lostKeysDurations = []
        for ind,state in enumerate(curr_keystates):
            durations[ind] = curr_time - self.times[ind]
            if (state != self.keystates[ind]) and (durations[ind] > self.debounce):
                # update the key state and time of event
                self.keystates[ind] = state
                self.times[ind] = curr_time
                if state==1:
                    #print('new key')
                    newKeys.append(ind)
                else:
                    #print('lost key')
                    lostKeys.append(ind)
                    lostKeysFirstPress.append(self.times[ind])
                    lostKeysDurations.append(durations[ind])
        # what to return depends on the settings
        # remember to subtract the debounce time because everything that has been
        # stored was stored after that delay
        if reportRelease and len(lostKeys)!=0:
            keysToReturn = lostKeys
            timesToReturn = [x - self.debounce for x in lostKeysFirstPress]
            durationsToReturn = lostKeysDurations
        elif (not reportRelease) and len(newKeys)!=0:
            keysToReturn = newKeys
            timesToReturn = [(curr_time - self.debounce) for i in range(len(keysToReturn))]
            durationsToReturn = [None for i in range(len(keysToReturn))]
        else:
            return None
        # if there is something to return check whether there was a keylist to 
        # filter these returns
        if keyList:
            j = [i for i, val in enumerate(keysToReturn) if val not in keyList]
            for k in reversed(j):
                del(keysToReturn[k])
                del(timesToReturn[k])
                del(durationsToReturn[k])
        # does the user want just the key or a tuple with the time?
        if timeStamped == False:
            return keysToReturn
        else:
            tuples = list(zip(keysToReturn,timesToReturn))
            return tuples
    
    
    def waitButtons(self, maxWait=float('inf'), keyList=None, timeStamped=False, reportRelease=False):
        """
        This function waits a particular amount of time for button presses
        similar to waitKeys function,
        by calling it, the associated clock is reset
        
        :Parameters:
        maxWait: any numeric value.
            Maximum number of seconds to wait for.
            Default is float('inf') which simply waits forever.
        keyList: **None** or []
            Allows the user to specify a set of keys to check for.
            Only presses from this set of keys will be reported.
            Default is None and all keys will be checked.
        timeStamped: **False** or True
            If True will return a list of tuples instead of a list of
            keynames with timestamps added.
        reportRelease: **False** or True
            If True will return the time when certain buttons were released.
            Default is False and the time of button press is reported.
        
        """
        self.clock.reset()
        self.reset()
        got_keypress = False
        while not got_keypress and self.clock.getTime() < maxWait:
            key_presses = self.getButtons(keyList=keyList, timeStamped=timeStamped, reportRelease=reportRelease)
            if key_presses:
                got_keypress = True
        if got_keypress:
            return key_presses
        else:
            return None



