#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from psychopy import core, clock, data, visual, event, gui, monitors, logging #parallel
import csv, random, time, numpy, sys, platform, os
from pyglet.window import key
import matplotlib.pyplot as plt # for plotting the results
import parallel
from scipy.io import savemat

logging.console.setLevel(logging.WARNING)


#########
# Stuff still to add

# instructions for experimenter, which pinprick to pick up etc
# participant screen, add which hand is being tested and remove the "painful stimulus" instruction for the beginning of calib
# record temperature throughout the trial (so we can see what was actually coming out of the thermode)



    
thisOS = platform.system()

if thisOS == "Linux":
    slash = "/"
else:   
    slash = "\\"


#import ButtonBoxFunctions as bb


# *********************************************************
#              Which devices to switch on?
# *********************************************************    

# used computer has a parallel port (for the button boxes)
parallel_port_mode = False

# eyetracking
eyetrack_mode = False

#brain amp mode
brainAmp = False

#thermode
thermode = True
#whichComputer = "Home" #python3
whichComputer = "LaserLab" #python2

if whichComputer == "LaserLab":
    sys.path.insert(1, '/NOBACKUP2/Controlling_QST/')
    sys.path.insert(1, '/NOBACKUP2/Pred_spec/Ulrike_functions/')
    directory="//NOBACKUP2//Pred_spec//"
    if thermode:
        import QST_functions
    import ButtonBoxFunctions as bb
    
else:
    directory="D:\\GitHub\\Pain_pred_spec\\"

if brainAmp:
    # # Port for BrainAmp Trigger
    p_out = parallel.Parallel(1)
    p_out.setDataDir(1)
    
    
    # # sending signal to brain amp
    def signalBrainAmp():
        p_out.setData(0)
        timer.reset()
        while timer.getTime() <= 0.05:
            p_out.setData(int("00000001", 2))  # sets pin 2 high
        p_out.setData(0)
        
if parallel_port_mode:
    # initialize button boxes on port 0
    timerRating=core.Clock()
    p_in = parallel.Parallel(0)
    p_in.setDataDir(0)
    bbox = bb.ButtonBox(port = p_in, clock = timerRating)
else:
    bbox = [] #some functions ask for this so need to define even if blank           
    
# *******************************************************
#                   Timing
# *******************************************************        

#timer for brainAmp
timer = core.Clock()

# how long should the TTL pulse be?
thermode_trigger_dur = 0.01
# How long is the stimulation programmed?
#stim_time = 1.5

## SETUP thermode
# settings
baselineTemp = 31.0 # baseline/neutral temperature (for all 5 zones equally)
durations = [1]*5 # stimulation durations in s for the 5 zones
ramp_speed = [100]*5 # ramp up speed in C/s for the 5 zones
return_speed = [100]*5 # ramp down speed in C/s for the 5 zones
mytemperatures = [47]*5 # target temperatures in C for the 5 zones


## stimulus durations and parameters
stim_dur_calibration = 1.0 #in seconds
stim_dur_main_expt = 1 #in seconds
delay_before_resp_calib = 3.0 #in seconds, so rating scale appears X s after thermode onset
delay_after_stim_calibration = 8.0
delay_after_stim_main_experiment = 3.0 #how long to wait after stim onset, so if stim is 1s long,
#then this give 2s afterwards before rating scale
delay_before_stim_main_experiment = 8.0 #gives time for experimenter to start the stimulus (for pinpricks it's manually driven)
#5 s countdown plus around 3 s extra (the exact time will be jittered) because 8s min ISI is good. With the jitter will be between 6 and 10
stimonsetTimer = core.CountdownTimer(delay_before_stim_main_experiment)  # runs backwards
#stimonsetTimer.add(delay_before_stim_main_experiment)
# how to use
# while stimonsetTimer.getTime() > 0:



## Setup Section
#win = visual.Window([1000,700], fullscr=False, monitor="testMonitor", units='pix')


# insert at 1, 0 is the script path (or '' in REPL)
#sys.path.insert(1, 'D:\Yulia\Psychopy Learning')
import myFunctions # import my own functions


# *************************************************************
#     Obtain user data
# *************************************************************

myDlg = gui.Dlg(title="Psychophysics")
myDlg.addText('Subject info')
myDlg.addField('ID:', 00)
myDlg.addField('Alter:', 21)
myDlg.addField('Geschlecht:', choices=["M", "W", "D"])
#myDlg.addText('Experiment Info')
#myDlg.addField('Grating Ori:',45)
myDlg.addField('Session:', choices=["Pain Location", "Pain Type"])
myDlg.addField('Pain calibration?', choices=['Nein', 'Ja'])
myDlg.addField('Practice Session?', choices=['Nein', 'Ja'])
myDlg.addField('Cue order', choices=["1", "2", "3", "4", "5", "6"])
myDlg.addField('Block', choices=["1", "2", "3", "4"])
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # or if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')    

sub = ok_data[0]
age = ok_data[1]
sex = ok_data[2]
sessiontype = ok_data[3]
paincalibrationYN = ok_data[4]
practicesessionYN = ok_data[5]
cueorder = ok_data[6]
thisblock = ok_data[7]


# Can manually enter some temperatures from a previous calibration file if needed
# these are overwritten if calibration == Ja by the calibrated values later on in the script

#temperatures_debug = [46.8, 47.4, 48.1, 48.8, 49] # calibrate to the person's own thresholds?
#temperatures_debug = [42, 43, 44, 45, 46] # calibrate to the person's own thresholds?
#temperatures_debug = [15, 25, 40, 45, 50] # calibrate to the person's own thresholds?
#temperatures_debug = [40, 42, 44, 46, 48, 50, 52, 54, 56] # calibrate to the person's own thresholds?
#temperatures_debug = [48.5, 49.4, 50.3, 51.3, 52.2] # calibrate to the person's own thresholds?
#temperatures_debug = [49.7, 50.6, 51.5, 52.4, 53.3] # calibrate to the person's own thresholds?
#temperatures_debug = [49.2, 50.2, 51.3, 52.3, 53.3] # calibrate to the person's own thresholds?
#temperatures_debug = [51.3, 52.5, 53.6, 54.8, 55.9] # calibrate to the person's own thresholds?
#temperatures_debug = [47.8, 48.5, 49.2, 49.9, 50.6] # calibrate to the person's own thresholds?
#temperatures_debug = [49.8, 50.5, 51.2, 51.9, 52.6] # calibrate to the person's own thresholds?
#temperatures_debug = [48.4, 49.1, 49.8, 50.5, 51.2] # calibrate to the person's own thresholds?
#temperatures_debug = [48.7, 49.7, 50.7, 51.6, 52.6] # calibrate to the person's own thresholds?
#temperatures_debug = [50.7, 51.9, 53.2, 54.4, 55.6] # Pilot Sub 01
#temperatures_debug = [49.6, 50.6, 51.6, 52.5, 53.5] # Pilot Sub 02
#temperatures_debug = [50.1, 51.1, 52.1, 53.0, 54.0] # Pilot Sub 03
#temperatures_debug = [45.5, 47.7, 49.9, 52.1, 54.3] # Pilot Sub 04
#temperatures_debug = [50.3, 51.1, 52.0, 52.9, 53.8] # Pilot Sub 05
#temperatures_debug = [50.9, 52.0, 53.0, 54.1, 55.1] # Pilot Sub 06
temperatures_debug = [48.5, 49.7, 50.9, 52.1, 53.3] # Pilot Sub 07

# routine to quit the experiment e.g. at the end or when escape is pressed
def QuitExperiment():

    #save the temperature log file here, rather than on every trial to save lag
    # save as matlab file as that's the easiest for now
    mdic = {"left_thermode": temperatures_in_trial_left, "right_thermode": temperatures_in_trial_right, "label": "temps"}
    savemat(filenamelogtemp + ".mat", mdic)
    #temperatures_in_trial_left[timesample, zones, trial]
    
    ## Closing Section
    datafilewrite.close()
    if cueorderinwords: #if variable exists
        writerlog.writerow(["Cue order: ", cueorderinwords]) 
    logfilewrite.close()
    
    
    if eyetrack_mode:
        
        tk.sendMessage('END')
        tk.stopRecording()  # stop recording
        
        # Get the EDF data file
        tk.setOfflineMode()
        tk.closeDataFile()
        pylink.pumpDelay(50)
        tk.receiveDataFile(edf_running_name, filenameeyetrack)
        
        
        # close the link to the tracker
        tk.close()
        
        # close everything
        pylink.closeGraphics()
        
    win.close()
    winexp.close()    
    
    if parallel_port_mode:
        p_in.PPRELEASE()
    
    if brainAmp:
        p_out.PPRELEASE()

    core.quit()

       

## Calibration file
#filenamecalibration="{}/Ulrike functions/randomization_trials_session_2_calibration_short.csv".format(directory)

## Calibration ratings data filename
#filenamecalibrationdata = "{}/calibration_{}_{}_{}_{}_{}.csv".format(directory, sub, sex, age, sessiontype, time.strftime('%Y-%m-%dT%H.%M.%S'))
#if thisOS == "Linux":
#    datafilewritecalib = open(filenamecalibrationdata, "w")
#else:
#    datafilewritecalib = open(filenamecalibrationdata, "w", newline='') # windows
#writercalib = csv.writer(datafilewritecalib, delimiter=";")
#writercalib.writerow(["Temp", "Rating"]) # data calibration file column headers


# **************************************************
#    File names
# **************************************************

## Data file
filenamedata="{}data_{}_{}_{}_{}_blk{}_cueorder{}_{}.csv".format(directory, sub, sex, age, sessiontype, thisblock, cueorder, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
if thisOS == "Linux":
    datafilewrite = open(filenamedata, "w")
else:
    datafilewrite = open(filenamedata, "w", newline='') # windows
writer = csv.writer(datafilewrite, delimiter=";")
writer.writerow(["Trial number", "Trial Name", "Trial Type ID", "Control Intensity", "Comparison Intensity", "Position of Control", "Sub Resp Raw", "Sub Resp Comparison More Pain", "RT (s)", "Delay before stim (s)"]) # data file column headers


## Log file (prints out key events, for timing etc)
filenamelog="{}log_{}_{}_{}_{}_{}_{}.csv".format(directory, sub, sex, age, sessiontype, thisblock, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
if thisOS == "Linux":
    logfilewrite = open(filenamelog, "w")
else:
    logfilewrite = open(filenamelog, "w", newline='') # windows
writerlog = csv.writer(logfilewrite, delimiter=";")
#writerlog.writerow(["Trial number", "Trial Name", "Trial Type ID", "Control Intensity", "Comparison Intensity", "Position of Control", "Sub Resp Raw", "Sub Resp Comparison More Pain", "RT"]) # data file column headers


## Log file temperature. Mat file. Not csv
filenamelogtemp="{}log_temp_{}_{}_{}_{}_{}_{}".format(directory, sub, sex, age, sessiontype, thisblock, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
#if thisOS == "Linux":
#    logtempfilewrite = open(filenamelogtemp, "w")
#else:
#    logtempfilewrite = open(filenamelogtemp, "w", newline='') # windows
#writerlogtemp = csv.writer(logtempfilewrite, delimiter=";")

# **************************************************
#       Screens
# **************************************************

# set screen properties
scnWidth, scnHeight = (1920, 1080)
#scnWidth, scnHeight = (1080, 720)

# define monitor
mon = monitors.Monitor('laserlab', width=53.0, distance=57.0)
mon.setSizePix((scnWidth, scnHeight))


# window for experimenter
winexp = visual.Window(
    (1500, 800), fullscr=False, screen=0,
    allowGUI=False, allowStencil=False,
    color=[0.404,0.404,0.404], colorSpace='rgb', waitBlanking = False)
refreshratewinexp = winexp.getActualFrameRate(nIdentical=10, nMaxFrames=100, nWarmUpFrames=10, threshold=1)
print(refreshratewinexp)

# window for subject
win = visual.Window(
    (scnWidth, scnHeight), fullscr=False, screen=1,
    allowGUI=False, allowStencil=False,
    monitor=mon, color=[0.404,0.404,0.404], colorSpace='rgb', waitBlanking = False)
refreshratewin = win.getActualFrameRate(nIdentical=10, nMaxFrames=100, nWarmUpFrames=10, threshold=1)
print(refreshratewin)


# ***************************************************************
#        Set up eyetracking
# ***************************************************************

if eyetrack_mode:
     # initialize eyetracking and run for the whole experiment
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
    
    #-------------------------------------------
    dummyMode = False  
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
#
#    # ==============================================================
#    # preparation
#    # ==============================================================
#    # Ensure that relative paths start from the same directory as this script
#    thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
#    os.chdir(thisDir)
#    
#    # Make data folder
#    if not os.path.isdir("data"):
#        os.makedirs("data")
#    
#    # filename with time stamp
#    timestamp = data.getDateStr(format='%Y%m%d_%H%M')
#    filename = thisDir + os.sep + 'data' + os.sep + 'eyetracking_demo_%s' % (timestamp) + '.edf'
#    
#    # in the DOS system you can only store up to 8 characters for the file name 
#    edf_running_name = 'demo.EDF'
#    
#    # open data file
#    tk.openDataFile(edf_running_name)
#    # add personalized data file header (preamble text)
#    tk.sendCommand("add_file_preamble_text 'Eyetracking Demo'")
#
#    tk.setOfflineMode()  # we need to put the tracker in offline mode before we change its configurations
#    tk.sendCommand('sample_rate 1000')  # 250, 500, 1000
#    # inform the tracker the resolution of the subject display
#    tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (scnWidth - 1, scnHeight - 1))
#    # save display resolution in EDF data file for Data Viewer integration purposes
#    tk.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (scnWidth - 1, scnHeight - 1))
#    # specify the calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical), 
#    tk.sendCommand("calibration_type = HV9")  # HV9
#    # specify the proportion of subject display to calibrate/validate (OPTIONAL, useful for wide screen monitors)
#    tk.sendCommand("calibration_area_proportion 0.55 0.53") # 0.65 0.63
#    # tk.sendCommand("validation_area_proportion  0.85 0.83")
#    # the model of the tracker, 1-EyeLink I, 2-EyeLink II, 3-Newer models (1000/1000Plus/DUO)
#    eyelinkVer = tk.getTrackerVersion()
#    # Set the tracker to parse Events using "GAZE" (or "HREF") data
#    tk.sendCommand("recording_parse_type = GAZE")
#    # Online parser configuration: 0-> standard/cognitive, 1-> sensitive/psychophysiological
#    # [see Eyelink User Manual, Section 4.3: EyeLink Parser Configuration]
#    
#    
#    if not dummyMode:
#        # set up the camera and calibrate the tracker at the beginning of each block
#        tk.doTrackerSetup()
#
#    # take the tracker offline
#    tk.setOfflineMode()
#    pylink.pumpDelay(50)
        
        
        
        
# ************************************************************
##      Eyetracking calibration
# ************************************************************
if eyetrack_mode:
    
    try: #python 2, unicode string
        thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
    except: #python 3, string already unicode so no decode function can be used (or needed)
        thisDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(thisDir)
    
    # Make data folder
    if not os.path.isdir("data"):
        os.makedirs("data")
    timestamp = data.getDateStr(format='%Y%m%d_%H%M')    
    filenameeyetrack = thisDir + os.sep + 'data' + os.sep + 'eyetracking_%s' % (timestamp) + str(sub) + str(sex) + str(age) + str(sessiontype) +'.edf'

    (tk, edf_running_name) = myFunctions.Eyetracking_calibration(filenameeyetrack, tk, win, winexp, scnWidth, scnHeight, dummyMode)        
    #tk.sendMessage('Start Rec 2')     
        

###################################################################
#          CALIBRATION
###################################################################    

## Do Calibration
# for individual temperatures and so on
# should do this for both arms    
    
if paincalibrationYN == 'Ja':
    
    # ==============================================================
    # Quit routine in case run is aborted
    # ==============================================================
    def quitRoutine():
        print('Calibration aborted, calculating temperatures up to this point')
        
        # this is not properly implemented yet
#        if rating: #if non empty
#            (temperatures_calibrated, temp_30, temp_50, temp_75) = QST_functions.SaveCalibrationTemp(temperatures_calibration, rating, writercalib, filenamecalibrationdata)
#            datafilewritecalib.close()
            
        win.close()
        winexp.close()
        core.quit()
    
    whichSide = [0, 1] #0 = left, 1 = right
    random.shuffle(whichSide) #counterbalance order
    #calibration_not_passed = True
    
    
    for side in whichSide: #do it twice, for each arm/leg
        calibration_not_passed = True
        
        
        if side == 0:
            sideString = "left"
            sideStringDE = "LINKS"
        else:
            sideString = "right"
            sideStringDE = "RECHTS"
        
        # ==============================================================
        # TESTSTIMULI
        # ==============================================================
        
        # generate text and rating scale objects     
        textObjExp = visual.TextStim(win=winexp, text="", color="black", height = 20, units="pix")
        textObjSub = visual.TextStim(win=win, text="", color="black", height = 40, units="pix")
        dotObj = visual.Circle(win=win, fillColor="white", lineColor="white",radius=[12,12],units="pix")
        ratingPain = visual.RatingScale(win = win, low = 0, high = 100, markerStart = 50, textSize=0.75,
        marker = 'triangle', stretch = 1.5, tickHeight = 1.5, tickMarks = [0,50,100],textColor='black',lineColor='black',
        labels = [u'keine Empfindung', u'Schmerzschwelle', u'nicht aushaltbarer Schmerz'],
        showAccept = False)
        ratingPainExp = visual.RatingScale(win = winexp, low = 0, high = 100, markerStart = 50, textSize=0.75,
        marker = 'triangle', stretch = 1.5, tickHeight = 1.5, tickMarks = [0,50,100],textColor='black',lineColor='black',
        labels = [u'keine Empfindung', u'Schmerzschwelle', u'nicht aushaltbarer Schmerz'],
        showAccept = False)
        
        keyState=key.KeyStateHandler() # to check the key status when using the keyboard mode
        win.winHandle.push_handlers(keyState)
        
        timerTrigger = core.Clock() # for duration of messages and triggers to brain amp and thermode
        timerRating=core.Clock() #for rating reaction time
        
#        if parallel_port_mode:
#            # initialize button boxes on port 0
#            bbox = bb.ButtonBox(port = 0, clock = timerRating)
#            # the port for communication with brainamp and thermode
#            p_port1 = parallel.Parallel(port=1)
#        else:
#            pass
#            #keyState = key.KeyStateHandler()  # to check the key status when using the keyboard
#            #win.winHandle.push_handlers(keyState)
        
                  
            
        # Create some timers to manage the timing of routines within one trial
        routineClock = core.Clock() # runs forwards
        routineTimer = core.CountdownTimer()  # runs backwards 
        
        
        # Experimenter starts by pressing space
        textObjExp.setText(u"Press space to send some first test stimuli\n" + " on the " + sideString + " side")
        textObjExp.setHeight(20)
        textObjExp.draw()
        winexp.flip()
        event.waitKeys(keyList=["space"])
        textObjExp.setText(u"Applying test stimuli" + "on the " + sideString + " side")
        textObjExp.draw()
        winexp.flip()
        textObjSub.setText(u'Zu Beginn werden wir einige kurze Hitzereize verabreichen, um die Hautstelle daran zu gewöhnen.\n'+\
                        u'Der erste Reiz kommt aus dem warmen Bereich.\n' + sideStringDE)
        textObjSub.draw()
        win.flip()
        core.wait(5.0)
        
        
        
        ## new USB stuff for QST thermode
        if thermode:
            if side == 0: #left
                QST_functions.Burn_left([45, 45, 45, 45, 45], [1]*5, [100]*5, [100]*5)
            else:  #right
                QST_functions.Burn_right([45, 45, 45, 45, 45], [1]*5, [100]*5, [100]*5)
        core.wait(5.0)
        
        textObjSub.setText(u'Der zweite Reiz ist genau der gleiche Reiz wie der erste.')
        textObjSub.draw()
        win.flip()
        core.wait(5.0)
        if thermode:
            if side == 0: #left
                QST_functions.Burn_left([45, 45, 45, 45, 45], [1]*5, [100]*5, [100]*5)
            else:  #right
                QST_functions.Burn_right([45, 45, 45, 45, 45], [1]*5, [100]*5, [100]*5)
        core.wait(5.0)
        
        #core.wait(3.0)
        timerRating.reset()
        # send signal to thermode
#        if parallel_port_mode:
#            while timerRating.getTime() <= thermode_trigger_dur:
#                p_port1.setData(int("00010000", 2))  # sets pin 6 high
#            p_port1.setData(0)  # set all pins low
       # core.wait(4.0)
        
        
        textObjSub.setText(u'Der nächste Reiz ist aus dem schmerzhaften Bereich.')
        textObjSub.draw()
        win.flip()
        core.wait(5.0)
        timerRating.reset()
        # send signal to thermode
#        if parallel_port_mode:
#            while timerRating.getTime() <= thermode_trigger_dur:
#                p_port1.setData(int("00010000", 2))  # sets pin 6 high
#            p_port1.setData(0)  # set all pins low
        if thermode:       
            if side == 0: #left
                   QST_functions.Burn_left([48, 48, 48, 48, 48], [1]*5, [100]*5, [100]*5)
            else:  #right
                   QST_functions.Burn_right([48, 48, 48, 48, 48], [1]*5, [100]*5, [100]*5)
        
        core.wait(5.0)
        
        #textObjSub.setText(u'Der nächste Reiz ist aus dem schmerzhaften Bereich.')
        #textObjExp.setText(u'Der nächste Reiz ist aus dem schmerzhaften Bereich.')
        #textObjSub.draw()
        #textObjExp.draw()
        #win.flip()
        #winexp.flip()
        #core.wait(3.0)
        
        #core.wait(1.0)
        #win.flip()
                   
        #########################    
        # PROPER CALIBRATION
        #########################
        
        while calibration_not_passed:
            redo = False
            if side == 0:
                sideString = "left"
            else:
                sideString = "right"
                
                
            #save 2 separate calibration files for L and R
            filenamecalibrationdata = "{}/calibration_{}_{}_{}_{}_{}_".format(directory, sub, sex, age, sessiontype, time.strftime('%Y-%m-%dT%H.%M.%S'))
            filenamecalibrationdata = filenamecalibrationdata + sideString + ".csv" #need separate files for L and R
            
            if thisOS == "Linux":
                datafilewritecalib = open(filenamecalibrationdata, "w")
            else:
                    datafilewritecalib = open(filenamecalibrationdata, "w", newline='') # windows
            writercalib = csv.writer(datafilewritecalib, delimiter=";")
            writercalib.writerow(["Temp", "Rating"]) # data calibration file column headers
            
            print('Calibration started...' + " " + sideString)
            
            
            rating = []
            
               
            
        
       
            
            # ==============================================================
            # START
            # ==============================================================
            # Experimenter starts by pressing space
            textObjExp.setText(u"Press space to start calibration for {} side \n Press R at any point during the rating scale to restart the calibration for the current side".format(sideString))
            textObjExp.setHeight(20)
            textObjExp.draw()
            textObjSub.setText(u'Die Kalibrierung beginnt demnächst.')
            textObjSub.draw()
            win.flip()
            winexp.flip()
            event.waitKeys(keyList=["space"])
            textObjExp.setText("")
            textObjExp.draw()
            win.flip()
            winexp.flip()
            
            rating = []
            
            # for debugging
            temperatures_calibration_debugging = [
                46.0, 47.0,
                44.0, 48.0,
                49.5, 47.0] 
    
            
#            temperatures_calibration_real = [
#                46.0, 47.0,
#                44.0, 48.0,
#                49.5, 47.0,  
#                44.5, 48.5,
#                43.5, 49.0,
#                47.0, 48.0,
#                44.0, 45.0,
#                47.5, 44.0,
#                49.0, 46.5,
#                43.0, 44.5,
#                42.0, 45.5,
#                47.5, 42.5,
#                46.0, 43.0,
#                45.0, 48.5,
#                45.5, 42.5,
#                46.5, 45.0,
#                46.0, 43.5,
#                49.5, 42.0,
#                50.0, 50.0,
#                50.5, 50.5,
#                51.0, 51.0]
            
#            temperatures_calibration_real = [ # not including half degree increments
#                42.0, 42.0, 43.0,
#                43.0, 44.0, 44.0,
#                44.0, 45.0, 45.0,
#                45.0, 46.0, 46.0,
#                46.0, 47.0, 47.0,
#                47.0, 48.0, 48.0,  
#                49.0, 49.0, 50.0,
#                50.0, 51.0, 51.0]
#            
            #try more trials in painful range
            temperatures_calibration_real = [ # not including half degree increments
                42.0, 42.5, 43.0,
                43.5, 44.0, 44.5,
                45.0, 45.5, 46.0,
                46.5, 47.0, 47.5,
                48.0, 48.5, 49.0, 49.0, 49.5,
                49.5, 50.0, 50.0, 50.5, 50.5,
                51.0, 51.0, 51.5,
                51.5, 52.0, 52.0]
            
            random.shuffle(temperatures_calibration_real)
            
            temperatures_calibration = temperatures_calibration_real
            #temperatures_calibration = temperatures_calibration_debugging  
            random.shuffle(temperatures_calibration)
                
            for i, eachcalibrationtemp in enumerate(temperatures_calibration):
                tk.sendMessage(str('Calib Trial %d' % (i+1)))  
                print(redo)
                print (i)
                # (stimulate only 2 pads at a time, so 1+2 then 4+5 then 1+2 and so on, to prevent sensitization etc)
                # changed now to 4 pads at a time after some feedback
                if i % 2 == 0: # even number trial
                    requiredtemperatures = [eachcalibrationtemp, eachcalibrationtemp, 31, eachcalibrationtemp, eachcalibrationtemp]
                else: # odd number trial
                    requiredtemperatures = [eachcalibrationtemp, eachcalibrationtemp, 31, eachcalibrationtemp, eachcalibrationtemp]
                        
                
                core.wait(delay_after_stim_calibration + random.uniform(-2, 2)) #wait the delay (probably around 8s, defined above, plus a random jitter,
                # so that the total delay is 6-10 s)
                
                # 1.5 s duration, 100 deg ramp up/down
                if thermode:
                    if side == 0: #left
                        QST_functions.Burn_left(requiredtemperatures, [stim_dur_calibration]*5, [100]*5, [100]*5)
                    else:  #right
                        QST_functions.Burn_right(requiredtemperatures, [stim_dur_calibration]*5, [100]*5, [100]*5)
                core.wait(delay_before_resp_calib) #wait before rating scale appears
                #check for quit (the Esc key)
                if event.getKeys(keyList=["escape"]):
                    quitRoutine()
                
                submittedanswer = False
                ratingPain.reset()
                ratingPainExp.reset()
                currentPos = 50
                textObjSub.setText(u"Bitte bewerten Sie\ndie Intensität\ndieses Reizes\n")
                
                while not submittedanswer:
                    ratingPain.markerPlacedAt = currentPos
                    ratingPain.draw()
                    textObjSub.draw()
                    
                    ratingPainExp.markerPlacedAt = currentPos
                    ratingPainExp.draw()
                    
                    win.flip()
                    winexp.flip()
                    
                    if parallel_port_mode:
                        bbox.reset()
                        keypress = bbox.getButtons(timeStamped=False)
                        keypresskeyboard = event.getKeys(keyList=['left', 'right', 'escape', 'return', 'r']) #wait for Left Arrow or Right Arrow key
                        if keypresskeyboard:
                                if keypresskeyboard[0] == "escape":
                                    QuitExperiment()
                                elif keypresskeyboard[0] == "r":
                                    redo = True
                                    print("Redo = True")
                        #print(keypresskeyboard)
                    else:
                        keypress = event.waitKeys(keyList=['left', 'right', 'escape', 'return', 'r']) #wait for Left Arrow or Right Arrow key
                    
                    
                    if keypress:
                        if parallel_port_mode == True:
                            #print(keypress)
                            # move left
                            if keypress[0] == 0:
                                currentPos = currentPos - 1
                            # move right
                            elif keypress[0] == 1:
                                currentPos = currentPos + 1
                            elif keypress[0] == 2:
                                submittedanswer = True
                            elif keypress[0] == 3:    
                                pass
                            else:
                                print('Do you use the correct button box / keys?')
                            
                        else:
                            #print(keypress)
                            # move left
                            if keypress[0] == 'left':
                                currentPos = currentPos - 1
                            # move right
                            elif keypress[0]  == 'right':
                                currentPos = currentPos + 1
                            elif keypress[0] == 'escape':
                                quitRoutine()
                            elif keypress[0] == 'return':
                                submittedanswer = True
                            elif keypress[0] == 'r':
                                redo = True
                                print("Redo = True")
                                #print(redo)
                            else:
                                print('Do you use the correct button box / keys?')
                        
                    if currentPos > 100:
                        currentPos = 100
                    elif currentPos < 0:
                        currentPos = 0
                    ratingPain.markerPlacedAt = currentPos
                    ratingPain.draw()
                    textObjSub.draw()
                    ratingPainExp.markerPlacedAt = currentPos
                    ratingPainExp.draw()
                    win.flip()
                    winexp.flip()
                    #core.wait(0.01)        
                        
                # record answer
                rating.append(ratingPain.getRating())
                print([i, '   ', eachcalibrationtemp, '   ', rating[i]])
                
                winexp.flip()
                win.flip()
                if redo: #if need to restart the current side
                    rating = []
                    break
            #end of for eachtemp loop
     
            # Work out the key temperatures and write to file
            
            if not redo:
                (temperatures_calibrated, temp_30, temp_50, temp_75, temp_80) = QST_functions.SaveCalibrationTemp(temperatures_calibration, rating, writercalib, filenamecalibrationdata)
                datafilewritecalib.close()
            
                if side == 0:
                    temp30_left = temp_30
                    temp50_left = temp_50
                    temp75_left = temp_75
                    temp80_left = temp_80
                    
                else:
                    temp30_right = temp_30
                    temp50_right = temp_50
                    temp75_right = temp_75
                    temp80_right = temp_80
            
            
                # for resulting plot
                img = visual.ImageStim(
                win=winexp,
                image=filenamecalibrationdata+".png",
                units="norm",
                pos = (0,0))
            
                img.draw()
                textObjExp.pos = (0, -300)
                textObjExp.setText('%.1f    %.1f     %.1f     %.1f \nPress Y to accept, N to reject and try again' % (temp_30, temp_50, temp_75, temp_80))
                textObjExp.draw()
                winexp.flip()
                expkey = event.waitKeys(keyList=["y", "n"])
                if expkey[0] == "y":
                    print("calibrationpassed")
                    calibration_not_passed = False
                    textObjSub.setText("Sehr gut! \nDie Kalibrierung ist beendet.")
                else:
                    textObjSub.setText("Es ist leider ein Fehler aufgetreten, versuchen wir es noch einmal.")
                    
                
                
                textObjSub.setText("Sehr gut! \nDie Kalibrierung ist beendet.")
                textObjSub.draw()
                win.flip()
            
            
            
        textObjExp.setText('Press space')
        textObjExp.draw()
        winexp.flip()    
        event.waitKeys(keyList=["space"])
            
            
    
    #print("About to show fix during if statememnts...")
    
    #show fix
    myFunctions.showFix(win, "+", (1, 1, 1))
    win.flip()
    core.wait(0.5)
    

# *******************************************************
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    STIMULI
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# *******************************************************    

# 5 stimulus intensity levels
#temperatures_debug = [46.8, 47.4, 48.1, 48.8, 49] # calibrate to the person's own thresholds?
#temperatures_debug = [42, 43, 44, 45, 46] # calibrate to the person's own thresholds?
#temperatures_debug = [15, 25, 40, 45, 50] # calibrate to the person's own thresholds?
#temperatures_debug = [40, 42, 44, 46, 48, 50, 52, 54, 56] # calibrate to the person's own thresholds?
#temperatures_debug = [48.5, 49.4, 50.3, 51.3, 52.2] # calibrate to the person's own thresholds?
mytemperatures = temperatures_debug
if paincalibrationYN == 'Ja':
    #take the average calibration of L and R
    temperatures_calibrated = numpy.linspace((temp50_left+temp50_right)/2, (temp75_left+temp75_right)/2, 5) # we want 5 numbers for the psychometric function
    print(temperatures_calibrated)
    mytemperatures = numpy.round(temperatures_calibrated, 1) # from calibration, to 1 dec place
mechanicalinstensities = [32, 64, 128, 256, 512] #check what these should be, also calibrated individually?

temperature_intensity_control = mytemperatures[2] # third stimulus in our calibration
#temperature_intensity_control = 48 # for debug
mechintensity_control = 128



################################
## Generate stimuli
################################
# Qualitative session [Pain type]
#   Conditions
#   1. 66% Thermo
#   2. 66% Mechano
#   3. 50-50%
#
# Spatial session [Pain location]
#   Conditions
#   1. 66% Finger 2 + 4
#   2. 66% Finger 3 + 5
#   3. 50-50%
#
# General design
#   Thermal High
#       Thermal = 12 trials/per point of psychometric function
#       Mechanical = 6 trials/per point of psychometric function
#   Mechanical High
#       Thermal = 6 trials/pt
#       Mechano = 12 trials/pt
#   No expectaion
#       T 9 trials
#       M 9 trials
#


expectation_rate = 3 # 2wice or 3rice as often as the other stim; 66.6666% or 75%
trialsperpointhigh = 18
trialsperpointlow = numpy.int(trialsperpointhigh/expectation_rate)
nBlocks = 4.0
#noexpectation = numpy.int(numpy.floor((trialsperpointhigh+trialsperpointlow)/2)) #remove NONE trials for now

thermalhigh_thermal = trialsperpointhigh
thermalhigh_mechano = trialsperpointlow

stimuli_list = []
# need to counterbalance which position on the hand is control and which comparison
# stimuli_list = [Trial Num (of this type), Trial Type String, Trial Type Numerical, Intensity Comparison, position_of_control]



# Create list of stims
# There will be some differences for the 4 blocks because of the specific number of trials and
# combinations of everything. Basically, can't divide all the trials into any number such that there is an
# even number of every combination of everything across the blocks
# N trials to create is N trials per pt divided by 4 blocks divided by 2 (half control first, half control second)
# Important: do 3.0 / 2.0 rather than 3 / 2 in python 2 to get a float result!!!
if sessiontype == "Pain Type":
    for temperature_intensity in mytemperatures: #for each stimulus temperature
        for i in range(numpy.int(trialsperpointhigh/nBlocks/2.0)): #thermal high thermal presented, control position 1
            stimuli_list.append([i+1, "ThermalHigh_thermal", 1, temperature_intensity, 0])
        for i in range(numpy.int(trialsperpointhigh/nBlocks/2.0)): #thermal high thermal presented, control position 2
            stimuli_list.append([i+1, "ThermalHigh_thermal", 1, temperature_intensity, 1])
            
        for i in range(numpy.int(trialsperpointlow/nBlocks/2.0)): # mechano high thermal presented, control position 1
            stimuli_list.append([i+1, "MechanoHigh_thermal", 4, temperature_intensity, 0])       
        for i in range(numpy.int(trialsperpointlow/nBlocks/2.0)): # mechano high thermal presented, control position 2
            stimuli_list.append([i+1, "MechanoHigh_thermal", 4, temperature_intensity, 1])  
            
#        #something a bit different needs to happen for the no expectation because of the odd N of trials
#        # note the ceil and floor, instead of just int
#        if thisblock == "1":
#            for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect thermal presented, control position 1
#                stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 0])  
#            for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect thermal presented, control position 2
#                stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 1])
#        elif thisblock == "2":
#            for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect thermal presented, control position 1
#                stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 0])  
#            for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect thermal presented, control position 2
#                stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 1])
#        elif thisblock == "3":
#            for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect thermal presented, control position 1
#                stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 0])  
#            for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect thermal presented, control position 2
#                stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 1])
                
    for mechintensity in mechanicalinstensities:
        for i in range(numpy.int(trialsperpointlow/nBlocks/2.0)): # thermal high mechano presented, control position 1
            stimuli_list.append([i+1, "ThermalHigh_mechano", 2, mechintensity, 0])    
        for i in range(numpy.int(trialsperpointlow/nBlocks/2.0)): # thermal high mechano presented, control position 2
            stimuli_list.append([i+1, "ThermalHigh_mechano", 2, mechintensity, 1]) 
            
        for i in range(numpy.int(trialsperpointhigh/nBlocks/2.0)): # mechano high mechano presented, control position 1
            stimuli_list.append([i+1, "MechanoHigh_mechano", 3, mechintensity, 0]) 
        for i in range(numpy.int(trialsperpointhigh/nBlocks/2.0)): # mechano high mechano presented, control position 2
            stimuli_list.append([i+1, "MechanoHigh_mechano", 3, mechintensity, 1]) 
        
#        #something a bit different needs to happen for the no expectation because of the odd N of trials
#        # note the ceil and floor, instead of just int
#        if thisblock == "1":
#            for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect mechano presented, control position 1
#                stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 0])   
#            for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect mechano presented, control position 2
#                stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 1])   
#        elif thisblock == "2":
#            for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect mechano presented, control position 1
#                stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 0])   
#            for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect mechano presented, control position 2
#                stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 1]) 
#        elif thisblock == "3":     
#            for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect mechano presented, control position 1
#                stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 0])   
#            for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect mechano presented, control position 2
#                stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 1])                         
            
elif sessiontype == "Pain Location": #same location but only thermal for now
    
        for temperature_intensity in mytemperatures: #for each stimulus temperature
            if thisblock == "1" : #round up or down as necessary
                #HIGH LEFT
                ntrialsiteratorHIGHLEFTCtrl1 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHLEFTCtrl2 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                
                #LOW LEFT
                ntrialsiteratorLOWLEFTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWLEFTCtrl2 = range(numpy.int(numpy.floor(trialsperpointlow/nBlocks/2.0)))
                
                #HIGH RIGHT
                ntrialsiteratorHIGHRIGHTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHRIGHTCtrl2 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                
                #LOW RIGHT
                ntrialsiteratorLOWRIGHTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWRIGHTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                
            elif thisblock == "2" :     
                #HIGH LEFT
                ntrialsiteratorHIGHLEFTCtrl1 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHLEFTCtrl2 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
               
                #LOW LEFT
                ntrialsiteratorLOWLEFTCtrl1 = range(numpy.int(numpy.floor(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWLEFTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
               
                #HIGH RIGHT
                ntrialsiteratorHIGHRIGHTCtrl1 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHRIGHTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointhigh/nBlocks/2.0)))
               
                #LOW RIGHT
                ntrialsiteratorLOWRIGHTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWRIGHTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
               
            elif thisblock == "3" :       
                #HIGH LEFT
                ntrialsiteratorHIGHLEFTCtrl1 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHLEFTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointhigh/nBlocks/2.0)))
               
                #LOW LEFT
                ntrialsiteratorLOWLEFTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWLEFTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
               
                #HIGH RIGHT
                ntrialsiteratorHIGHRIGHTCtrl1 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHRIGHTCtrl2 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
               
                #LOW RIGHT
                ntrialsiteratorLOWRIGHTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWRIGHTCtrl2 = range(numpy.int(numpy.floor(trialsperpointlow/nBlocks/2.0)))
                
                
            elif thisblock == "4" :       
                #HIGH LEFT
                ntrialsiteratorHIGHLEFTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHLEFTCtrl2 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))    
                
                #LOW LEFT
                ntrialsiteratorLOWLEFTCtrl1 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWLEFTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
                
                #HIGH RIGHT
                ntrialsiteratorHIGHRIGHTCtrl1 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                ntrialsiteratorHIGHRIGHTCtrl2 = range(numpy.int(numpy.floor(trialsperpointhigh/nBlocks/2.0)))
                
                #LOW RIGHT
                ntrialsiteratorLOWRIGHTCtrl1 = range(numpy.int(numpy.floor(trialsperpointlow/nBlocks/2.0)))
                ntrialsiteratorLOWRIGHTCtrl2 = range(numpy.int(numpy.ceil(trialsperpointlow/nBlocks/2.0)))
               
                
                               
            for i in ntrialsiteratorHIGHLEFTCtrl1: #thermal high thermal presented, control position 1
                    stimuli_list.append([i+1, "LeftHigh_Left", 1, temperature_intensity, 0])
            for i in ntrialsiteratorHIGHLEFTCtrl2: #thermal high thermal presented, control position 2
                stimuli_list.append([i+1, "LeftHigh_Left", 1, temperature_intensity, 1])
                
            for i in ntrialsiteratorLOWLEFTCtrl1: # mechano high thermal presented, control position 1
                stimuli_list.append([i+1, "RightHigh_Left", 4, temperature_intensity, 0])       
            for i in ntrialsiteratorLOWLEFTCtrl2: # mechano high thermal presented, control position 2
                stimuli_list.append([i+1, "RightHigh_left", 4, temperature_intensity, 1])  
                            
#            #something a bit different needs to happen for the no expectation because of the odd N of trials
#            # note the ceil and floor, instead of just int    
#            if thisblock == "1":
#                for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect left presented, control position 1
#                    stimuli_list.append([i+1, "Noexpect_Left", 5, temperature_intensity, 0])  
#                for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect left presented, control position 2
#                    stimuli_list.append([i+1, "Noexpect_Left", 5, temperature_intensity, 1])             
#            elif thisblock == "2":
#                for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect left presented, control position 1
#                    stimuli_list.append([i+1, "Noexpect_Left", 5, temperature_intensity, 0])  
#                for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect left presented, control position 2
#                    stimuli_list.append([i+1, "Noexpect_Left", 5, temperature_intensity, 1])  
#            elif thisblock == "3":
#                for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect left presented, control position 1
#                    stimuli_list.append([i+1, "Noexpect_Left", 5, temperature_intensity, 0])  
#                for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect left presented, control position 2
#                    stimuli_list.append([i+1, "Noexpect_Left", 5, temperature_intensity, 1])  

            
            for i in ntrialsiteratorLOWRIGHTCtrl1: # thermal high mechano presented, control position 1
                stimuli_list.append([i+1, "LeftHigh_Right", 2, temperature_intensity, 0])    
            for i in ntrialsiteratorLOWRIGHTCtrl2: # thermal high mechano presented, control position 2
                stimuli_list.append([i+1, "LeftHigh_Right", 2, temperature_intensity, 1]) 
                
            for i in ntrialsiteratorHIGHRIGHTCtrl1: # mechano high mechano presented, control position 1
                stimuli_list.append([i+1, "RightHigh_Right", 3, temperature_intensity, 0]) 
            for i in ntrialsiteratorHIGHRIGHTCtrl2: # mechano high mechano presented, control position 2
                stimuli_list.append([i+1, "RightHigh_Right", 3, temperature_intensity, 1]) 
                
                
                
#            #something a bit different needs to happen for the no expectation because of the odd N of trials
#            # note the ceil and floor, instead of just int    
#            if thisblock == "1":   
#                for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect right presented, control position 1
#                    stimuli_list.append([i+1, "Noexpect_Right", 6, temperature_intensity, 0])   
#                for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect right presented, control position 2
#                    stimuli_list.append([i+1, "Noexpect_Right", 6, temperature_intensity, 1])      
#            elif thisblock == "2":
#                for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect right presented, control position 1
#                    stimuli_list.append([i+1, "Noexpect_Right", 6, temperature_intensity, 0])   
#                for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect right presented, control position 2
#                    stimuli_list.append([i+1, "Noexpect_Right", 6, temperature_intensity, 1])
#            elif thisblock == "3":
#                for i in range(numpy.int(numpy.ceil(noexpectation/3.0/2.0))): # no expect right presented, control position 1
#                    stimuli_list.append([i+1, "Noexpect_Right", 6, temperature_intensity, 0])   
#                for i in range(numpy.int(numpy.floor(noexpectation/3.0/2.0))): # no expect right presented, control position 2
#                    stimuli_list.append([i+1, "Noexpect_Right", 6, temperature_intensity, 1])
print(stimuli_list)
#print(stimuli_list[0]) # [1, 'ThermalHigh_thermal']
#print(stimuli_list[0][0]) # 1
#print(stimuli_list[1]) # [2, 'ThermalHigh_thermal']
#print(stimuli_list[1][0]) # 2
#print(stimuli_list[1][1]) # ThermalHigh_thermal


## Load Cue images

        
#CueHighThermal = visual.ImageStim(win, (directory+"image//HighThermal.png"), units="pix", size=(600, 600))
#CueHighMechano = visual.ImageStim(win, (directory+"image//HighMechano.jpg"), units="pix", size=(600, 600))
#CueNoExpect = visual.ImageStim(win, (directory+"image//NoExpect.jpg"), units="pix", size=(600, 600))
## same for experimenters screen
#CueHighThermalExp = visual.ImageStim(winexp, (directory+"image//HighThermal.png"), units="pix", size=(600, 600))
#CueHighMechanoExp = visual.ImageStim(winexp, (directory+"image//HighMechano.jpg"), units="pix", size=(600, 600))
#CueNoExpectExp = visual.ImageStim(winexp, (directory+"image//NoExpect.jpg"), units="pix", size=(600, 600))


Pic1 = visual.ImageStim(win, (directory+"image//bild4_masked_matched_bg_179.png"), units="pix", size=(600, 600))
Pic2 = visual.ImageStim(win, (directory+"image//bild3_masked_matched_bg_179.png"), units="pix", size=(600, 600))
Pic3 = visual.ImageStim(win, (directory+"image//bild2_masked_matched_bg_179.png"), units="pix", size=(600, 600))
# same for experimenters screen
Pic1exp = visual.ImageStim(winexp, (directory+"image//bild4_masked_matched_bg_179.png"), units="pix", size=(600, 600))
Pic2exp = visual.ImageStim(winexp, (directory+"image//bild3_masked_matched_bg_179.png"), units="pix", size=(600, 600))
Pic3exp = visual.ImageStim(winexp, (directory+"image//bild2_masked_matched_bg_179.png"), units="pix", size=(600, 600))



if cueorder == "1":
    Cue1 = Pic1
    Cue2 = Pic2
    Cue3 = Pic3
    Cue1exp = Pic1exp
    Cue2exp = Pic2exp
    Cue3exp = Pic3exp
    cueorderinwords = "1: Thermal: Bild4, Mech: Bild3, None: Bild2"
elif cueorder == "2":
    Cue1 = Pic1
    Cue2 = Pic3
    Cue3 = Pic2 
    Cue1exp = Pic1exp
    Cue2exp = Pic3exp
    Cue3exp = Pic2exp
    cueorderinwords = "2: Thermal: Bild4, Mech: Bild2, None: Bild3"
elif cueorder == "3":
    Cue1 = Pic2
    Cue2 = Pic1
    Cue3 = Pic3
    Cue1exp = Pic2exp
    Cue2exp = Pic1exp
    Cue3exp = Pic3exp
    cueorderinwords = "3: Thermal: Bild3, Mech: Bild4, None: Bild2"
elif cueorder == "4":
    Cue1 = Pic2
    Cue2 = Pic3
    Cue3 = Pic1
    Cue1exp = Pic2exp
    Cue2exp = Pic3exp
    Cue3exp = Pic1exp
    cueorderinwords = "4: Thermal: Bild3, Mech: Bild2, None: Bild4"
elif cueorder == "5":
    Cue1 = Pic3
    Cue2 = Pic1
    Cue3 = Pic2
    Cue1exp = Pic3exp
    Cue2exp = Pic1exp
    Cue3exp = Pic2exp
    cueorderinwords = "5: Thermal: Bild2, Mech: Bild4, None: Bild3"
elif cueorder == "6":
    Cue1 = Pic3
    Cue2 = Pic2
    Cue3 = Pic1
    Cue1exp = Pic3exp
    Cue2exp = Pic2exp
    Cue3exp = Pic1exp
    cueorderinwords = "6: Thermal: Bild2, Mech: Bild3, None: Bild4"


CueHighThermal = Cue1
CueHighMechano = Cue2
CueNoExpect = Cue3
# same for experimenters screen
CueHighThermalExp = Cue1exp
CueHighMechanoExp = Cue2exp
CueNoExpectExp = Cue3exp

print("Cue order: " + cueorderinwords + "\n")







# **********************************************************************
# **********************************************************************
#       MAIN EXPERIMENT
# **********************************************************************
# **********************************************************************    

stimuli_list_shuffled = stimuli_list
random.shuffle(stimuli_list_shuffled)
RT = []
whichZones = [1, 4]

myPainType = []
myPainLocation = []

myFunctions.showText(winexp, "Press Space to start", (1, 1, 1))
myFunctions.showText(win, "Waiting for experimenter", (1, 1, 1))
win.flip()
winexp.flip()
writerlog.writerow(["Waiting for Experimenter", core.getTime()])
keypress = event.waitKeys(float('inf'),keyList=['space', 'escape']) #wait for space
if keypress[0] == "escape":
    QuitExperiment()
   
t0 = core.getTime()
writerlog.writerow(["Start of Experiment // Spacebar pressed", "Absolute Time", "Time since t0 [t0 = start of expt]"])
writerlog.writerow(["Start of Experiment // Spacebar pressed", core.getTime(), core.getTime()-t0])

#for recording temperature during each trial
temperatures_in_trial_left = numpy.zeros((400, 5, len(stimuli_list_shuffled)))
temperatures_in_trial_right = numpy.zeros((400, 5, len(stimuli_list_shuffled)))

if paincalibrationYN == "Nein":
    # show some example stimuli so the first trial doesn't come as a shock
    # when we have calibration at the start they are used to the heat, but in other blocks no
    myFunctions.showText(win, "Beispielreiz", (1, 1, 1))
    myFunctions.showText(winexp, "Beispielreiz", (1, 1, 1))
    win.flip()
    winexp.flip()

    if thermode:
            QST_functions.Burn_left([45, 45, 31, 45, 45], [1]*5, [100]*5, [100]*5)
            core.wait(3.0)
            QST_functions.Burn_right([45, 45, 31, 45, 45], [1]*5, [100]*5, [100]*5)
            core.wait(3.0)
            QST_functions.Burn_left([46, 46, 31, 46, 46], [1]*5, [100]*5, [100]*5)
            core.wait(3.0)
            QST_functions.Burn_right([46, 46, 31, 46, 46], [1]*5, [100]*5, [100]*5)
            core.wait(3.0)


if practicesessionYN == "Ja":
    arm = [0, 1]
    random.shuffle(arm)
    side = [0, 1]
    random.shuffle(side)
    
    for i in range(10):
        myFunctions.PracticeSession(thermode, win, winexp, arm, side, parallel_port_mode, bbox)
        arm = numpy.flip(arm) #alternate the arms
        random.shuffle(side) # pick a random side (might not be equalized then, but shouldn't matter
        #that much if it's like 4 left, 6 right. More important probably to equalize the arms)
        core.wait(2)
    


#for each trial
for trial, stimulus in enumerate(stimuli_list_shuffled):
    
    #Work out which type of trial this is
    trial_type = stimulus[2] # give a number 1 to 6
       
    if trial_type == 1: #ThermalHigh_thermal
        myCue = CueHighThermal #or LeftHigh
        myCueExp = CueHighThermalExp
        if sessiontype == "Pain Type":
            myPainType = "thermal"
        elif sessiontype == "Pain Location":
            myPainLocation = "left"
            myPainType = "thermal"
    elif trial_type == 2: #ThermalHigh_mechano
        myCue = CueHighThermal  #or LeftHigh
        myCueExp = CueHighThermalExp
        if sessiontype == "Pain Type":
            myPainType = "mechano"
        elif sessiontype == "Pain Location":
            myPainLocation = "right"
            myPainType = "thermal"
    elif trial_type == 3: #MechanoHigh_mechano
        myCue = CueHighMechano  #or RightHigh
        myCueExp = CueHighMechanoExp
        if sessiontype == "Pain Type":
            myPainType = "mechano"
        elif sessiontype == "Pain Location":
            myPainLocation = "right"
            myPainType = "thermal"
    elif trial_type == 4: #MechanoHigh_thermal
        myCue = CueHighMechano #or RightHigh
        myCueExp = CueHighMechanoExp
        if sessiontype == "Pain Type":
            myPainType = "thermal"
        elif sessiontype == "Pain Location":
            myPainLocation = "left"
            myPainType = "thermal"
    elif trial_type == 5: #Noexpect_thermal
        myCue = CueNoExpect
        myCueExp = CueNoExpectExp
        if sessiontype == "Pain Type":
            myPainType = "thermal"
        elif sessiontype == "Pain Location":
            myPainLocation = "left"
            myPainType = "thermal"
    elif trial_type == 6: #Noexpect_mechano
        myCue = CueNoExpect
        myCueExp = CueNoExpectExp
        if sessiontype == "Pain Type":
            myPainType = "mechano"
        elif sessiontype == "Pain Location":
            myPainLocation = "right"
            myPainType = "thermal"
    
    print(myPainType)
    if sessiontype == "Pain Location":
        print(myPainLocation)
    
    myPainIntensity = stimulus[3]
    if sessiontype == "Pain Type":
        if myPainType == "thermal":
            myPainControlIntensity = temperature_intensity_control
        elif myPainType == "mechano":
            myPainControlIntensity = mechintensity_control
    elif sessiontype == "Pain Location":
        myPainControlIntensity = temperature_intensity_control #we only need temperature for now
        
        
    # PRESENT DEBUG TEXT 
    if stimulus[4] == 0: #present control in position 1
        # position 1 # LEFT ARROW
        myPainControlIntensity
        debugText1 = " {}".format(myPainControlIntensity)
        debugTextPos1 = (-200,-300)
        # position 2  #RIGHT ARROW
        myPainIntensity
        debugText2 = " {}".format(myPainIntensity)
        debugTextPos2 = (200,-300)
    elif stimulus[4] == 1: #present comparison in position 1
        # position 1 
        myPainIntensity
        # LEFT ARROW
        debugText1 = " {}".format(myPainIntensity)
        debugTextPos1 = (-200,-300)
        # position 2
        myPainControlIntensity
        # RIGHT ARROW    
        debugText2 = " {}".format(myPainControlIntensity)
        debugTextPos2 = (200,-300)    
        
        
    
    ## Present fix for 0.5s
    print("Trial {}".format(trial+1))
    print("Stimulus " + stimulus[1])
    
    # present text to the experimenter
    currtrialstring = str("Pain Type: " + str(myPainType) + "\nPain Location: " + str(myPainLocation) + "\nControl: " +
                       str(myPainControlIntensity) + "\nComparison: " + str(myPainIntensity))
    if (trial) % 30 == 0: #on every 25 trials. Trial 25 is coded 24 in python, and we need to give break AFTER 25th
        #so at the start of trial 26 which is trial 25 in python
        #changed to 30
        myFunctions.showText(winexp, "Give Break + Press Space ", (1, -1, -1))
        myFunctions.showText(win, u"Pause. Drück eine beliebige Taste um weiterzumachen ", (1, -1, -1))
    else:
        myFunctions.showText(winexp, "Press Space ", (-1, -1, -1))
        myFunctions.showText(win, u"Drück eine beliebige Taste ", (-1, -1, -1))
    myFunctions.showDebugText(winexp, currtrialstring, (0, 220),whichComputer)
    myFunctions.showDebugText(winexp, "Stimulus: " + str(stimulus[1]),  (0, -200),whichComputer) 
    myFunctions.showDebugText(winexp,("Left" + debugText1),debugTextPos1,whichComputer)
    myFunctions.showDebugText(winexp,("Right" + debugText2),debugTextPos2,whichComputer)
    
    # timing stuff
    # only need to print time stamp on the first frame of something
    timestampprinted_5 = False
    timestampprinted_4 = False
    timestampprinted_3 = False
    timestampprinted_2 = False
    timestampprinted_1 = False
    timestampprinted_stim_onset = False
    
    win.flip()
    winexp.flip()
    
    continueexpt = False
    keypress_exp = []
    keypress_bbox = [] 
    
    
    if parallel_port_mode:
        print("keypress before bbox reset")
        print(keypress_bbox)
        bbox.reset()
        core.wait(0.3)
        print("bbox reset")
        print(keypress_bbox)
    
    
    
    print("Continue?")
    print(continueexpt)
    if keypress_bbox:
        print(keypress_bbox)
    else:
        #print("no keypress yet")
        pass
    
    #counterrrr = 0
    while not continueexpt:
        #counterrrr = counterrrr+1
        #print("cOUNTER")
        #print(counterrrr)
        if parallel_port_mode:
            
            keypress_bbox = bbox.getButtons(timeStamped=False)
            #print("listened for key")
            #print(keypress_bbox)
            
            if keypress_bbox:
                print("keypress after bbox reset + key detected")
                print(keypress_bbox)
                #print(keypress)
                # move left
                if keypress_bbox[0] == 0:
                    print("key detected")
                    print(keypress_bbox)
                    continueexpt = True
                # move right
                elif keypress_bbox[0] == 1:
                    print("key detected")
                    print(keypress_bbox)
                    continueexpt = True
                elif keypress_bbox[0] == 2:
                    print("key detected")
                    print(keypress_bbox)
                    continueexpt = True
                elif keypress_bbox[0] == 3:
                    print("key detected")
                    print(keypress_bbox)
                    continueexpt = True
                else:
                    print('Do you use the correct button box / keys?')
            else:
                #print("no keypress yet")
                pass
        
        keypress_exp = event.getKeys(keyList=['space', 'escape']) #wait for space
        #print(keypress_exp)
        if keypress_exp:
            if keypress_exp[0] == "escape":
                QuitExperiment()
            elif keypress_exp[0] == "space":
                continueexpt = True
        
        
    
   #keypress = event.waitKeys(float('inf'),keyList=['space', 'escape']) #wait for space
# #     Wait for space again once the experimenter knows which stimulation to prepare
# #    important to prepare because pinpricks are not automatically administered
#    if keypress[0] == "escape":
#        QuitExperiment()
#    
    #show fix
    myFunctions.showFix(win, "+", (1, 1, 1))
    myFunctions.showFix(winexp, "Get ready", (1, 1, 1))
    win.flip()
    winexp.flip()
    getready = core.getTime() # set our time = 0 for future calcs
    if eyetrack_mode:
        tk.sendMessage("Trial " + str(trial+1))
        tk.sendMessage("Get ready")
    writerlog.writerow(["Start of Trial %d // Get ready" % (trial+1), "Absolute Time", "Time since t0 [t0 = start of expt]", "Time since trial onset [since getready]"])
    writerlog.writerow(["Start of Trial %d // Get ready" % (trial+1), getready, core.getTime()-t0, core.getTime()-getready])
    
    core.wait(0.5) # wait 500 ms
    winexp.flip() #flip experimenter window
    print(("After 500ms wait  ", core.getTime() - getready))
    writerlog.writerow(["After 500ms wait", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    
    stimonsetTimer = core.CountdownTimer(delay_before_stim_main_experiment - 0.5 + random.uniform(-2,2)) #delay as defined above plus jitter, minus the 500ms wait we already had
    stimonsetTimer.reset()
    delay_stimonset_curr_trial = stimonsetTimer.getTime() #record how much the delay was in each trial, you never know if it will be needed in the analysis XD
    print(delay_stimonset_curr_trial)
    myFunctions.showFix(winexp, "Wait", (1, 1, 1))
    #print(stimonsetTimer.getTime())
    
    # make a countdown for the experimenter
    while stimonsetTimer.getTime() > 0:
        if  stimonsetTimer.getTime() > 5.0:
            myFunctions.showFix(winexp, "Wait", (1, 1, 1))
        elif stimonsetTimer.getTime() > 4.0: # between 4 and 5, don't want to start counting down too early
            myFunctions.showFix(winexp, "5", (1, 1, 1))
            #print("between 4 and 5  " + str(stimonsetTimer.getTime()))
            if timestampprinted_5 == False:  # if not False
                    #print(("After 5s countdown  ", core.getTime() - getready))
                    writerlog.writerow(["Countdown 5s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                    if eyetrack_mode:
                        tk.sendMessage("Countdown 5")
                    timestampprinted_5 = True
            #print(stimonsetTimer.getTime())
        elif stimonsetTimer.getTime() > 3:
            myFunctions.showFix(winexp, "4", (1, 1, 1))
            #print("> 3 " + str(stimonsetTimer.getTime()))
            if timestampprinted_4 == False:  # if not False
                    #print(("After 4s countdown  ", core.getTime() - getready))
                    writerlog.writerow(["Countdown 4s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                    if eyetrack_mode:
                        tk.sendMessage("Countdown 4")
                    timestampprinted_4 = True
            #print(stimonsetTimer.getTime())
        elif stimonsetTimer.getTime() > 2:
            myFunctions.showFix(winexp, "3", (1, 1, 1))
            #print("> 2 " + str(stimonsetTimer.getTime()))
            if timestampprinted_3 == False:  # if not False
                    #print(("After 3s countdown  ", core.getTime() - getready))
                    writerlog.writerow(["Countdown 3s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                    if eyetrack_mode:
                        tk.sendMessage("Countdown 3")
                    timestampprinted_3 = True
            #print(stimonsetTimer.getTime())
        elif stimonsetTimer.getTime() > 1:
            myFunctions.showFix(winexp, "2", (1, 1, 1))
            if timestampprinted_2 == False:  # if not False
                    #print(("After 2s countdown  ", core.getTime() - getready))
                    writerlog.writerow(["Countdown 1s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                    if eyetrack_mode:
                        tk.sendMessage("Countdown 2")
                    timestampprinted_2 = True
            #print(stimonsetTimer.getTime())
                      
        elif stimonsetTimer.getTime() > 0:    
            
            #print(stimonsetTimer.getTime())
            ## Present cue on the last 1s
            myCue.draw() #1st stim
            myCueExp.draw()
            myFunctions.showFix(winexp, "1", (1, 1, 1))
            if timestampprinted_1 == False:  # if not False
                    print(("After 1s countdown  ", core.getTime() - getready))
                    writerlog.writerow(["Countdown 1s + cue", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                    if eyetrack_mode:
                        tk.sendMessage("Countdown 1")
                    timestampprinted_1 = True
                    if brainAmp:
                        signalBrainAmp() #brainAmp trigger 1 for cue onset
            win.flip()
            
        
        winexp.flip()
        
        
        #core.wait(1.0)
    
    ################################
    ## Present cue + pain
    ################################

    # stimulus[4] contains the position of the control, for counterbalancing
    
    # STIM
    #myCue.draw() #1st stim
    myCueExp.draw()
    myFunctions.showFix(winexp, "!!!", (1, 1, 1))
    if timestampprinted_stim_onset == False:  # if not False
                    print(("After stim onset requested ", core.getTime() - getready))
                    writerlog.writerow(["!!! Stim onset request", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                    if eyetrack_mode:
                        tk.sendMessage("Stim onset request")
                    timestampprinted_stim_onset = True
   
       
    if myPainType == "thermal":   
        # placeholder message for debugging
        #LEFT
        #myFunctions.showDebugText(win,("Burn" + debugText1),debugTextPos1,whichComputer)
        #myFunctions.showDebugText(winexp,("Burn" + debugText1),debugTextPos1,whichComputer)
        #Present heat
        
        #need some kind of switch to say whether zone 1+2 or zone 4+5 is activated
        
        
        
        if stimulus[4] == 0: #present control in position 1
            if thermode:
                # for pain type experiment: present heat on each arm (2 zones at any one time?)
                # for pain location experiment: present heat on one arm, depending on location, then judge if zone 1+2 or zone 4+5 is hotter
                
                if sessiontype == "Pain Type": #present stimuli one on each arm
                
                    if whichZones[0] == 1: # zones 1 and 2                
                        QST_functions.Burn_left([myPainControlIntensity, myPainControlIntensity, 31, 31, 31], [1]*5, [100]*5, [100]*5)
                        QST_functions.Burn_right([myPainIntensity, myPainIntensity, 31, 31, 31], [1]*5, [100]*5, [100]*5)
                        
                    else: #zones 4 and 5
                        QST_functions.Burn_left([31, 31, 31, myPainControlIntensity, myPainControlIntensity], [1]*5, [100]*5, [100]*5)
                        QST_functions.Burn_right([31, 31, 31, myPainIntensity, myPainIntensity], [1]*5, [100]*5, [100]*5)
                        
                elif sessiontype == "Pain Location": #present stimuli both within one arm
                    
                    if myPainLocation == "left":
                        QST_functions.Burn_left([myPainControlIntensity, myPainControlIntensity, 31, myPainIntensity, myPainIntensity], [1]*5, [100]*5, [100]*5)
                    elif myPainLocation == "right":
                        QST_functions.Burn_right([myPainControlIntensity, myPainControlIntensity, 31, myPainIntensity, myPainIntensity], [1]*5, [100]*5, [100]*5)
                   
                
            whichZones.reverse() #flip the vector for next time, acts like a switch between 1 and 4        
            print(("After heat onset requested ", core.getTime() - getready))
            writerlog.writerow(["Heat onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
            if eyetrack_mode:
                tk.sendMessage("Heat onset")
            #core.wait(3.0)
        else: #present control in position 2
            if thermode:
                
                if sessiontype == "Pain Type":
                
                    if whichZones[0] == 1: # zones 1 and 2   
                        QST_functions.Burn_right([myPainControlIntensity, myPainControlIntensity, 31, 31, 31], [1]*5, [100]*5, [100]*5)
                        QST_functions.Burn_left([myPainIntensity, myPainIntensity, 31, 31, 31], [1]*5, [100]*5, [100]*5)
                    else:#zones 4 and 5
                        QST_functions.Burn_right([31, 31, 31, myPainControlIntensity, myPainControlIntensity], [1]*5, [100]*5, [100]*5)
                        QST_functions.Burn_left([31, 31, 31, myPainIntensity, myPainIntensity], [1]*5, [100]*5, [100]*5)
                
                elif sessiontype == "Pain Location":
                    if myPainLocation == "left":
                        QST_functions.Burn_left([myPainIntensity, myPainIntensity, 31, myPainControlIntensity, myPainControlIntensity], [1]*5, [100]*5, [100]*5)
                    elif myPainLocation == "right":
                        QST_functions.Burn_right([myPainIntensity, myPainIntensity, 31, myPainControlIntensity, myPainControlIntensity], [1]*5, [100]*5, [100]*5)
                   
                
            whichZones.reverse() #flip the vector for next time, acts like a switch between 1 and 4          
            print(("After heat onset requested ", core.getTime() - getready))
            writerlog.writerow(["Heat onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
            if eyetrack_mode:
                tk.sendMessage("Heat onset")
            #core.wait(3.0)
        print("Burn" + debugText1)
        #RIGHT
        #myFunctions.showDebugText(win,("Burn" + debugText2),debugTextPos2,whichComputer)
        #myFunctions.showDebugText(winexp,("Burn" + debugText2),debugTextPos2,whichComputer)
        print("Burn" + debugText2)
    elif myPainType == "mechano":
        #LEFT
        #myFunctions.showDebugText(win,("Stab" + debugText1),debugTextPos1,whichComputer)
        #myFunctions.showDebugText(winexp,("Stab" + debugText1),debugTextPos1,whichComputer)
        print(("After pinprick onset requested ", core.getTime() - getready))
        writerlog.writerow(["Pinprick onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
        if eyetrack_mode:
            tk.sendMessage("Pinprick onset")
        print("Stab" + debugText1)
        #RIGHT
        #myFunctions.showDebugText(win,("Stab" + debugText2),debugTextPos2,whichComputer)
        #myFunctions.showDebugText(winexp,("Stab" + debugText2),debugTextPos2,whichComputer)
        print(("After pinprick onset requested ", core.getTime() - getready))
        writerlog.writerow(["Pinprick onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
        if eyetrack_mode:
            tk.sendMessage("Pinprick onset")
        print("Stab" + debugText2)
        
    
   
    win.flip()
    winexp.flip()
    #print(("After winflip ", core.getTime() - getready))
    writerlog.writerow(["Winflip after stimulus onset request", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    if eyetrack_mode:
        tk.sendMessage("Winflip after stimulus onset request")
        
    if thermode:    
        # Record temps for 1s
        start_time = time.time()
        print(start_time)
        recordDur = delay_after_stim_main_experiment
        
        left_curr_temps = []
        right_curr_temps = []
        
        timesample = 0
        currtime = time.time()
        while (currtime - start_time) < recordDur:
            #temperatures_in_trial_left[timesample, zones, trial]
            [left_curr_temps, right_curr_temps, datatempleft, datatempright] = QST_functions.RecordTemperature()
            temperatures_in_trial_left[timesample, :, trial] = left_curr_temps
            temperatures_in_trial_right[timesample, :, trial] = right_curr_temps
            timesample = timesample + 1
            currtime = time.time()
            #print(left_curr_temps)
            #print(datatempleft)
            #print(datatempright)
            #print("")
        print(currtime)
        print(currtime-start_time)
        print("Temperature rec finished, elapsed time: " + str(currtime - start_time))
    
    ############################
    ## Record response 
    ############################
    #core.wait(1.0)
    myFunctions.showText(win, 'Welcher Reiz ist schmerzhafter?', (1, 1, 1))
    win.flip()
    RTstart = clock.getTime()
    print(("Response onset ", RTstart - getready))
    writerlog.writerow(["Response onset", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    if eyetrack_mode:
        tk.sendMessage("Response onset")
   
    submittedanswer = False
    #keypress = []
    event.clearEvents()
    # Don't need to record temp here as just do it above now
#    if thermode:    
#        # Record temps for 1s
#        start_time = time.time()
#        recordDur = 1
#        
#        timesample = timesample + 1 # leave a gap between this recording and the previous one
#        currtime = time.time()
#        while (currtime - start_time) < recordDur:
#            #temperatures_in_trial_left[timesample, zones, trial]
#            [left_curr_temps, right_curr_temps] = QST_functions.RecordTemperature()
#            temperatures_in_trial_left[timesample, :, trial] = left_curr_temps
#            temperatures_in_trial_right[timesample, :, trial] = right_curr_temps
#            timesample = timesample + 1
#            currtime = time.time()
#            if not submittedanswer:
#                #print("Recording temp and ans")
#                [submittedanswer, keypress] = RecordAnswer()
#                if submittedanswer:
#                    RTend = clock.getTime()
#                    RT.append(RTend-RTstart)
#                    print("start: {}, end: {}, RT: {}".format(RTstart, RTend, RTend-RTstart))
#                    writerlog.writerow(["Keypress", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#                    if eyetrack_mode:
#                        tk.sendMessage("Response offset")
#                        print("Temperature rec finished, elapsed time: " + str(currtime - start_time))
    while not submittedanswer: #in case the answer was not given during the temperature recording phase
            #print("Recording ans")  
            [submittedanswer, keypress] = myFunctions.RecordAnswer(parallel_port_mode, bbox)
            if submittedanswer:
                RTend = clock.getTime()
                RT.append(RTend-RTstart)    
                print("start: {}, end: {}, RT: {}".format(RTstart, RTend, RTend-RTstart))
                writerlog.writerow(["Keypress", core.getTime(), core.getTime()-t0, core.getTime()-getready])
                if eyetrack_mode:
                    tk.sendMessage("Response offset")
    #feedback
#    print('correct = {}'.format(corrrespstim[stimulus]))
    if keypress != None: #check if not empty
        print('key = {}'. format(keypress[0]))
#        if corrrespstim[stimulus] == key[0]:
#            myFunctions.showText(win, 'correct!', (1, 1, 1))
#        elif corrrespstim[stimulus] != key:
#            myFunctions.showText(win, 'incorrect!', (1, 1, 1))
        if keypress[0] == "escape":
            QuitExperiment()
    else: #key is empty, can't do key[0] subscript
#        print('key = {}'. format(key))
#        myFunctions.showText(win, 'Respond faster!', (1, 1, 1))
        keypress = ['None']
        
    
    win.flip()
    winexp.flip()
#    myFunctions.showText(win, 'Waiting for experimenter', (1, 1, 1))
#    myFunctions.showText(winexp, 'Waiting for space key...', (1, 1, 1))
#    win.flip()
#    winexp.flip()
    writerlog.writerow(["Waiting for space + next trial", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    if eyetrack_mode:
        tk.sendMessage("Waiting for next trial")
        
        
    ## record response in data file and wait for next trial
    # figure out which response to record. We want to record whether they press "more painful" for comparison. This is either L or R arrow depending
    # on the counterbalancing
    if stimulus[4] == 0: #if control left
        if keypress[0] == 'right': #count right key because that's comparison
            response = 1
        elif keypress[0] == 'left': #they answered control more pain
            response = 0
        else: #if something else has been pressed or no key is pressed
            response = 'NaN'
    elif stimulus[4] == 1: #if control right
        if keypress[0] == 'right':  #they answered control more pain
            response = 0
        elif keypress[0] == 'left': #count left key because that's comparison
            response = 1
        else: #if something else has been pressed or no key is pressed
            response = 'NaN'
   # writer.writerow(["Trial number", "Trial Name", "Trial Type ID", "Control Intensity", "Comparison Intensity", "Position of Control", "Sub Resp Raw" "Sub Resp Comparison More Pain", "RT"]) # data file column headers
    print("Write to file trial {}".format(trial+1))
    writer.writerow([trial+1, stimulus[1], stimulus[2], myPainControlIntensity, myPainIntensity, stimulus[4], keypress[0], response, RT[trial], delay_stimonset_curr_trial]) # data file column headers
    
    
    
    
#    keypress = event.waitKeys(float('inf'),keyList=['space', 'escape']) #wait for space to start next trial
#    if keypress[0] == "escape":
#            QuitExperiment()
    #core.wait(1.0)




# show goodbye screen
print("End")
myFunctions.showText(win, u"Danke für die Teilnahme", (1, 1, 1))
myFunctions.showText(winexp, u"Danke für die Teilnahme", (1, 1, 1))
win.flip()
winexp.flip()
writerlog.writerow(["End, danke", core.getTime(), core.getTime()-t0, core.getTime()-getready])
if eyetrack_mode:
    tk.sendMessage("End")
core.wait(1.000)



    
    
QuitExperiment()    