
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


#Logging of the spyder console to a text file
Logging_to_file = True
if Logging_to_file:
    logFile = "name.txt"
    logoutput = open(logFile,'w')
    sys.stdout = logoutput # lets me use print() statements

    
thisOS = platform.system()

if thisOS == "Linux":
    slash = "/"
else:   
    slash = "\\"


# *********************************************************
#              Which devices to switch on?
# *********************************************************    

# used computer has a parallel port (for the button boxes)
parallel_port_mode = False

#trigger
trigger_mode = False #set to False for debugging without trigger box

# eyetracking
eyetrack_mode = False

#brain amp mode
brainAmp = False

#thermode
thermode = False

#dual screen
dual_screen = False #if True, create a second screen for the experimenter

#whichComputer = "Home" #python3
#whichComputer = "LaserLab" #python2
whichComputer = "MRI" #python3, run from project folder

if whichComputer == "LaserLab":
    sys.path.insert(1, '/NOBACKUP2/Controlling_QST/')
    sys.path.insert(1, '/NOBACKUP2/Pred_spec/Ulrike_functions/')
    directory="//NOBACKUP2//Pred_spec//"
    if thermode:
        import QST_functions
    if parallel_port_mode: #doesn't work with trigger so don't use and set to false!    
        import ButtonBoxFunctions as bb
elif whichComputer == "MRI":
    sys.path.insert(1, '/data/pt_02650/fMRI/Experiment_scripts/Ulrike_functions/')
    sys.path.append('/data/pt_02650/fMRI/Experiment_scripts/')
    directory="/data/pt_02650/fMRI/Experiment_scripts/"
    if thermode:
        import QST_functions
    if parallel_port_mode: #doesn't work with trigger so don't use and set to false!    
        import ButtonBoxFunctions as bb
        
else:
    directory="D:\\Yulia\\Psychopy Learning\\"
    
    
    
if trigger_mode:    
    # parallel port from scanner
    p_sc = parallel.Parallel(port = 0)
    p_sc.setDataDir(0)
    p_sc.setData(0)    
    
    
    
if parallel_port_mode: #doesn't work with trigger so don't use and set to false!
    # initialize button boxes on port 0
    timerRating=core.Clock()
    p_in = parallel.Parallel(port = 0)
    p_in.setDataDir(0)
    bbox = bb.ButtonBox(port = p_in, clock = timerRating)
else:
    bbox = [] #some functions ask for this so need to define even if blank      
    
    

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
    
# *******************************************************
#                   Timing
# *******************************************************        

#timer for brainAmp
timer = core.Clock()

## SETUP thermode
# settings
baselineTemp = 31.0 # baseline/neutral temperature (for all 5 zones equally)
durations = [1]*5 # stimulation durations in s for the 5 zones
ramp_speed = [100]*5 # ramp up speed in °C/s for the 5 zones
return_speed = [100]*5 # ramp down speed in °C/s for the 5 zones
mytemperatures = [54.9]*5 # target temperatures in °C for the 5 zones


## stimulus durations and parameters
stim_dur_calibration = 1.5 #in seconds
stim_dur_main_expt = 1 #in seconds
cue_dur = 1 # s
#delay_after_stim_calibration = 3.5
#delay_after_stim_main_experiment = 3.0 #how long to wait after stim onset, so if stim is 1s long,
#then this give 2s afterwards before rating scale
#delay_before_stim_main_experiment = 5.0 #gives time for experimenter to start the stimulus (for pinpricks it's manually driven)
#stimonsetTimer = core.CountdownTimer(delay_before_stim_main_experiment)  # runs backwards
#stimonsetTimer.add(delay_before_stim_main_experiment)
# how to use
# while stimonsetTimer.getTime() > 0:
ISI_time = 8.0 #seconds
ISI_timer = core.CountdownTimer(ISI_time)
Schluckpause_len = 10
first_or_last_ISI = 10

total_trial_len = 10.0 #seconds



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
myDlg.addText('Output name e.g. Sub001_Block1_with_eyetrack or Sub002_Block2_rescan')
myDlg.addField('Output_name:', "000")
myDlg.addField('Sub_Number. MUST BE 3 digit code e.g. 001, 002, 013:', "000")
myDlg.addField('Block_number:', choices=["1", "2", "3", "4"])
myDlg.addField('Alter:', 21)
myDlg.addField('Geschlecht:', choices=["M", "W", "D"])
myDlg.addField('Session:', choices=["Pain Location", "Pain Type",])
myDlg.addField('Pain calibration?', choices=['Nein', 'Ja'])
myDlg.addField('Cue order', choices=["1", "2", "3", "4", "5", "6"])
myDlg.addField('Lots of catch trials?', choices=['Nein', 'Ja']) #for debugging put "Ja"
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # or if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')    

outputname = ok_data[0]
sub = ok_data[1]
blocknum = ok_data[2]
age = ok_data[3]
sex = ok_data[4]
sessiontype = ok_data[5]
paincalibrationYN = ok_data[6]
cueorder = ok_data[7]
manycatchtrials = ok_data[8]


# Can manually enter some temperatures from a previous calibration file if needed
# these are overwritten if calibration == Ja by the calibrated values later on in the script

temperatures_debug = [48.5, 49.4, 50.3, 51.3, 52.2] # calibrate to the person's own thresholds?



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
    win.close()
    if dual_screen:
        winexp.close()
    
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
    
    if Logging_to_file:    
        logoutput.close()
        sys.stdout = sys.__stdout__    
    core.quit()




# **************************************************
#    File names
# **************************************************

## Data file
filename="{}data_{}_{}_{}_Cue_{}_{}_{}_{}_{}.csv".format(directory, outputname, sub, blocknum, cueorder, sex, age, sessiontype, time.strftime('%Y-%m-%dT%H_%M_%S')) #for MS Windows
if thisOS == "Linux":
    datafilewrite = open(filename, "w")
else:
    datafilewrite = open(filename, "w", newline='') # windows
writer = csv.writer(datafilewrite, delimiter=";")
writer.writerow(["Trial number", "Trial Name", "Trial Type ID", "Control Intensity", "CatchTrial", "CuePosition", "SubjResponse", "CorrectAnswer?", "RT"]) # data file column headers


## Log file (prints out key events, for timing etc)
filenamelog="{}log{}_{}_{}_Cue_{}_{}_{}_{}_{}.csv".format(directory, outputname, sub, blocknum, cueorder, sex, age, sessiontype, time.strftime('%Y-%m-%dT%H_%M_%S')) #for MS Windows
if thisOS == "Linux":
    logfilewrite = open(filenamelog, "w")
else:
    logfilewrite = open(filenamelog, "w", newline='') # windows
writerlog = csv.writer(logfilewrite, delimiter=";")
#writerlog.writerow(["Trial number", "Trial Name", "Trial Type ID", "Control Intensity", "Comparison Intensity", "Position of Control", "Sub Resp Raw", "Sub Resp Comparison More Pain", "RT"]) # data file column headers


## Log file temperature
filenamelogtemp="{}log{}_{}_{}_Cue_{}_{}_{}_{}_{}.csv".format(directory, outputname, sub, blocknum, cueorder, sex, age, sessiontype, time.strftime('%Y-%m-%dT%H_%M_%S')) #for MS Windows
if thisOS == "Linux":
    logtempfilewrite = open(filenamelogtemp, "w")
else:
    logtempfilewrite = open(filenamelogtemp, "w", newline='') # windows
writerlogtemp = csv.writer(logtempfilewrite, delimiter=";")


#read in ISIs
#sub = ok_data[1]
#blocknum = ok_data[2]
#file string format = Sub001_Block1_pseudorandom.txt

filename_ISI = "{}ISIs//Sub{}_Block{}_pseudorandom_fMRI_96trials.txt".format(directory,sub,blocknum)
ISI_vector = []
try:
    with open(filename_ISI) as f:
        for line in f:
            print(line.strip())
            ISI_vector.append(line.strip())
except:
    print("ERROR \n ISI file cannot be opened, check correct subject ID and Block number has been entered! \n Sub ID must be in 3 digit format: 001, 002, 003 ... 065, 100, etc")
    QuitExperiment()    


# **************************************************
#       Screens
# **************************************************

# set screen properties
#scnWidth, scnHeight = (1920, 1080)
#scnWidth, scnHeight = (1080, 720)
scnWidth, scnHeight = (900, 500)

# define monitor
#mon = monitors.Monitor('laserlab', width=53.0, distance=57.0)
mon = monitors.Monitor('fMRI7T', width=53.0, distance=46.0)
mon.setSizePix((scnWidth, scnHeight))

if dual_screen:
    # window for experimenter
    winexp = visual.Window(
        (1500, 800), fullscr=False, screen=1,
        allowGUI=False, allowStencil=False,
        color=[0.404,0.404,0.404], colorSpace='rgb', waitBlanking = False)
    refreshratewinexp = winexp.getActualFrameRate(nIdentical=10, nMaxFrames=100, nWarmUpFrames=10, threshold=1)
    print(refreshratewinexp)

# window for subject
win = visual.Window(
    (scnWidth, scnHeight), fullscr=False, screen=0,
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
    # try: #python 2, unicode string
    #     thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
    # except: #python 3, string already unicode so no decode function can be used (or needed)
    #     thisDir = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(thisDir)
    
    # Make data folder
    if not os.path.isdir(directory + "data"):
        os.makedirs(directory + "data")
    timestamp = data.getDateStr(format='%Y%m%d_%H%M')    
    #filenameeyetrack = thisDir + os.sep + 'data' + os.sep + 'eyetracking_%s' % (timestamp) + str(outputname) + str(sex) + str(age) + str(sessiontype) +'.edf'
    filenameeyetrack = directory + 'data' + os.sep + 'eyetracking_%s' % (timestamp) + str(outputname) + str(sex) + str(age) + str(sessiontype) +'.edf'

    (tk, edf_running_name) = myFunctions.Eyetracking_calibration(filenameeyetrack, tk, win, winexp, scnWidth, scnHeight, dummyMode)        
    #tk.sendMessage('Start Rec 2') 




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

#****  INSERT PREVIOUSLY CALIBRATED TEMPS HERE *****
#temperatures_debug = mytemperatures

#mytemperatures = temperatures_debug

mechanicalinstensities = [32, 64, 128, 256, 512] #check what these should be, also calibrated individually?

#temperature_intensity_control = mytemperatures[2] # third stimulus in our calibration
temperature_intensity_control = mytemperatures[0] # for debug
mechintensity_control = 128



################################
## Generate stimuli
################################
# Qualitative session [Pain type]
#   Conditions
#   1. 75% Thermo
#   2. 75% Mechano
#   
#
# Spatial session [Pain location]
#   Conditions
#   1. 75% left arm
#   2. 75% right arm
#
#
# General design per block
#   Left High
#       Left = 36 trials
#       Omission = 12 trials
#   Right High
#       Right = 36 trials
#       Omission = 12 trials

# 66 stims per block, randomized


expectation_rate = 3 # 3rice as often as the other stim; 75%
trialspercondition_presented = 36 #36
trialspercondition_omitted = numpy.int(trialspercondition_presented/expectation_rate)
trialspercondition_neutral = 0 #0


if manycatchtrials == "Ja":
    nCatch_Stim = 10
    nCatch_Omiss = 6
    nCatch_Neutral = 10
else:
    nCatch_Stim = 3
    nCatch_Omiss = 1
    nCatch_Neutral = 0


stimuli_list = []
# need to counterbalance which position on the hand is control and which comparison
# stimuli_list = [Trial Num (of this type), Trial Type String, Trial Type Numerical, Intensity Comparison, position_of_control]



# Create list of stims
if sessiontype == "Pain Type":
#    for temperature_intensity in mytemperatures: #for each stimulus temperature
#        for i in range(numpy.int(trialsperpointhigh/2)): #thermal high thermal presented, control position 1
#            stimuli_list.append([i+1, "ThermalHigh_thermal", 1, temperature_intensity, 0])
#        for i in range(numpy.int(trialsperpointhigh/2)): #thermal high thermal presented, control position 2
#            stimuli_list.append([i+1, "ThermalHigh_thermal", 1, temperature_intensity, 1])
#            
#        for i in range(numpy.int(trialsperpointlow/2)): # mechano high thermal presented, control position 1
#            stimuli_list.append([i+1, "MechanoHigh_thermal", 4, temperature_intensity, 0])       
#        for i in range(numpy.int(trialsperpointlow/2)): # mechano high thermal presented, control position 2
#            stimuli_list.append([i+1, "MechanoHigh_thermal", 4, temperature_intensity, 1])  
#            
#        for i in range(numpy.int(noexpectation/2)): # mechano high mechano presented, control position 1
#            stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 0])  
#        for i in range(numpy.int(noexpectation/2)): # mechano high mechano presented, control position 2
#            stimuli_list.append([i+1, "Noexpect_thermal", 5, temperature_intensity, 1])      
    
#    for mechintensity in mechanicalinstensities:
#        for i in range(numpy.int(trialsperpointlow/2)): # thermal high mechano presented, control position 1
#            stimuli_list.append([i+1, "ThermalHigh_mechano", 2, mechintensity, 0])    
#        for i in range(numpy.int(trialsperpointlow/2)): # thermal high mechano presented, control position 2
#            stimuli_list.append([i+1, "ThermalHigh_mechano", 2, mechintensity, 1]) 
#            
#        for i in range(numpy.int(trialsperpointhigh/2)): # mechano high mechano presented, control position 1
#            stimuli_list.append([i+1, "MechanoHigh_mechano", 3, mechintensity, 0]) 
#        for i in range(numpy.int(trialsperpointhigh/2)): # mechano high mechano presented, control position 2
#            stimuli_list.append([i+1, "MechanoHigh_mechano", 3, mechintensity, 1]) 
#            
#        for i in range(numpy.int(noexpectation/2)): # mechano high mechano presented, control position 1
#            stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 0])   
#        for i in range(numpy.int(noexpectation/2)): # mechano high mechano presented, control position 2
#            stimuli_list.append([i+1, "Noexpect_mechano", 6, mechintensity, 1])      
    pass
            
elif sessiontype == "Pain Location": #same location but only thermal for now
    
        #for temperature_intensity in mytemperatures: #for each stimulus temperature
            #the first 6 stims should always be stimulation    
            # put them into a pseudorandomized order
            # stimuli_list.append([1, "LeftHigh_presented", 1, 0])
            # stimuli_list.append([1, "RightHigh_presented", 2, 0])
            # stimuli_list.append([2, "LeftHigh_presented", 1, 0])
            # stimuli_list.append([2, "RightHigh_presented", 2, 0])
            # stimuli_list.append([3, "LeftHigh_presented", 1, 0])
            # stimuli_list.append([3, "RightHigh_presented", 2, 0])
            
            
            
            #PRESENTED
            for i in range(0, numpy.int(trialspercondition_presented)): #left high presented
                stimuli_list.append([i+1, "LeftHigh_presented", 1, 0])
                #stimuli_list.append([i+1, "RightHigh_presented", 2]) #put left, right after one another because we need the 1st 2 trials to be 1 L and 1 R
                
                
            # add catctrials
            catchttrials_stim = numpy.zeros(trialspercondition_presented) #array of length of stimulation trials
            catchttrials_stim[:nCatch_Stim] = numpy.ones(nCatch_Stim) #add catch trials, 1 = catch, 0 = no catch
            numpy.random.shuffle(catchttrials_stim) #shuffle
            #add to stimuli list
            for j in range(trialspercondition_presented):
                stimuli_list[j][3] = catchttrials_stim[j]
                
            stimuli_list_tmp = stimuli_list.copy() # make a temporary copy    
            stimuli_list_tmp_first3LEFT = stimuli_list_tmp[:3].copy() #take first 3 elements
            stimuli_list_tmp_restLEFT = stimuli_list_tmp[3:].copy() # take the remaining elements
            
            stimuli_list = [] #clear list so we can do the same for the right stims
                           
            for i in range(0, numpy.int(trialspercondition_presented)): # right high presented
                stimuli_list.append([i+1, "RightHigh_presented", 2, 0]) 
                
            # add catctrials
            catchttrials_stim = numpy.zeros(trialspercondition_presented) #array of length of stimulation trials
            catchttrials_stim[:nCatch_Stim] = numpy.ones(nCatch_Stim) #add catch trials, 1 = catch, 0 = no catch
            numpy.random.shuffle(catchttrials_stim) #shuffle
            #add to stimuli list
            for j in range(trialspercondition_presented):
                stimuli_list[j][3] = catchttrials_stim[j]
                
            stimuli_list_tmp = stimuli_list.copy() # make a temporary copy    
            stimuli_list_tmp_first3RIGHT = stimuli_list_tmp[:3].copy() #take first 3 elements
            stimuli_list_tmp_restRIGHT = stimuli_list_tmp[3:].copy() # take the remaining elements   
            
            stimuli_list = [] #clear list 
            
                        
            #OMITTED                
            for i in range(numpy.int(trialspercondition_omitted)): # left high omitted
                stimuli_list.append([i+1, "LeftHigh_omitted", 3, 0])    
                
            # we need to add catch trials here to all the _omitted trials
            catchttrials_omiss = numpy.zeros(trialspercondition_omitted) #array of length of stimulation trials
            catchttrials_omiss[:nCatch_Omiss] = numpy.ones(nCatch_Omiss) #add catch trials, 1 = catch, 0 = no catch
            numpy.random.shuffle(catchttrials_omiss) #shuffle
            
            #add to stimuli list
            for j in range(trialspercondition_omitted):
                #print(j)
                stimuli_list[j][3] = catchttrials_omiss[j]  #add to the end of the            stimulation trials    
             
            stimuli_list_tmp_omitLEFT    = stimuli_list.copy()
            
            stimuli_list = [] #clear list     
                
            for i in range(numpy.int(trialspercondition_omitted)): # right high omitted
                stimuli_list.append([i+1, "RightHigh_omitted", 4, 0]) 
                
            # we need to add catch trials here to all the _omitted trials
            catchttrials_omiss = numpy.zeros(trialspercondition_omitted) #array of length of stimulation trials
            catchttrials_omiss[:nCatch_Omiss] = numpy.ones(nCatch_Omiss) #add catch trials, 1 = catch, 0 = no catch
            numpy.random.shuffle(catchttrials_omiss) #shuffle
            
            #add to stimuli list
            for j in range(trialspercondition_omitted):
                #print(j)
                stimuli_list[j][3] = catchttrials_omiss[j]  #add to the end of the stimulation trials
                
            stimuli_list_tmp_omitRIGHT   = stimuli_list.copy()    
            
            stimuli_list = [] #clear list   
            
            # NEUTRAL
            for i in range(numpy.int(trialspercondition_neutral)): # neutral cue that's never followed by pain
                stimuli_list.append([i+1, "Neutral_cue", 5, 0])     
                
                
            # we need to add catch trials here to all the _neutral trials
            catchttrials_neut = numpy.zeros(trialspercondition_neutral) #array of length of stimulation trials
            catchttrials_neut[:nCatch_Neutral] = numpy.ones(nCatch_Neutral) #add catch trials, 1 = catch, 0 = no catch
            numpy.random.shuffle(catchttrials_neut) #shuffle
            
            #add to stimuli list
            for j in range(trialspercondition_neutral):
                stimuli_list[trialspercondition_presented*2 + trialspercondition_omitted*2 + j][3] = catchttrials_neut[j]  #add to the end of the omission trials  
                
                
            stimuli_list_tmp_Neutral   = stimuli_list.copy()     
            
            
            stimuli_list = [] #clear list  
            
            
            
            
            ###### put everything together
            #make a new list for 3 LEFT, 3 RIGHT trials, the first 6 trials should be these ones so we need to shuffle them separately
            stimuli_list_first6 = [] 
            stimuli_list_first6.extend(stimuli_list_tmp_first3LEFT)
            stimuli_list_first6.extend(stimuli_list_tmp_first3RIGHT)
             
            #shuffle pseudorandomly
            stimuli_list = myFunctions.shufflelist(stimuli_list_first6)     
             
             #add the remaining L and R trials
            stimuli_list.extend(stimuli_list_tmp_restLEFT)
            stimuli_list.extend(stimuli_list_tmp_restRIGHT)   
                
            stimuli_list.extend(stimuli_list_tmp_omitLEFT)
            stimuli_list.extend(stimuli_list_tmp_omitRIGHT) 
            
            stimuli_list.extend(stimuli_list_tmp_Neutral) 
            
              
                
                
            
#print(stimuli_list)
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
if dual_screen:
    Pic1exp = visual.ImageStim(winexp, (directory+"image//bild4_masked_matched_bg_179.png"), units="pix", size=(600, 600))
    Pic2exp = visual.ImageStim(winexp, (directory+"image//bild3_masked_matched_bg_179.png"), units="pix", size=(600, 600))
    Pic3exp = visual.ImageStim(winexp, (directory+"image//bild2_masked_matched_bg_179.png"), units="pix", size=(600, 600))



if cueorder == "1":
    Cue1 = Pic1
    Cue2 = Pic2
    Cue3 = Pic3
    if dual_screen:
        Cue1exp = Pic1exp
        Cue2exp = Pic2exp
        Cue3exp = Pic3exp
    cueorderinwords = "1: Left: Bild4, Right: Bild3, Neutral: Bild2"
elif cueorder == "2":
    Cue1 = Pic1
    Cue2 = Pic3
    Cue3 = Pic2 
    if dual_screen:
        Cue1exp = Pic1exp
        Cue2exp = Pic3exp
        Cue3exp = Pic2exp
    cueorderinwords = "2: Left: Bild4, Right: Bild2, Neutral: Bild3"
elif cueorder == "3":
    Cue1 = Pic2
    Cue2 = Pic1
    Cue3 = Pic3
    if dual_screen:
        Cue1exp = Pic2exp
        Cue2exp = Pic1exp
        Cue3exp = Pic3exp
    cueorderinwords = "3: Left: Bild3, Right: Bild4, Neutral: Bild2"
elif cueorder == "4":
    Cue1 = Pic2
    Cue2 = Pic3
    Cue3 = Pic1
    if dual_screen:
        Cue1exp = Pic2exp
        Cue2exp = Pic3exp
        Cue3exp = Pic1exp
    cueorderinwords = "4: Left: Bild3, Right: Bild2, Neutral: Bild4"
elif cueorder == "5":
    Cue1 = Pic3
    Cue2 = Pic1
    Cue3 = Pic2
    if dual_screen:
        Cue1exp = Pic3exp
        Cue2exp = Pic1exp
        Cue3exp = Pic2exp
    cueorderinwords = "5: Left: Bild2, Right: Bild4, Neutral: Bild3"
elif cueorder == "6":
    Cue1 = Pic3
    Cue2 = Pic2
    Cue3 = Pic1
    if dual_screen:
        Cue1exp = Pic3exp
        Cue2exp = Pic2exp
        Cue3exp = Pic1exp
    cueorderinwords = "6: Left: Bild2, Right: Bild3, Neutral: Bild4"


CueHighThermal_or_left = Cue1
CueHighMechano_or_right = Cue2
CueNoExpect = Cue3
if dual_screen:
# same for experimenters screen
    CueHighThermal_or_left_Exp = Cue1exp
    CueHighMechano_or_right_Exp = Cue2exp
    CueNoExpectExp = Cue3exp

print("Cue order: " + cueorderinwords + "\n")



 





# **********************************************************************
# **********************************************************************
#       MAIN EXPERIMENT
# **********************************************************************
# **********************************************************************    




first_6_stims = stimuli_list[0:6] #chop off the 1st 2 stims as these should not be shuffled. We always present
# real pain in the first 6 trials
stimuli_list_shuffled = stimuli_list[6:] #shuffle the rest of the list

list_ok = False
while not list_ok:
    shuffledlist = myFunctions.shufflelist(stimuli_list_shuffled) 
    stimuli_list_shuffled_combined = first_6_stims + shuffledlist # combine
    el_6 = stimuli_list_shuffled_combined[5][2]
    el_7 = stimuli_list_shuffled_combined[6][2]
    el_8 = stimuli_list_shuffled_combined[7][2]
    print("6th to 8th elem " + str([el_6, el_7, el_8]))
    if len(set([el_6, el_7, el_8])) == 1: #if 2nd, 3rd and 4th element are the same
        #bad list
        print("bad stimuli list, try again")
        print(str(len(stimuli_list_shuffled_combined)))
        list_ok = False
    else:
        print("good stimuli list")
        print(str(len(stimuli_list_shuffled_combined)))
        list_ok = True


#random.shuffle(stimuli_list_shuffled) #shuffle the rest of the list
#first_2_stims.append(stimuli_list_shuffled[:])
#stimuli_list_shuffled = first_2_stims + shuffledlist # combine


#for recording temperature during each trial
temperatures_in_trial_left = numpy.zeros((250, 5, len(stimuli_list_shuffled_combined)))
temperatures_in_trial_right = numpy.zeros((250, 5, len(stimuli_list_shuffled_combined)))




RT = []
whichZones = [1, 4]

myPainType = []
myPainLocation = []

if dual_screen:
    myFunctions.showText(winexp, "Press Space to start", (1, 1, 1))
    winexp.flip()
myFunctions.showText(win, "Waiting for experimenter", (1, 1, 1))
win.flip()

writerlog.writerow(["Waiting for Experimenter", core.getTime()])
keypress = event.waitKeys(float('inf'),keyList=['space']) #wait for space


if dual_screen:
    myFunctions.showText(winexp, "Waiting for scanner trigger", (1, 1, 1))
    winexp.flip()
myFunctions.showText(win, "Waiting for scanner trigger", (1, 1, 1))
win.flip()


writerlog.writerow(["Start of Experiment // Trigger Detected", "Absolute t", "t since triggertime", "t since trial onset"])


####################
#    wait for trigger here!!!
if trigger_mode:
    run_trigger = True
    #first_trigger = threading.Event()
    start_time_trigger = 0.0
    #trial_n = 1
    
    for n in range(1): #do several times for debugging or once in real expt
        # just after you recorded a signal, don't listen to it for a while
        # so that it doesn't detect several triggers for one
        time.sleep(0.015)
        run_trigger = True
        while run_trigger:
            # falling edge on pin 10
            if not p_sc.getInAcknowledge():
                tn = core.getTime()
                print ("Trigger " + str(n+1) + " detected")
                print(tn)
                run_trigger = False
                
            keypress = event.getKeys(keyList=['space', 'escape']) #listen for escape
            if keypress:
                if keypress[0] == "escape":
                    QuitExperiment()   
    #            


    #keypress = event.waitKeys(float('inf'),keyList=['t']) #wait for T
    triggertime = tn
else:
    keypress = event.waitKeys(float('inf'),keyList=['t', 'escape']) #wait for T  #
    if keypress:
        if keypress[0] == "escape":
            QuitExperiment() 
    triggertime = core.getTime()
    
#writerlog.writerow(["Start of Experiment // Trigger Detected", core.getTime(), core.getTime()-triggertime])

event.clearEvents()


#getready = core.getTime() # set our time = 0 for future calcs
#t0 = triggertime

################################################################################################################
# Present 1 intial ISI
################################################################################################################
# total_trial_len - 1s of cue - 1s of cue + pain

myFunctions.showFix(win, "+", (1, 1, 1))

if dual_screen:
    #myFunctions.showDebugText(winexp, currtrialstring, (0, 220),whichComputer)
    myFunctions.showDebugText(winexp, "Initial baseline",  (0, -200),whichComputer)
    #myFunctions.showDebugText(winexp,("Temp" + debugText1),debugTextPos1,whichComputer)
    myFunctions.showFix(winexp, "ISI", (1, 1, 1))
    winexp.flip()
win.flip()

if eyetrack_mode:
    tk.sendMessage("After very 1st ISI onset")

first_ISI_start_t = core.getTime()
#writerlog.writerow(["Very 1st baseline start", core.getTime(), core.getTime()-triggertime]) 
writerlog.writerow(["Start of Experiment // Trigger Detected", triggertime, triggertime-triggertime])
writerlog.writerow(["Very 1st baseline start", first_ISI_start_t, first_ISI_start_t-triggertime]) 
datafilewrite.flush() #force write to file, so we don't wait for file.close(). In case script crashes
logfilewrite.flush()

#calculate how much time is left after stimulation. Trial should be 10s with 9s ISI
print("Start of 1st ISI")
print("Total trial len: " + str(total_trial_len))
print("Cue dur + stim dur " + str(cue_dur + stim_dur_main_expt) )
print("Core.getTime - trigger " + str(core.getTime() - triggertime))

#print("ISI length: " + str(total_trial_len - (cue_dur + stim_dur_main_expt) - (core.getTime() - triggertime)))
#core.wait(total_trial_len - (cue_dur + stim_dur_main_expt) - (core.getTime() - triggertime)) # trial duration, minus cue dur, minus stim dur, minus time already elapsed since trigger (a few ms usually)
print("First ISI length: " + str(first_or_last_ISI) + "s")
core.wait(first_or_last_ISI)

print("Offset of very 1st ISI:   " + str(core.getTime() - triggertime))

nSchluck = 0 #count the number of swallowing breaks 
presentSchluck = True #whether to have a swallowing break
catchTrial = False

################################################################################################################
#for each trial
################################################################################################################
for trial, stimulus in enumerate(stimuli_list_shuffled_combined):
    print("Trial " + str(trial+ 1))
    
    if stimulus[3] == 1:
        catchTrial = True
    else:
        catchTrial = False
    
    trial_start_time = core.getTime()
    print ("Trial Start Time:  " + str(trial_start_time))
    #writerlog.writerow(["Trial " + str(trial+1) + " start", trial_start_time, trial_start_time-triggertime, trial_start_time - trial_start_time]) 
    
    # work out ISI length on the current trial and the total trial length
    # ISI is different on each trial so total length will not be 10 s always (but will be on average)
    
    thisISI = float(ISI_vector[trial])
    print("This ISI: " + str(thisISI))
    total_trial_len = cue_dur + stim_dur_main_expt + thisISI
    print("Current total trial length: " + str(total_trial_len ))
    
    #we need to count how much ISI time has elapsed already
    totalISIelapsedsofar = 0
    for i in range(trial): #last i is trial - 1 so for 96 trials, last trial is trial 95 in python, so last i = 94 here. We add up everything until and including the penultimate trial
        totalISIelapsedsofar = totalISIelapsedsofar + float(ISI_vector[i]) #just add everything up so far
    
    ################################
    ## Swallowing break every 12 trials
    ################################
    
    if presentSchluck: #if swallowing break is required
        if (trial != 0) & (trial % 12 == 0): #every 12 trials, at the *start* of the 13th trial. *After* 12 trials are completed. Trial 12 in python is Trial 13 in human 
            counter = 10
            
            textstring = "Blinzelpause " + str(counter)
            myFunctions.showText(win, textstring, (1, 1, 1))
            if dual_screen:
                myFunctions.showText(winexp, textstring, (1, 1, 1))
                winexp.flip()
            win.flip()
           
            start_schluckpause = core.getTime()
            #work out the duration of the swallowing break given delays upstream
            #schluckpause dur = 0s for the behavioural
            dur_schluckpause = Schluckpause_len - (start_schluckpause - (triggertime + (cue_dur + stim_dur_main_expt) * trial + totalISIelapsedsofar + first_or_last_ISI + Schluckpause_len * nSchluck)) # will depend on delays upstream. So would be slightly less than 10s
            schluckpauseCounter = core.CountdownTimer(dur_schluckpause)
            schluckpauseCounter.reset()
            if eyetrack_mode:
                tk.sendMessage("Swallowing break")
            while schluckpauseCounter.getTime() > 0:
                counter = numpy.floor(schluckpauseCounter.getTime()) + 1# get time in s
                           
                textstring = "Blinzelpause " + str(counter)
                
                myFunctions.showText(win, textstring, (1, 1, 1))
                if dual_screen:
                    myFunctions.showText(winexp, textstring, (1, 1, 1))
                    winexp.flip()
                win.flip()
                
            
            #writerlog.writerow(["Trial " + str(trial+1) + " schluckpause start ", start_schluckpause, start_schluckpause-triggertime, start_schluckpause - trial_start_time]) 
            #core.wait(10 - (start_schluckpause - (triggertime + (trial) * 10 + ISI_time)))
            end_schluckpause = core.getTime()
            #writerlog.writerow(["Trial " + str(trial+1) + " schluckpause end ", end_schluckpause, end_schluckpause-triggertime, end_schluckpause - trial_start_time]) 
            print("Schluckpause at the start of Trial " + str(trial + 1) + " " + str(end_schluckpause - start_schluckpause) + " s long")
            nSchluck = nSchluck + 1 #update swallowing counter
    #Work out which type of trial this is
    trial_type = stimulus[2] # give a number 1 to 6
       
    if trial_type == 1: #ThermalHigh_thermal
        myCue = CueHighThermal_or_left #or LeftHigh
        OtherImage1 = CueHighMechano_or_right #the other images not used as cue on this trial
        OtherImage2 = CueNoExpect
        if dual_screen:
            myCueExp = CueHighThermal_or_left_Exp
            OtherImage1Exp = CueHighMechano_or_right_Exp
            OtherImage2Exp = CueNoExpectExp
        if sessiontype == "Pain Type":
            myPainType = "thermal"
        elif sessiontype == "Pain Location":
            myPainLocation = "left"
            myPainType = "thermal"
            omissiontrial = False
    elif trial_type == 3: #ThermalHigh_mechano
        myCue = CueHighThermal_or_left  #or LeftHigh
        OtherImage1 = CueHighMechano_or_right #the other images not used as cue on this trial
        OtherImage2 = CueNoExpect
        if dual_screen:
            myCueExp = CueHighThermal_or_left_Exp
            OtherImage1Exp = CueHighMechano_or_right_Exp
            OtherImage2Exp = CueNoExpectExp
        if sessiontype == "Pain Type":
            myPainType = "mechano"
        elif sessiontype == "Pain Location":
            myPainLocation = "left"
            myPainType = "thermal"
            omissiontrial = True
    elif trial_type == 2: #MechanoHigh_mechano
        myCue = CueHighMechano_or_right  #or RightHigh
        OtherImage1 = CueHighThermal_or_left #the other images not used as cue on this trial
        OtherImage2 = CueNoExpect
        if dual_screen:
            myCueExp = CueHighMechano_or_right_Exp
            OtherImage1Exp = CueHighThermal_or_left_Exp
            OtherImage2Exp = CueNoExpectExp
        if sessiontype == "Pain Type":
            myPainType = "mechano"
        elif sessiontype == "Pain Location":
            myPainLocation = "right"
            myPainType = "thermal"
            omissiontrial = False
    elif trial_type == 4: #MechanoHigh_thermal
        myCue = CueHighMechano_or_right #or RightHigh
        OtherImage1 = CueHighThermal_or_left #the other images not used as cue on this trial
        OtherImage2 = CueNoExpect
        if dual_screen:
            myCueExp = CueHighMechano_or_right_Exp
            OtherImage1Exp = CueHighThermal_or_left_Exp
            OtherImage2Exp = CueNoExpectExp
        if sessiontype == "Pain Type":
            myPainType = "thermal"
        elif sessiontype == "Pain Location":
            myPainLocation = "right"
            myPainType = "thermal"
            omissiontrial = True
    elif trial_type == 5: #Noexpect
        myCue = CueNoExpect
        OtherImage1 = CueHighThermal_or_left #the other images not used as cue on this trial
        OtherImage2 = CueHighMechano_or_right
        if dual_screen:
            myCueExp = CueNoExpectExp
            OtherImage1Exp = CueHighThermal_or_left_Exp
            OtherImage2Exp = CueHighMechano_or_right_Exp
        if sessiontype == "Pain Type":
            myPainType = "thermal"
        elif sessiontype == "Pain Location":
            myPainLocation = "left" #just a placeholder, we won't present anything
            myPainType = "thermal"
            omissiontrial = True #we don't need to present stimulus in neutral trials
#    elif trial_type == 6: #Noexpect_mechano
#        myCue = CueNoExpect
#        myCueExp = CueNoExpectExp
#        if sessiontype == "Pain Type":
#            myPainType = "mechano"
#        elif sessiontype == "Pain Location":
#            myPainLocation = "right"
#            myPainType = "thermal"
    
    print("Trial type: " + str(trial_type))
    print("Pain type: " + myPainType)
    if sessiontype == "Pain Location":
        print("Pain location: " + myPainLocation)
        print("Omission: " + str(omissiontrial))
        #print("")
    
    #myPainIntensity = stimulus[3]
    if sessiontype == "Pain Type":
        if myPainType == "thermal":
            myPainControlIntensity = temperature_intensity_control
        elif myPainType == "mechano":
            myPainControlIntensity = mechintensity_control
    elif sessiontype == "Pain Location":
        myPainControlIntensity = temperature_intensity_control #we only need temperature for now
        
        
    # PRESENT DEBUG TEXT 
    myPainControlIntensity
    debugText1 = " {}".format(myPainControlIntensity)
    debugTextPos1 = (-200,-300)
#    
#    if stimulus[4] == 0: #present control in position 1
#        # position 1 # LEFT ARROW
#        myPainControlIntensity
#        debugText1 = " {}".format(myPainControlIntensity)
#        debugTextPos1 = (-200,-300)
#        # position 2  #RIGHT ARROW
#        myPainIntensity
#        debugText2 = " {}".format(myPainIntensity)
#        debugTextPos2 = (200,-300)
#    elif stimulus[4] == 1: #present comparison in position 1
#        # position 1 
#        myPainIntensity
#        # LEFT ARROW
#        debugText1 = " {}".format(myPainIntensity)
#        debugTextPos1 = (-200,-300)
#        # position 2
#        myPainControlIntensity
#        # RIGHT ARROW    
#        debugText2 = " {}".format(myPainControlIntensity)
#        debugTextPos2 = (200,-300)    
#        
        
    
    ## Present fix for 0.5s
    #print("Trial {}".format(trial + 1))
    print("Stimulus " + stimulus[1])
    
    
    # present text to the experimenter
    currtrialstring = str("Trial: " + str(trial+1) + "\nTrial Type: " + str(trial_type) + "\nPain Type: " + str(myPainType) + "\nPain Location: " + str(myPainLocation) + "\Temp: " +
                       str(myPainControlIntensity) + "\nOmission: " + str(omissiontrial))
    if dual_screen:
        myCueExp.draw()
        myFunctions.showDebugText(winexp, currtrialstring, (0, 220),whichComputer)
        myFunctions.showDebugText(winexp, "Stimulus: " + str(stimulus[1]),  (0, -200),whichComputer) 
        myFunctions.showDebugText(winexp,("Temp" + debugText1),debugTextPos1,whichComputer)
        winexp.flip()
    
#    # timing stuff
#    # only need to print time stamp on the first frame of something
#    timestampprinted_5 = False
#    timestampprinted_4 = False
#    timestampprinted_3 = False
#    timestampprinted_2 = False
#    timestampprinted_1 = False
#    timestampprinted_stim_onset = False

    
    
    #keypress = event.waitKeys(float('inf'),keyList=['space']) #wait for space
    # Wait for space again once the experimenter knows which stimulation to prepare
    # important to prepare because pinpricks are not automatically administered
    
#    #show fix
#    myFunctions.showFix(win, "+", (1, 1, 1))
#    myFunctions.showFix(winexp, "Get ready", (1, 1, 1))
#    win.flip()
#    winexp.flip()
#    getready = core.getTime() # set our time = 0 for future calcs
#    if eyetrack_mode:
#        tk.sendMessage("Get ready")
#    writerlog.writerow(["Start of Trial %d // Get ready" % trial, "Absolute Time", "Time since t0 [t0 = start of expt]", "Time since trial onset [since getready]"])
#    writerlog.writerow(["Start of Trial %d // Get ready" % trial, getready, core.getTime()-t0, core.getTime()-getready])
#    
#    core.wait(0.5) # wait 500 ms
#    winexp.flip() #flip experimenter window
#    print(("After 500ms wait  ", core.getTime() - getready))
#    writerlog.writerow(["After 500ms wait", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#    
#    stimonsetTimer.reset()
    
    #print(stimonsetTimer.getTime())
    
#    # make a countdown for the experimenter
#    while stimonsetTimer.getTime() > 0:
#        
#        if stimonsetTimer.getTime() > 4:
#            myFunctions.showFix(winexp, "5", (1, 1, 1))
#            if timestampprinted_5 == False:  # if not False
#                    #print(("After 5s countdown  ", core.getTime() - getready))
#                    writerlog.writerow(["Countdown 5s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#                    if eyetrack_mode:
#                        tk.sendMessage("Countdown 5")
#                    timestampprinted_5 = True
#            #print(stimonsetTimer.getTime())
#        elif stimonsetTimer.getTime() > 3:
#            myFunctions.showFix(winexp, "4", (1, 1, 1))
#            if timestampprinted_4 == False:  # if not False
#                    #print(("After 4s countdown  ", core.getTime() - getready))
#                    writerlog.writerow(["Countdown 4s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#                    if eyetrack_mode:
#                        tk.sendMessage("Countdown 4")
#                    timestampprinted_4 = True
#            #print(stimonsetTimer.getTime())
#        elif stimonsetTimer.getTime() > 2:
#            myFunctions.showFix(winexp, "3", (1, 1, 1))
#            if timestampprinted_3 == False:  # if not False
#                    #print(("After 3s countdown  ", core.getTime() - getready))
#                    writerlog.writerow(["Countdown 3s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#                    if eyetrack_mode:
#                        tk.sendMessage("Countdown 3")
#                    timestampprinted_3 = True
#            #print(stimonsetTimer.getTime())
#        elif stimonsetTimer.getTime() > 1:
#            myFunctions.showFix(winexp, "2", (1, 1, 1))
#            if timestampprinted_2 == False:  # if not False
#                    #print(("After 2s countdown  ", core.getTime() - getready))
#                    writerlog.writerow(["Countdown 1s", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#                    if eyetrack_mode:
#                        tk.sendMessage("Countdown 2")
#                    timestampprinted_2 = True
#            #print(stimonsetTimer.getTime())
#                      
#        elif stimonsetTimer.getTime() > 0:    
            
            #print(stimonsetTimer.getTime())
            ## Present cue on the last 1s
    myCue.draw() #1st stim
            #myCueExp.draw()
            #myFunctions.showFix(winexp, "1", (1, 1, 1))
#            if timestampprinted_1 == False:  # if not False
#                    print(("After 1s countdown  ", core.getTime() - getready))
#                    writerlog.writerow(["Countdown 1s + cue", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    win.flip()
     
    if eyetrack_mode:
         tk.sendMessage("Cue onset")
    if brainAmp:
         signalBrainAmp() #brainAmp trigger 1 for cue onset
   
    
    cue_shown_time = core.getTime()
    print ("Cue Shown X s after trial onset:   " + str(cue_shown_time - trial_start_time))
        
    #writerlog.writerow(["Trial " + str(trial + 1) + "Cue onset", cue_shown_time, cue_shown_time-triggertime, cue_shown_time - trial_start_time])    
        #winexp.flip()
        
        
    core.wait(cue_dur) #present cue for 1s
    
    ################################
    ## Present cue + pain
    ################################

    # stimulus[4] contains the position of the control, for counterbalancing
    
    # STIM
    myCue.draw() #1st stim
    #myCueExp.draw()
    if dual_screen:
        myFunctions.showFix(winexp, "!!!", (1, 1, 1))
#    if timestampprinted_stim_onset == False:  # if not False
#                    print(("After stim onset requested ", core.getTime() - getready))
#                    writerlog.writerow(["!!! Stim onset request", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    stim_onset_request_t = core.getTime()
    if eyetrack_mode:
        tk.sendMessage("Pain Stim onset request")
    print("Pain Stim onset request: " + str(stim_onset_request_t - triggertime) + " s after trigger and " + str(stim_onset_request_t - trial_start_time) + " s after trial onset")
    #writerlog.writerow(["Trial " + str(trial + 1) + "Pain Stim onset request", stim_onset_request_t, stim_onset_request_t-triggertime, stim_onset_request_t - trial_start_time])  
   
       
    if myPainType == "thermal":   
        # placeholder message for debugging
        #LEFT
        #myFunctions.showDebugText(win,("Burn" + debugText1),debugTextPos1,whichComputer)
        #myFunctions.showDebugText(winexp,("Burn" + debugText1),debugTextPos1,whichComputer)
        #Present heat
        
        #need some kind of switch to say whether zone 1+2 or zone 4+5 is activated
        
        
        
         ##if thermode: #make separate if statements below. If running in debug mode w/o thermode we still need to run the code below to get 
         #the correct timestamps for each trial
                    # for pain type experiment: present heat on each arm (2 zones at any one time?)
                    # for pain location experiment: present heat on one arm, depending on location, then judge if zone 1+2 or zone 4+5 is hotter
                    
             if sessiontype == "Pain Type": #present stimuli one on each arm
                if whichZones[0] == 1: # zones 1 and 2   
                  if thermode:
                    QST_functions.Burn_left([myPainControlIntensity, myPainControlIntensity, 31, 31, 31], [stim_dur_main_expt]*5, [100]*5, [100]*5)
                    QST_functions.Burn_right([myPainControlIntensity, myPainControlIntensity, 31, 31, 31], [stim_dur_main_expt]*5, [100]*5, [100]*5)
                    
                else: #zones 4 and 5
                  if thermode:
                    QST_functions.Burn_left([31, 31, 31, myPainControlIntensity, myPainControlIntensity], [stim_dur_main_expt]*5, [100]*5, [100]*5)
                    QST_functions.Burn_right([31, 31, 31, myPainControlIntensity, myPainControlIntensity], [stim_dur_main_expt]*5, [100]*5, [100]*5)
                    
             elif sessiontype == "Pain Location": #present stimuli both within one arm
                if not omissiontrial:
                    if myPainLocation == "left":
                        if thermode:
                            QST_functions.Burn_left([myPainControlIntensity, myPainControlIntensity, myPainControlIntensity, myPainControlIntensity, myPainControlIntensity], [stim_dur_main_expt]*5, [100]*5, [100]*5)
                        
                        #whichZones.reverse() #flip the vector for next time, acts like a switch between 1 and 4        
                        heat_onset_request_time = core.getTime()
                        print("After heat onset requested " + str(heat_onset_request_time - triggertime) + " s after trigger and "+ str(heat_onset_request_time - trial_start_time) + " s after trial onset")
                        #writerlog.writerow(["Trial " + str(trial + 1) + "Heat onset requested", heat_onset_request_time, heat_onset_request_time-triggertime, heat_onset_request_time-trial_start_time])
                        if eyetrack_mode:
                            tk.sendMessage("Trial " + str(trial + 1) + " Heat onset requested")
                        
                    elif myPainLocation == "right":
                        if thermode:
                            QST_functions.Burn_right([myPainControlIntensity, myPainControlIntensity, myPainControlIntensity, myPainControlIntensity, myPainControlIntensity], [stim_dur_main_expt]*5, [100]*5, [100]*5)
                            
                        #whichZones.reverse() #flip the vector for next time, acts like a switch between 1 and 4        
                        heat_onset_request_time = core.getTime()
                        print("After heat onset requested " + str(heat_onset_request_time - triggertime) + " s after trigger and "+ str(heat_onset_request_time - trial_start_time) + " s after trial onset")
                        #writerlog.writerow(["Trial " + str(trial + 1) + "Heat onset requested", heat_onset_request_time, heat_onset_request_time-triggertime, heat_onset_request_time-trial_start_time])
                        if eyetrack_mode:
                            tk.sendMessage("Trial " + str(trial + 1) + " Heat onset requested")
                else: #omission trial, don't present heat
                     omission_onset_request_time = core.getTime()
                     print(("After omission onset requested "+ str(omission_onset_request_time - triggertime) + " s after trigger and " + str(omission_onset_request_time - trial_start_time) + " s after trial onset"))
                     #writerlog.writerow(["Trial " + str(trial + 1) + " Omission onset requested", omission_onset_request_time, omission_onset_request_time-triggertime, omission_onset_request_time-trial_start_time])
                     if eyetrack_mode:
                        tk.sendMessage("Trial " + str(trial + 1) + " Omission onset request")
                #core.wait(3.0)
           
                       
                    
                #whichZones.reverse() #flip the vector for next time, acts like a switch between 1 and 4          
               # print(("After heat onset requested ", core.getTime() - getready))
                #writerlog.writerow(["Heat onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
#                if eyetrack_mode:
#                    tk.sendMessage("Heat onset")
                #core.wait(3.0)
#                if not omissiontrial:
#                    writerlog.writerow(["Trial " + str(trial + 1) + "Stim onset", core.getTime(), core.getTime()-trial_start_time])  
#                else:
#                    writerlog.writerow(["Trial " + str(trial + 1) + "Omission onset", core.getTime(), core.getTime()-trial_start_time])  
                print("Burn" + debugText1)
              
    elif myPainType == "mechano":
        
        if sessiontype == "Pain Type": #present stimuli one on each arm
    #        print(("After pinprick onset requested ", core.getTime() - getready))
    #        writerlog.writerow(["Pinprick onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
            if eyetrack_mode:
                tk.sendMessage("Pinprick onset")
            print("Stab" + debugText1)
            #LEFT
            #RIGHT
        elif sessiontype == "Pain Location": #present stimuli both within one arm    
    #        print(("After pinprick onset requested ", core.getTime() - getready))
    #        writerlog.writerow(["Pinprick onset requested", core.getTime(), core.getTime()-t0, core.getTime()-getready])
            if eyetrack_mode:
                tk.sendMessage("Pinprick onset")
            print("Stab" + debugText1)
        
    
   
    win.flip()
    if dual_screen:
        winexp.flip()
    #print(("After winflip ", core.getTime() - getready))
    #writerlog.writerow(["Winflip after stimulus onset request", core.getTime(), core.getTime()-t0, core.getTime()-getready])
    if eyetrack_mode:
        tk.sendMessage("After winflip")
        
        
    # start of 1s temp rec
    start_of_1stTempRec = core.getTime()
    print("Start of 1st Temp rec: " + str(start_of_1stTempRec-triggertime) + " after trigger and " + str(start_of_1stTempRec - trial_start_time) + " after trial start")
    #writerlog.writerow(["Trial " + str(trial + 1) + "After win flip + start of temp rec", start_of_1stTempRec, start_of_1stTempRec-triggertime, start_of_1stTempRec - trial_start_time])      
    if thermode:    
        # Record temps for 1s
        start_time = time.time()
        recordDur = 1
        
        timesample = 0
        currtime = time.time()
        while (currtime - start_time) < recordDur:
            #temperatures_in_trial_left[timesample, zones, trial]
            [left_curr_temps, right_curr_temps,  datatempleft, datatempright] = QST_functions.RecordTemperature()
            temperatures_in_trial_left[timesample, :, trial] = left_curr_temps
            temperatures_in_trial_right[timesample, :, trial] = right_curr_temps
            timesample = timesample + 1
            currtime = time.time()
    else:
        core.wait(1)
    temp_rec_1_start = core.getTime()
    print("Trial " + str(trial + 1) + "Temp rec 1 ends "+ str(core.getTime()-triggertime) + " after trigger and " + str(core.getTime() - trial_start_time) + " after trial start")
    #writerlog.writerow(["Trial " + str(trial + 1) + "Temp rec 1 ends", core.getTime(), core.getTime() - triggertime, core.getTime()-trial_start_time])  

    # =============================================================================
    #     ISI    
    # =============================================================================
    myFunctions.showFix(win, "+", (1, 1, 1))
    if dual_screen:
        myFunctions.showDebugText(winexp, currtrialstring, (0, 220),whichComputer)
        #myFunctions.showDebugText(winexp, "Stimulus: " + str(stimulus[1]),  (0, -200),whichComputer) 
        #myFunctions.showDebugText(winexp,("Temp" + debugText1),debugTextPos1,whichComputer)
        myFunctions.showFix(winexp, "ISI", (1, 1, 1))
        winexp.flip()
    
    win.flip()
    
    #calculate how much time is left after stimulation. Trial should be 10s with 9s ISI
    onset_of_ISI = core.getTime()
    print("Onset of ISI X s after trial start:   " + str(onset_of_ISI - trial_start_time))
    #print("Onset of ISI X s after trial start:   " + str(onset_of_ISI - (triggertime + (trial+1) * 10 + ISI_time)))
    # remember total_trial_len already includes the current trial's requested ISI (so total_trial_len is different on each trial)
    # formula = length - stim - delay
    # delay = time_now - time_it_should_be
    #time_it_should_be = trigger + 2 x NTrials + totalISIs + FirstISI + NSchluck
    # putting it all together = length - (time_now - (trigger + 2 x NTrials + totalISIs + FirstISI + NSchluck))
    print("ISI should be " + str(total_trial_len - (cue_dur + stim_dur_main_expt) - (onset_of_ISI - (triggertime + (cue_dur + stim_dur_main_expt) * (trial+1) + totalISIelapsedsofar + first_or_last_ISI + Schluckpause_len * nSchluck))) + " s long...")
  
    if eyetrack_mode:
        tk.sendMessage("After ISI onset")
    
    #writerlog.writerow(["Trial " + str(trial + 1) + "ISI onset", onset_of_ISI, onset_of_ISI - triggertime, onset_of_ISI-trial_start_time]) 
     
    
    if thermode:    #record another 1s 
        timesample = timesample + 1 # leave a gap in the log file rows
        # Record temps for 1s
        start_time = time.time()
        recordDur = 1
        
        #timesample = 0
        currtime = time.time()
        while (currtime - start_time) < recordDur:
            #temperatures_in_trial_left[timesample, zones, trial]
            [left_curr_temps, right_curr_temps,  datatempleft, datatempright] = QST_functions.RecordTemperature()
            temperatures_in_trial_left[timesample, :, trial] = left_curr_temps
            temperatures_in_trial_right[timesample, :, trial] = right_curr_temps
            timesample = timesample + 1
            currtime = time.time()
    else:
        core.wait(1.0)
    temp_rec_2_end = core.getTime()    
    print("Trial " + str(trial + 1) + " Temp rec 2 ends " + str(temp_rec_2_end-triggertime) + " after trigger and " + str(temp_rec_2_end - trial_start_time) + " after trial start")
    #writerlog.writerow(["Trial " + str(trial + 1) + "Temp rec 2 ends", core.getTime(), core.getTime() - triggertime, core.getTime()-trial_start_time])    
    
    
    end_of_temp_rec = core.getTime()
    print("End of temp rec X s after trial start:   " + str(end_of_temp_rec - trial_start_time))
    remainingISI = total_trial_len - (cue_dur + stim_dur_main_expt) - (end_of_temp_rec - (triggertime + (cue_dur + stim_dur_main_expt) * (trial+1) + totalISIelapsedsofar + first_or_last_ISI + Schluckpause_len * nSchluck))

    print("Rest of ISI should be " + str(remainingISI) + "s long...")
    #core.wait(remainingISI) #pinned to the trigger start rather than trial start
    
    #catch trial here
    whichImage_toshow = numpy.random.permutation(2)
    side_of_cue = numpy.random.permutation(2)
    corrAns = ["none"]
    submittedanswer = False
    keypress = ["NaN"]
    RT = "NaN"
    response = "NaN"
    start_catch_trial = core.getTime()
    if catchTrial:
        if eyetrack_mode:
            tk.sendMessage("CatchTrial_Start")
        while (core.getTime() - start_catch_trial) < remainingISI:
            if (not submittedanswer) & ((core.getTime() - start_catch_trial) < 3): #if no answer yet and less than 3s have elapsed
                if dual_screen:    
                    myFunctions.showDebugText(winexp, "Which cue was presented?",  (0, -200),whichComputer)
                
                myFunctions.showDebugText(win, "Welches Bild\nhaben Sie\ngerade gesehen?",  (0, -200),whichComputer)
                
                print("Time now - start catch trial " + str((core.getTime() - start_catch_trial)))
                if (whichImage_toshow[0] == 0) & (side_of_cue[0] == 0): #show distractor 1 on the right and cue on the left
                    print("Which image to show " + str(whichImage_toshow))
                    print("Side of cue " + str(side_of_cue)) 
                    print("Which Image to show = 0? " + str(whichImage_toshow[0] == 0))
                    print("Side of cue = 0? " + str(side_of_cue[0] == 0))
                    print("Dist 1 right, cue left")    
                    OtherImage1.pos = (500, 0) #right
                    OtherImage1.draw()
                    myCue.pos = (-500, 0) #left
                    myCue.draw()
                    if dual_screen:
                        OtherImage1Exp.pos = (500, 0)
                        myCueExp.pos = (-500, 0)
                        myCueExp.draw()
                        OtherImage1Exp.draw()
                    corrAns = "left"
                    print("Side of cue")
                    print(str(side_of_cue[0]))
                    print(corrAns + " should be correct answer" )
                
                elif (whichImage_toshow[0] == 1) & (side_of_cue[0] == 0): #show distractor 2 on the right and cue on the left
                    print("Which image to show " + str(whichImage_toshow))
                    print("Side of cue " + str(side_of_cue)) 
                    print("Which Image to show = 1? " + str(whichImage_toshow[0] == 1))
                    print("Side of cue = 0? " + str(side_of_cue[0] == 0))
                    print("Dist 2 right, cue left")
                    OtherImage2.pos = (500, 0) #right
                    OtherImage2.draw()
                    myCue.pos = (-500, 0) #left
                    myCue.draw()
                    if dual_screen:
                        OtherImage2Exp.pos = (500, 0)
                        OtherImage2Exp.draw()  
                        myCueExp.pos = (-500, 0)
                        myCueExp.draw()
                    corrAns = "left"
                    print("Side of cue")
                    print(str(side_of_cue[0]))
                    print(corrAns + " should be correct answer" )
                
                elif (whichImage_toshow[0] == 0) & (side_of_cue[0] == 1): #show distractor 1 on the left and cue on the right
                    print("Which image to show " + str(whichImage_toshow))
                    print("Side of cue " + str(side_of_cue)) 
                    print("Which Image to show = 0? " + str(whichImage_toshow[0] == 0))
                    print("Side of cue = 1? " + str(side_of_cue[0] == 1))
                    print("Dist 1 left, cue right")
                    OtherImage1.pos = (-500, 0) #left
                    OtherImage1.draw()
                    myCue.pos = (500, 0) #right
                    myCue.draw()
                    if dual_screen:
                        OtherImage1Exp.pos = (-500, 0)
                        OtherImage1Exp.draw()
                        myCueExp.pos = (500, 0)
                        myCueExp.draw()
                    corrAns = "right"
                    print("Side of cue")
                    print(str(side_of_cue[0]))
                    print(corrAns + " should be correct answer" )
                
                elif (whichImage_toshow[0] == 1) & (side_of_cue[0] == 1): #show distractor 2 on the left and cue on the right
                    print("Which image to show " + str(whichImage_toshow))
                    print("Side of cue " + str(side_of_cue)) 
                    print("Which Image to show = 1? " + str(whichImage_toshow[0] == 1))
                    print("Side of cue = 1? " + str(side_of_cue[0] ==1))
                    print("Dist 2 LEFT, cue RIGHT")
                    OtherImage2.pos = (-500, 0) #left
                    OtherImage2.draw()
                    myCue.pos = (500, 0) #right
                    myCue.draw()
                    if dual_screen:
                        OtherImage2Exp.pos = (-500, 0)
                        OtherImage2Exp.draw()
                        myCueExp.pos = (500, 0)
                        myCueExp.draw()
                    corrAns = "right"
                    print("Side of cue")
                    print(str(side_of_cue[0]))
                    print(corrAns + " should be correct answer" )
                
                win.flip()
                if dual_screen:
                    winexp.flip()
                
                #record answer
                [submittedanswer, keypress, keypresskeyboard] = myFunctions.RecordAnswer(parallel_port_mode, bbox)
                if submittedanswer:
                    RTend = core.getTime()
                    RT = (RTend-start_catch_trial)
                    if eyetrack_mode:
                        tk.sendMessage("Response_submitted")
                    print("Submitted ans") 
                    print(str(keypress[0]))
                else:
                    RTend = core.getTime() #record end of response period if answer is not given
                    
            else: #if submitted answer or already more than 3s for response, just show fix
                 myFunctions.showFix(win, "+", (1, 1, 1))
                 win.flip()
                 if dual_screen:
                     myFunctions.showDebugText(winexp, currtrialstring, (0, 220),whichComputer)
                     #myFunctions.showDebugText(winexp, "Stimulus: " + str(stimulus[1]),  (0, -200),whichComputer) 
                     #myFunctions.showDebugText(winexp,("Temp" + debugText1),debugTextPos1,whichComputer)
                     myFunctions.showFix(winexp, "ISI", (1, 1, 1))
                     winexp.flip()
                 
                 
                 
            
            #reset image positions
            myCue.pos = (0, 0) #center
            OtherImage1.pos = (0, 0)
            OtherImage2.pos = (0, 0)
            if dual_screen:
                myCueExp.pos = (0, 0) #center
                OtherImage1Exp.pos = (0, 0)
                OtherImage2Exp.pos = (0, 0)
            
            
           
                    
        # work out if the response was correct            
        if keypress:
            if corrAns == "left": #if control left
                if keypress[0] == 'left': #correct answer
                        response = 1
                elif keypress[0] == 'right': #wrong answer
                        response = 0
                else: #if something else has been pressed or no key is pressed
                        response = 'NaN'
            elif corrAns == "right": #if control right
                if keypress[0] == 'right':   #correct answer
                    response = 1
                elif keypress[0] == 'left': #wrong answer
                    response = 0
                else: #if something else has been pressed or no key is pressed
                    response = 'NaN'    
        else:
            keypress = ["NaN"]
    else:
        core.wait(remainingISI) #pinned to the trigger start rather than trial start
    
    trial_end_time = core.getTime()
    print("Trial end: " + str(trial_end_time - trial_start_time))
    
    write_csv_start = core.getTime()

    writerlog.writerow(["Trial " + str(trial+1) + " start", trial_start_time, trial_start_time-triggertime, trial_start_time - trial_start_time]) 
    if presentSchluck:
        if (trial != 0) & (trial % 12 == 0): #if schluckpause
            writerlog.writerow(["Trial " + str(trial+1) + " schluckpause start ", start_schluckpause, start_schluckpause-triggertime, start_schluckpause - trial_start_time]) 
            writerlog.writerow(["Trial " + str(trial+1) + " schluckpause end ", end_schluckpause, end_schluckpause-triggertime, end_schluckpause - trial_start_time]) 
        
        
    writerlog.writerow(["Trial " + str(trial+1) + " Cue onset", cue_shown_time, cue_shown_time-triggertime, cue_shown_time - trial_start_time])    
    writerlog.writerow(["Trial " + str(trial+1) + " Pain Stim onset request", stim_onset_request_t, stim_onset_request_t-triggertime, stim_onset_request_t - trial_start_time])  
    if not omissiontrial:
        writerlog.writerow(["Trial " + str(trial + 1) + " Heat onset requested", heat_onset_request_time, heat_onset_request_time-triggertime, heat_onset_request_time-trial_start_time])
    else:
        writerlog.writerow(["Trial " + str(trial + 1) + " Omission onset requested", omission_onset_request_time, omission_onset_request_time-triggertime, omission_onset_request_time-trial_start_time])

    writerlog.writerow(["Trial " + str(trial + 1) + " After win flip + start of temp rec", start_of_1stTempRec, start_of_1stTempRec-triggertime, start_of_1stTempRec - trial_start_time])       
    writerlog.writerow(["Trial " + str(trial+1) + " Temp rec 1 ends", temp_rec_1_start, temp_rec_1_start - triggertime, temp_rec_1_start-trial_start_time])  
    writerlog.writerow(["Trial " + str(trial+1) + " ISI onset", onset_of_ISI, onset_of_ISI - triggertime, onset_of_ISI-trial_start_time]) 
 
    writerlog.writerow(["Trial " + str(trial+1) + " Temp rec 2 ends", temp_rec_2_end, temp_rec_2_end - triggertime, temp_rec_2_end-trial_start_time])    
    if catchTrial:
        writerlog.writerow(["Trial " + str(trial+1) + " CatchTrial", start_catch_trial, start_catch_trial-triggertime, start_catch_trial - trial_start_time]) 
        writerlog.writerow(["Trial " + str(trial+1) + " Response end", RTend, RTend-triggertime, RTend - trial_start_time]) 
                
    writerlog.writerow(["Trial " + str(trial+1) + " END", trial_end_time, trial_end_time - triggertime, trial_end_time - trial_start_time])
    print("write csv elapsed" + str(core.getTime() - write_csv_start))
    
    writer.writerow([trial+1, stimulus[1], stimulus[2], myPainControlIntensity, catchTrial, side_of_cue[0], keypress[0], response, RT]) # data file column headers

    
    datafilewrite.flush() #force write to file, so we don't wait for file.close(). In case script crashes
    logfilewrite.flush()
    if Logging_to_file:
        logoutput.flush()
    print("")
    
    



        
    


#    
    
    
    
    keypress = event.getKeys(keyList=['space', 'escape']) #listen for escape
    if keypress:
        if keypress[0] == "escape":
            QuitExperiment()
    #core.wait(1.0)


#### Present 1 final ISI ###


#calculate how much time is left after stimulation. Trial should be 10s with 9s ISI
onset_of_ISI = core.getTime()
print("Onset of Final ISI X s after trial start:   " + str(onset_of_ISI - trial_start_time))
#print("Onset of ISI X s after trial start:   " + str(onset_of_ISI - (triggertime + (trial+1) * 10 + ISI_time)))
# remember total_trial_len already includes the current trial's requested ISI (so total_trial_len is different on each trial)

totalISIelapsedsofar = 0
for i in range(trial+1): #last i is ((trial + 1) - 1) so for 96 trials, last trial is trial 95 in python, so last i = 95 here (95+1-1). We add up everything until and including the last trial
    totalISIelapsedsofar = totalISIelapsedsofar + float(ISI_vector[i]) #just add everything up so far

# formula = length - delay
# delay = time_now - time_it_should_be
#time_it_should_be = trigger + 2 x NTrials + totalISIs + FirstISI + NSchluck
# putting it all together = length - (time_now - (trigger + 2 x NTrials + totalISIs + FirstISI + NSchluck))
print("ISI should be " + str(first_or_last_ISI - (onset_of_ISI - (triggertime + (cue_dur + stim_dur_main_expt) * (trial+1) + totalISIelapsedsofar + first_or_last_ISI + Schluckpause_len * nSchluck))) + " s long...")

if eyetrack_mode:
    tk.sendMessage("After final ISI onset")
    
writerlog.writerow(["FINAL ISI start", onset_of_ISI, onset_of_ISI - triggertime, onset_of_ISI - trial_start_time])    
    
print("First/Last ISI: " + str(first_or_last_ISI))
print("Onset of ISI: " + str(onset_of_ISI))
print("Trigger time: " + str(triggertime))
print("Cue + Stim: " + str(cue_dur + stim_dur_main_expt))
print("Trial: " + str(trial+1))
print("totalISIelapsedsofar " + str(totalISIelapsedsofar) )
print("Schluck: " + str(Schluckpause_len * nSchluck))


remainingISI = first_or_last_ISI - (onset_of_ISI - (triggertime + (cue_dur + stim_dur_main_expt) * (trial+1) + totalISIelapsedsofar + first_or_last_ISI + Schluckpause_len * nSchluck))    

#display ISI
while (core.getTime() - onset_of_ISI) < remainingISI:
    myFunctions.showFix(win, "+", (1, 1, 1))
    win.flip()
    if dual_screen:
        myFunctions.showDebugText(winexp, currtrialstring, (0, 220),whichComputer)
        #myFunctions.showDebugText(winexp, "Stimulus: " + str(stimulus[1]),  (0, -200),whichComputer) 
        #myFunctions.showDebugText(winexp,("Temp" + debugText1),debugTextPos1,whichComputer)
        myFunctions.showFix(winexp, "ISI", (1, 1, 1))
        winexp.flip()
        
end_of_ISI = core.getTime()
if eyetrack_mode:
    tk.sendMessage("After final ISI offset")
    
writerlog.writerow(["FINAL ISI end", end_of_ISI, end_of_ISI - triggertime, end_of_ISI - trial_start_time])    


# show goodbye screen
the_end = core.getTime()
print("End: " + str(the_end - triggertime) + " after trigger")
myFunctions.showText(win, u"Danke für die Teilnahme", (1, 1, 1))
if dual_screen:
    myFunctions.showText(winexp, u"Danke für die Teilnahme", (1, 1, 1))
    winexp.flip()
win.flip()


if eyetrack_mode:
    tk.sendMessage("End")
writerlog.writerow(["End of block", the_end, the_end-triggertime])     
core.wait(1.000)




    
QuitExperiment()    