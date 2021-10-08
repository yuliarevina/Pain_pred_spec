#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
=== Authors ===
Ulrike Horn: uhorn@cbs.mpg.de
Date: 16th July 2020

=== Description ===
This script demonstrates how continuous eyetracking can be done using pylink.
In this example experiment the eyetracker is started and calibration can be done via the psychopy computer.
Messages will be sent to the eyetracker when certain events happen - in this case every time a dot is shown 
instead of a fixation cross.
An .edf file is sent from the tracker via Ethernet and will be saved in a subfolder called data.
You can convert this into an asc file using edf2asc tool (srresearch-->eyelink-->utilities)

To run the script make sure the file EyeLinkCoreGraphicsPsychoPy.py is in the same folder as this script.
This script also includes a dummy mode so that you can adapt this code and don't need the eyetracker running for testing.

Things you might want to adapt to your setting:
    line 60: filename and folder where your .edf file is saved
    line 71: set screen properties to your resolution
    lines 115-116: change the calibration/validation_area_proportion to smaller values if you have a large screen 
"""

from psychopy import data, visual, core, event, gui, monitors
import os, sys # handy system and path functions
import random # to randomly choose sides to display the dot
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

#-------------------------------------------
dummyMode = True  
# True = simulated connection to eyetracker, 
# False = real connection to eyetracker
#-------------------------------------------

iti_time = 4 # time the fixation cross will be shown (s)
dot_time = 4 # time a dot will be shown to the left or right (s)
num_trials = 5 # number of trials this will be done

# Establish a link to the tracker
if not dummyMode:
    tk = pylink.EyeLink('100.1.1.1')
else:
    tk = pylink.EyeLink(None)

# ==============================================================
# preparation
# ==============================================================
# Ensure that relative paths start from the same directory as this script
thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(thisDir)

# Make data folder
if not os.path.isdir("data"):
    os.makedirs("data")

# filename with time stamp
timestamp = data.getDateStr(format='%Y%m%d_%H%M')
filename = thisDir + os.sep + 'data' + os.sep + 'eyetracking_demo_%s' % (timestamp) + '.edf'

# in the DOS system you can only store up to 8 characters for the file name 
edf_running_name = 'demo.EDF'

# open data file
tk.openDataFile(edf_running_name)
# add personalized data file header (preamble text)
tk.sendCommand("add_file_preamble_text 'Eyetracking Demo'")

# set screen properties
scnWidth, scnHeight = (1920, 1080)

# define monitor for correct eye tracking
mon = monitors.Monitor('basement', width=53.0, distance=46.0)
mon.setSizePix((scnWidth, scnHeight))

# experimenter monitor
winexp = visual.Window((1500, 800), fullscr=False, screen=0, color=[0.404, 0.404, 0.404], units='pix',
                       allowStencil=True, autoLog=False, waitBlanking=False)
# subject monitor
win = visual.Window((scnWidth, scnHeight), fullscr=False, monitor = mon, screen=1, color=[0.404, 0.404, 0.404],
                    units='pix', allowStencil=True, autoLog=False, waitBlanking=False, allowGUI=False)

# call the custom calibration routine "EyeLinkCoreGraphicsPsychopy.py", instead of the default
# routines that were implemented in SDL
genv = EyeLinkCoreGraphicsPsychoPy(tk, win)
pylink.openGraphicsEx(genv)

# create objects
fixation= visual.TextStim(win=win, text='+',pos=(0.0, 0.0), 
    color='black',height=100, alignHoriz='center', 
    alignVert='center',autoLog=False)
dotObj = visual.Circle(win=win, fillColor="white", 
    lineColor="white", radius=[12, 12], units="pix", pos=[0, 0])
textObjExp = visual.TextStim(winexp, units="pix", 
    text="", color="black", height=20)
    
# Create some timers to manage the timing of routines within one trial
routineClock = core.Clock() # runs forwards
routineTimer = core.CountdownTimer()  # runs backwards


# ==============================================================
# set up tracker
# ==============================================================
tk.setOfflineMode()  # we need to put the tracker in offline mode before we change its configurations
tk.sendCommand('sample_rate 1000')  # 250, 500, 1000
# inform the tracker the resolution of the subject display
tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (scnWidth - 1, scnHeight - 1))
# save display resolution in EDF data file for Data Viewer integration purposes
tk.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (scnWidth - 1, scnHeight - 1))
# specify the calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical), 
tk.sendCommand("calibration_type = HV9")  # default HV9
# specify the proportion of subject display to calibrate/validate (OPTIONAL, useful for wide screen monitors)
tk.sendCommand("calibration_area_proportion 0.85 0.83") # default 0.85 0.83
tk.sendCommand("validation_area_proportion  0.85 0.83") # default 0.85 0.83
# the model of the tracker, 1-EyeLink I, 2-EyeLink II, 3-Newer models (1000/1000Plus/DUO)
eyelinkVer = tk.getTrackerVersion()
# Set the tracker to parse Events using "GAZE" (or "HREF") data
tk.sendCommand("recording_parse_type = GAZE")
# Online parser configuration: 0-> standard/cognitive, 1-> sensitive/psychophysiological
# [see Eyelink User Manual, Section 4.3: EyeLink Parser Configuration]
if eyelinkVer >= 2:
    tk.sendCommand('select_parser_configuration 0')
# get Host tracking software version
hostVer = 0
if eyelinkVer == 3:
    tvstr = tk.getTrackerVersionString()
    vindex = tvstr.find("EYELINK CL")
    hostVer = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
# specify the EVENT and SAMPLE data that are stored in EDF or retrievable from the Link
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT")
if hostVer >= 4:
    tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
    tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
else:
    tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,INPUT")
    tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT")


# ==============================================================
# Experiment start
# ==============================================================
# Experimenter starts by pressing space
textObjExp.setText(u"Press space to start experiment\n")
textObjExp.setHeight(20)
textObjExp.draw()
winexp.flip()
event.waitKeys(keyList=["space"])

textObjExp.setText("Press enter to show the eye on the subject's screen, \nstart calibration with C, validation with V, record with O")
textObjExp.draw()
winexp.flip()

if not dummyMode:
    # set up the camera and calibrate the tracker at the beginning of each block
    tk.doTrackerSetup()

# take the tracker offline
tk.setOfflineMode()
pylink.pumpDelay(50)

# send the standard "TRIALID" message to mark the start of a trial
# [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
# this is more important for trialwise recording, in this case we anyway record continuously
tk.sendMessage('TRIALID')

# start recording, parameters specify whether events and samples are
# stored in file, and available over the link
error = tk.startRecording(1, 1, 1, 1)
pylink.pumpDelay(100)  # wait for 100 ms to make sure data of interest is recorded

# loop through trials
for i in range(0,num_trials):
    
    # ==============================================================
    # ITI - showing a fixation cross
    # ==============================================================
    routineClock.reset()
    routineTimer.reset()
    routineTimer.add(iti_time)
    
    # have the objects been initialized
    init = False
    
    # for the time consuming stuff that needs to be done before the next routine
    win_exp_flip = False
    prepared = False
    
    # -------Start Routine "iti"-------
    while routineTimer.getTime() > 0:
        # get current time
        t = routineClock.getTime()
        
        # draw fixation cross
        if t >= 0 and not init:
            fixation.draw()
            win.flip()
            # send message to tracker when ITI begins
            tk.sendMessage('iti_onset')
            init = True
        
        # update experimenter window (timing not critical)
        if t >= 0.1 and not win_exp_flip:
            textObjExp.setText('fixation')
            textObjExp.draw()
            winexp.flip()
            win_exp_flip = True
        
        # prepare event phase and randomly choose side to show dot
        if t >= 0.2 and not prepared:
            if random.randint(0,1) == 1:
                dotObj.pos = (50,0)
                currentPos = 'right'
            else:
                dotObj.pos = (-50,0)
                currentPos = 'left'
            prepared = True
    
    # ==============================================================
    # Event: showing a dot to the left or right side
    # ==============================================================
    routineClock.reset()
    routineTimer.reset()
    routineTimer.add(dot_time)
    
    # have the objects been initialized
    init = False
    
    # for the time consuming stuff that needs to be done before the next routine
    win_exp_flip = False
    
    # -------Start Routine "event"-------
    while routineTimer.getTime() > 0:
        # get current time
        t = routineClock.getTime()
        
        # draw dot
        if t >= 0 and not init:
            dotObj.draw()
            win.flip()
            # send message to tracker which event is happening
            tk.sendMessage(currentPos)
            init = True
        
        # update experimenter window (timing not critical)
        if t >= 0.1 and not win_exp_flip:
            textObjExp.setText(currentPos)
            textObjExp.draw()
            winexp.flip()
            win_exp_flip = True


# send a message to mark the end of trial
# [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
tk.sendMessage('TRIAL_RESULT')
pylink.pumpDelay(100)
tk.stopRecording()  # stop recording

# Get the EDF data file
tk.setOfflineMode()
tk.closeDataFile()
pylink.pumpDelay(50)
tk.receiveDataFile(edf_running_name, filename)

# close the link to the tracker
tk.close()

# close everything
pylink.closeGraphics()
winexp.close()
win.close()
core.quit()
