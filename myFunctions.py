#!/usr/bin/env python2
# -*- coding: utf-8 -*-



from psychopy import core, clock, visual, event, monitors, data
import pandas as pd
import time, numpy, os, sys, random
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
        
        
def PracticeSession(thermodeYN, win, winexp, arm, side, parallel_port_mode, bbox):
        
    
    showText(win, "Practice Trial", (1, 1, 1))
    showText(winexp, "Practice Trial", (1, 1, 1))
    win.flip()
    winexp.flip()
    if side[0] == 0:
        practicetemperature = [45, 45, 31, 31, 31]
    else:
        practicetemperature = [31, 31, 31, 45, 45]
        
    if thermodeYN: 
          import QST_functions
          if arm[0] == 0: #left
              
              QST_functions.Burn_left(practicetemperature, [1]*5, [100]*5, [100]*5)
          else:  #right
              QST_functions.Burn_right(practicetemperature, [1]*5, [100]*5, [100]*5)
              
    core.wait(2.0)           
    showText(win, u"Welcher Reiz war wärmer?", (1, 1, 1))
    showText(winexp, u"Welcher Reiz war wärmer?", (1, 1, 1))
    win.flip() 
    winexp.flip()
    submittedanswer = False
    while not submittedanswer:
        [submittedanswer, keypress, keypresskeyboard] = RecordAnswer(parallel_port_mode, bbox)
    if (side[0] == 0 and keypress[0] == "left") or (side[0] == 1 and keypress[0] == "right"):
        #correct
        showText(win, "Richtig! :)", (1, 1, 1))
        showText(winexp, "Richtig! :)", (1, 1, 1))
        win.flip()
        winexp.flip()
    else:
        #incorrect
        showText(win, "Leider nicht richtig! :(", (1, 1, 1))
        showText(winexp, "Leider nicht richtig! :(", (1, 1, 1))
        win.flip()
        winexp.flip()
        
    
    
def RecordAnswer(parallel_port_mode, bbox):
    submittedanswer = False
    #keypress = []
    
    if parallel_port_mode:
#        bbox.reset()
#        core.wait(0.3)
        keypress = bbox.getButtons(timeStamped=False)
        keypresskeyboard = event.getKeys(keyList=['left', 'right', 'escape', 'return']) #wait for Left Arrow or Right Arrow key
        
    else:
        keypress = event.getKeys(keyList=['left', 'right', 'escape']) #wait for Left Arrow or Right Arrow key
        keypresskeyboard = event.getKeys(keyList=['left', 'right', 'escape']) #wait for Left Arrow or Right Arrow key
        #submittedanswer = True
    
    if keypress:
        # participant can use both L and R response pads to give answer
        # L button of each one is LEFT
        # R button of each one is RIGHT
        # People report it is easier to use L response pad when stim appears on the left
        # and R response pad when stimulus appears on the right
        if parallel_port_mode == True:
            if keypress[0] == 0:
                keypress[0] = "left" #recode to words
                submittedanswer = True
                print("key 0 detected")
                print(str(keypress[0]))
            elif keypress[0] == 1:
                keypress[0] = "right" #recode to words
                submittedanswer = True
                print("key 1 detected")
                print(str(keypress[0]))
            elif keypress[0] == 2:
                keypress[0] = "left" #recode to words
                submittedanswer = True
                print("key 2 detected")
                print(str(keypress[0]))
            elif keypress[0] == 3:    
                keypress[0] = "right" #recode to words
                submittedanswer = True
                print("key 3 detected")
                print(str(keypress[0]))
            else:
                print('Button Box: Do you use the correct button box / keys?')
                print("key ? detected")
                print(str(keypress[0]))
        else:
            if keypress[0] == 'left':
                submittedanswer = True
            elif keypress[0]  == 'right':
                submittedanswer = True
            elif keypress[0] == 'escape':
                #QuitExperiment()
                pass
            elif keypress[0] == 'return':
                pass
            else:
                print('Do you use the correct button box / keys?')
                print('Keyboard: Do you use the correct button box / keys?')
    else:
        keypress = ["NaN"]
    print("the function returned the following key")
    print(str(keypress))            
    return submittedanswer, keypress , keypresskeyboard           
           
        
        
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


def RatingExpectation(win, winexp, scnWidth, scnHeight, parallel_port_mode, bbox, ratingofExpectation):
     question = []
     question.append(u"Wie häufig hatten Sie das Gefühl,\ndass das Bild den korrekten Arm vorhergesagt hat?")
     question.append(u"Nachdem ich das Bild in jedem Durchgang gesehen habe,\nwartete ich auf den Schmerz auf dem vorhergesagten Arm")
     labels = []
     labels.append([u'Nie', u'Immer'])
     labels.append([u'Stimme überhaupt nicht zu', u'Stimme komplett zu'])
    
     for i in range(2):
         # generate text and rating scale objects     
         textObjExp = visual.TextStim(win=winexp, text="", color="black", height = 20, units="pix")
         textObjSub = visual.TextStim(win=win, text="", color="black", height = 40, units="pix")
         dotObj = visual.Circle(win=win, fillColor="white", lineColor="white",radius=[12,12],units="pix")
         ratingExpectation = visual.RatingScale(win = win, low = 0, high = 100, markerStart = 50, textSize=0.75,
         marker = 'triangle', stretch = 1.5, tickHeight = 1.5, tickMarks = [0,100],textColor='black',lineColor='black',
         labels = labels[i],
         showAccept = False)
         ratingExpectationExp = visual.RatingScale(win = winexp, low = 0, high = 100, markerStart = 50, textSize=0.75,
         marker = 'triangle', stretch = 1.5, tickHeight = 1.5, tickMarks = [0,100],textColor='black',lineColor='black',
         labels = labels[i],
         showAccept = False)
         
         submittedanswer = False
         ratingExpectation.reset()
         ratingExpectationExp.reset()
         currentPos = 50
         textObjSub.setText(question[i])
         textObjExp.setText(question[i])
               
         ExpectationRatingTimer = core.CountdownTimer(15)
         ExpectationRatingTimer.reset()
                    
         # ********************** for when we want to remove self-paced *************
         while ExpectationRatingTimer.getTime() > 0:
             if not submittedanswer:
                 ratingExpectation.markerPlacedAt = currentPos
                 ratingExpectation.draw()
                 textObjSub.draw()
                        
                 ratingExpectationExp.markerPlacedAt = currentPos
                 ratingExpectationExp.draw()
                        
                 win.flip()
                 winexp.flip()
                     
                 if parallel_port_mode:
                     bbox.reset()
                     keypress = bbox.getButtons(timeStamped=False)
                     keypresskeyboard = event.getKeys(keyList=['left', 'right', 'escape', 'return', 'r']) #wait for Left Arrow or Right Arrow key
                     if keypresskeyboard:
                         if keypresskeyboard[0] == "escape":
                             #QuitExperiment()
                             pass
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
                                 #quitRoutine()
                                 pass
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
                            
                     ratingExpectation.markerPlacedAt = currentPos
                     ratingExpectation.draw()
                     textObjSub.draw()
                     ratingExpectationExp.markerPlacedAt = currentPos
                     ratingExpectationExp.draw()
                     win.flip()
                     winexp.flip()
                             #core.wait(0.01)  
         ratingofExpectation.append(ratingExpectation.getRating())
         print(ratingofExpectation)
                    
         winexp.flip()
         win.flip()
     
     return(ratingofExpectation)
     
     
     
def shufflelist(inputlist):
    complete = 0
    while complete == 0:
        stimuli = inputlist.copy()
        #print('Stimuli ' + str(stimuli))
        shuffled = []
        #print('Shuffled ' + str(shuffled))
        


        for i in range(len(stimuli) ):
        #print('Iteration ' + str(i))
        #print('len shuff ' + str(len(shuffled)))
        #print('Shuffled more than 1 element? ' + str((len(shuffled) > 1)))
        
        # if shuffled contains more than 1 element
        
        
            finalels = [x[-1] for x in stimuli]
            #finalels = [x[-1] for x in stimuli]
            finalels = [x[2] for x in stimuli]
            
            
            if len(shuffled) > 1:
                #print('Shuffled ' + str(shuffled))
                #print('Shuffled last 2 ' + str(shuffled[-2:]))
               
                #print('Stimuli ' + str(stimuli))
                #print('Shuff last 2 + stims ' + str(shuffled[-2:] + stimuli))
                
                #if last 2 elements of shuffled and the remaining elements of stimuli are the
                # same, break out of For loop and reset to the 1st while loop
                if len(set([shuffled[-2][-1], shuffled[-1][-1]] + finalels)) == 1:
                    break
            test = 0 #will act as a marker to make sure we don't pop a repeated value
            print(i)
                #if len(set([shuffled[-2][-1], shuffled[-1][-1]] + finalels)) == 1:
                if len(set([shuffled[-2][2], shuffled[-1][2]] + finalels)) == 1:    
                    break
            test = 0 #will act as a marker to make sure we don't pop a repeated value
            #print(i)
           
            savelist = stimuli.copy()
            #print('Savelist')
            #print(savelist)
            while test == 0:
                randomnumber = random.randint(0, len(stimuli) - 1)
                #print('randomnumber')
                #print(randomnumber)
                possible = stimuli.pop(randomnumber)
                #print('Possible')
                #print(possible)
                
                #if we popped a value that is already double repeated, return list back to unpopped state
                if len(shuffled) > 1:
                    #print([shuffled[-2][-1], shuffled[-1][-1]] )
                    #print([possible[-1]]*2)
                    #print([shuffled[-2][-1], shuffled[-1][-1]] == [possible[-1]]*2)
                    if [shuffled[-2][-1], shuffled[-1][-1]] == [possible[-1]]*2: #possible x repnum for var repeat
                    #if [shuffled[-2][-1], shuffled[-1][-1]] == [possible[-1]]*2: #possible x repnum for var repeat
                    if [shuffled[-2][2], shuffled[-1][2]] == [possible[-1]]*2: #possible x repnum for var repeat
                        stimuli = savelist.copy()
                        #print('Already repeated, reset list')
                        #print('Stimuli')
                        #print(stimuli)
                    # else accept the new value and set test to 1    
                    else:
                        #print('All good, append')
                        shuffled.append(possible)
                        test = 1
                else:
                    #print('All good, append')
                    shuffled.append(possible)
                    test = 1 #just set test to 1 and start a new iteration if only 1 number was in shuffled so far (so no duplicates to worry about)
            print(' ')        
            #print(' ')        
    # if length of stimuli is 0 then we finished going through the list and didn't break out of for loop
        if len(stimuli) == 0: #if last 1
            #shuffled.append(stimuli[0])
            complete = 1
    print(shuffled)
    return shuffled