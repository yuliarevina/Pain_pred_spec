#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 15:52:26 2022

@author: user
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import core, clock, data, visual, event, gui, monitors #parallel
import csv, random, time, numpy, sys, platform, os
from pyglet.window import key
import matplotlib.pyplot as plt # for plotting the results
import parallel
from scipy.io import savemat

import psychopy
psychopy.prefs.hardware['audioLib'] = ['PTB', 'pyo','pygame']
print(psychopy.prefs.hardware)

#########
# Stuff still to add

# participant screen, add which hand is being tested and remove the "painful stimulus" instruction for the beginning of calib




    
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
parallel_port_mode = True

#trigger
trigger_mode = False #set to False for debugging without trigger box

# eyetracking
eyetrack_mode = False

#brain amp mode
brainAmp = False

#thermode
thermode = True
#whichComputer = "Home" #python3
#whichComputer = "LaserLab" #python2
whichComputer = "MRI" #python3, run from project folder


if whichComputer == "LaserLab":
    sys.path.insert(1, '/NOBACKUP2/Controlling_QST/')
    sys.path.insert(1, '/NOBACKUP2/Pred_spec/Ulrike_functions/')
    directory="//NOBACKUP2//Pred_spec//"
    if thermode:
        import QST_functions
    import ButtonBoxFunctions as bb
    
elif whichComputer == "MRI":
    sys.path.append('/data/pt_02650/fMRI/Experiment_scripts/')
    sys.path.append('/data/pt_02650/fMRI/Experiment_scripts/Ulrike_functions/')
    directory="/data/pt_02650/fMRI/Experiment_scripts/"
    if thermode:
        import QST_functions
    if parallel_port_mode: #doesn't work with trigger so don't use and set to false!    
        import ButtonBoxFunctions as bb    
else:
    directory="D:\\Yulia\\Psychopy Learning\\"
    
#%%

if trigger_mode:    
    # parallel port from scanner
    p_sc = parallel.Parallel(port = 0)
    p_sc.setDataDir(0)
    p_sc.setData(0)    
    

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
        

      
        
# if parallel_port_mode:
#     # initialize button boxes on port 0
#     timerRating=core.Clock()
#     #p_in = parallel.Parallel(port = 0)
#     #p_in.setDataDir(0)
#     bbox = bb.ButtonBox(port = p_sc, clock = timerRating)
# else:
#     bbox = [] #some functions ask for this so need to define even if blank     


if parallel_port_mode:
    # initialize button boxes on port 0
    timerRating=core.Clock()
    p_in = parallel.Parallel(0)
    p_in.setDataDir(0)
    bbox = bb.ButtonBox(port = p_in, clock = timerRating)
else:
    bbox = [] #some functions ask for this so need to define even if blank                 
        
#%%  

        
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
ramp_speed = [100]*5 # ramp up speed in °C/s for the 5 zones
return_speed = [100]*5 # ramp down speed in °C/s for the 5 zones
mytemperatures = [47]*5 # target temperatures in °C for the 5 zones


## stimulus durations and parameters
stim_dur_calibration = 1.0 #in seconds
stim_dur_main_expt = 1 #in seconds
delay_before_resp_calib = 3.0 #in seconds, so rating scale appears X s after thermode onset
delay_after_stim_calibration = 4.0 #was 8
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

myDlg = gui.Dlg(title="fMRI calibration")
myDlg.addText('Subject info')
myDlg.addField('ID:', '000')
myDlg.addField('Alter:', 21)
myDlg.addField('Geschlecht:', choices=["M", "W", "D"])
#myDlg.addText('Experiment Info')
#myDlg.addField('Grating Ori:',45)
myDlg.addField('Session:', choices=["Pain Type", "Pain Location"])

ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # or if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')    

sub = ok_data[0]
age = ok_data[1]
sex = ok_data[2]
sessiontype = ok_data[3]



def QuitExperiment():
    core.quit()
    
    
    
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

    # ==============================================================
    # preparation
    # ==============================================================
    # Ensure that relative paths start from the same directory as this script
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

    #    try more trials in painful range
        temperatures_calibration_real = [ # not including half degree increments
            42.0, 42.5, 43.0,
            43.5, 44.0, 44.5,
            45.0, 45.5, 46.0,
            46.5, 47.0, 47.5,
            48.0, 48.5, 49.0, 49.0, 49.5,
            49.5, 50.0, 50.0, 50.5, 50.5,
            51.0, 51.0, 51.5,
            51.5, 52.0, 52.0]
        
        

      # # #try more trials in painful range
        # temperatures_calibration_real = [ # not including half degree increments
        #     43.0, 43.5, 44.0,
        #     44.5, 45.0, 45.5,
        #     46.0, 46.5, 47.0,
        #     47.5, 48.0, 48.5,
        #     49.0, 49.5, 50.0, 50.0, 50.5,
        #     50.5, 51.0, 51.0, 51.5, 51.5,
        #     52.0, 52.0, 53.5,
        #     53.5, 54.0, 55.0]

        
        
        
        random.shuffle(temperatures_calibration_real)
        
        temperatures_calibration = temperatures_calibration_real
        #temperatures_calibration = temperatures_calibration_debugging  

        random.shuffle(temperatures_calibration)
            
        for i, eachcalibrationtemp in enumerate(temperatures_calibration):
            if eyetrack_mode:
                tk.sendMessage(str('Calib Trial %d' % (i+1)))  
            print(redo)
            print (i)
            # (stimulate only 2 pads at a time, so 1+2 then 4+5 then 1+2 and so on, to prevent sensitization etc)
            # changed now to 4 pads at a time after some feedback
            if i % 2 == 0: # even number trial
                requiredtemperatures = [eachcalibrationtemp, eachcalibrationtemp, eachcalibrationtemp, eachcalibrationtemp, eachcalibrationtemp]
            else: # odd number trial
                requiredtemperatures = [eachcalibrationtemp, eachcalibrationtemp, eachcalibrationtemp, eachcalibrationtemp, eachcalibrationtemp]

                    
            
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
            
            CalibrationRatingTimer = core.CountdownTimer(5)
            CalibrationRatingTimer.reset()
            
            # ********************** for when we want to remove self-paced *************
            while CalibrationRatingTimer.getTime() > 0:
                if not submittedanswer:
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
                        keypress = event.getKeys(keyList=['left', 'right', 'escape', 'return', 'r']) #wait for Left Arrow or Right Arrow key
                
                
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
                                currentPos = currentPos - 1
                            elif keypress[0] == 3:    
                                currentPos = currentPos + 1
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


temperatures_calibrated = numpy.round((temp75_left+temp75_right)/2)
print(temperatures_calibrated)

win.close()
winexp.close()
core.quit()