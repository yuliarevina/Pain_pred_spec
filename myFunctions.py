#!/usr/bin/env python2
# -*- coding: utf-8 -*-



from psychopy import core, clock, visual, event, monitors, data
import pandas as pd
import time, numpy, os, sys
import matplotlib.pyplot as plt # for plotting the results



#plt.interactive(True)

def showText(window, myText, myColor): 
    message = visual.TextStim(win=window, text=myText, font='Arial', color=myColor, units="pix", height=50)
    message.draw()
    
def showFix(window, myText, myColor): 
    message = visual.TextStim(win=window, text=myText, font='Arial', color=myColor, units="pix", height=100)
    message.draw()
    
def showDebugText(window, text, position, whichcomp):
    if whichcomp == "Home":
        message = visual.TextStim(window, text=text,
        font='Adler', pos=position, 
        color=(1.0, 1.0, 1.0), units="pix",
        height=50, anchorHoriz="center", 
        anchorVert="center")
        message.draw()
    else:
        message = visual.TextStim(window, text=text,
        font='Arial', pos=position, 
        color=(1.0, 1.0, 1.0), units="pix",
        height=50, anchorHoriz="center", 
        anchorVert="center")
        message.draw()
        
        
def Eyetracking_calibration(filenameeyetrack, tk, win, winexp, scnWidth, scnHeight, dummyMode):
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
    # ==============================================================
    # preparation
    # ==============================================================
    # Ensure that relative paths start from the same directory as this script
#    thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
#    os.chdir(thisDir)
#    
#    # Make data folder
#    if not os.path.isdir("data"):
#        os.makedirs("data")
    
    # filename with time stamp
    #timestamp = data.getDateStr(format='%Y%m%d_%H%M')
    #filenameeyetrack = thisDir + os.sep + 'data' + os.sep + 'eyetracking_%s' % (timestamp) + str(sub) + str(sex) + str(age) + str(sessiontype) +'.edf'
    
    # in the DOS system you can only store up to 8 characters for the file name 
    edf_running_name = 'data.EDF'
    
    # open data file
    tk.openDataFile(edf_running_name)
    # add personalized data file header (preamble text)
    tk.sendCommand("add_file_preamble_text 'Eyetracking Data'")
    
    
#    # define monitor for correct eye tracking
#    mon = monitors.Monitor('basement', width=53.0, distance=46.0)
#    mon.setSizePix((scnWidth, scnHeight))
    
    # call the custom calibration routine "EyeLinkCoreGraphicsPsychopy.py", instead of the default
    # routines that were implemented in SDL
    genv = EyeLinkCoreGraphicsPsychoPy(tk, win)
    pylink.openGraphicsEx(genv)
    
    
    # create objects
    fixation= visual.TextStim(win=win, text='+',pos=(0.0, 0.0), 
        color='black',height=100, anchorHoriz='center', 
        anchorVert='center',autoLog=False)
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
    tk.sendCommand("calibration_area_proportion 0.65 0.63") # default 0.85 0.83
    tk.sendCommand("validation_area_proportion  0.65 0.63") # default 0.85 0.83
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
    # Eyetracking start
    # ==============================================================
    # Experimenter starts by pressing space
    textObjExp.setText(u"Press space to start eyetracking\n")
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
    tk.sendMessage('Start Rec') 
    # to send a message to the tracler (for log file)
    #tk.sendMessage("Message")
    
    # to stop recording
    #tk.stopRecording()  # stop recording       
    return tk, edf_running_name    
