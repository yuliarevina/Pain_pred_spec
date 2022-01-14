#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 18:19:32 2021

@author: Yulia Revina
"""

from psychopy import core, clock, visual, event, monitors
import pandas as pd
import time, numpy
import matplotlib.pyplot as plt # for plotting the results
#import QSTControl_python3 as QC
import TcsControl_python3 as QST
## Initialize thermode
# create thermode object
#thermode = QC.QSTDevice()
thermode_left = QST.TcsDevice(port='/dev/ttyACM0') #create thermode obj on the first port for stimulating LEFT arm
thermode_right = QST.TcsDevice(port='/dev/ttyACM1') #create thermode obj on the second port for stimulating RIGHT arm
thermode_left.set_filter('low')
thermode_right.set_filter('low')



def Burn_left(temps, durs, rampspeeds, returnspeeds):
    #code borrowed from Ulrike Horn
    
    # settings
    baselineTemp = 31.0 # baseline/neutral temperature (for all 5 zones equally)
    #durations = [1]*5 # stimulation durations in s for the 5 zones
    #ramp_speed = [100]*5 # ramp up speed in °C/s for the 5 zones
    #return_speed = [100]*5 # ramp down speed in °C/s for the 5 zones
    #temperatures = [47]*5 # target temperatures in °C for the 5 zones
    durations = durs # stimulation durations in s for the 5 zones
    ramp_speed = rampspeeds # ramp up speed in °C/s for the 5 zones
    return_speed = returnspeeds # ramp down speed in °C/s for the 5 zones
    temperatures = temps # target temperatures in °C for the 5 zones
   

    # Quiet mode
    thermode_left.set_quiet()
    
    # send all settings for the stimuli
    thermode_left.set_baseline(baselineTemp)
    thermode_left.set_durations(durations)
    thermode_left.set_ramp_speed(ramp_speed)
    thermode_left.set_return_speed(return_speed)
    thermode_left.set_temperatures(temperatures)
    
    # start stimulation
    thermode_left.stimulate()   
    
#    # record stimulation temperatures
#    recordDuration = 6.0;
#    cpt = 0
#    start_time = time.time()
#    column_names = ["temp_1", "temp_2", "temp_3", "temp_4", "temp_5"]
#    df = pd.DataFrame(columns = column_names)
#    while True:
#        current_temperatures = thermode.get_temperatures()
#        data = pd.DataFrame([current_temperatures], columns=column_names)
#        df = df.append(data)
#        current_time = time.time()
#        cpt = cpt + 1;
#        elapsed_time = current_time - start_time
#        if elapsed_time > recordDuration:
#            print("Finished iterating in: " + str(int(elapsed_time))  + " seconds")
#            break

#    # plot it
#    plt.xlabel('time in samples')
#    plt.ylabel('temperature')
#    plt.plot(range(len(df)), df['temp_1'])
#    plt.plot(range(len(df)), df['temp_2'])
#    plt.plot(range(len(df)), df['temp_3'])
#    plt.plot(range(len(df)), df['temp_4'])
#    plt.plot(range(len(df)), df['temp_5'])
#    plt.show()

    # close connection
    #thermode.close()
    
    
    
#message = visual.TextStim(win, text='Hello World'
#font='Adler', pos=(0.0, 0.0), 
#depth=0, rgb=None, color=(1.0, 0.0, 0.0),
#colorSpace='rgb',
#opacity=1.0, contrast=1.0, units='', ori=45.0, height=0.5, 
#antialias=True, bold=False, italic=False, 
#alignText='center', anchorHoriz='center', 
#anchorVert='center', fontFiles=(), wrapWidth=None, flipHoriz=False,
#flipVert=False, languageStyle='LTR', name=None, autoLog=None)
    
    
    
    
def Burn_right(temps, durs, rampspeeds, returnspeeds):
    #code borrowed from Ulrike Horn
    
    # settings
    baselineTemp = 31.0 # baseline/neutral temperature (for all 5 zones equally)
    #durations = [1]*5 # stimulation durations in s for the 5 zones
    #ramp_speed = [100]*5 # ramp up speed in °C/s for the 5 zones
    #return_speed = [100]*5 # ramp down speed in °C/s for the 5 zones
    #temperatures = [47]*5 # target temperatures in °C for the 5 zones
    durations = durs # stimulation durations in s for the 5 zones
    ramp_speed = rampspeeds # ramp up speed in °C/s for the 5 zones
    return_speed = returnspeeds # ramp down speed in °C/s for the 5 zones
    temperatures = temps # target temperatures in °C for the 5 zones
   

    # Quiet mode
    thermode_right.set_quiet()
    
    # send all settings for the stimuli
    thermode_right.set_baseline(baselineTemp)
    thermode_right.set_durations(durations)
    thermode_right.set_ramp_speed(ramp_speed)
    thermode_right.set_return_speed(return_speed)
    thermode_right.set_temperatures(temperatures)
    
    # start stimulation
    thermode_right.stimulate()       


def SaveCalibrationTemp(temperatures_calibration, rating, writercalib, filenamesaveplot):
    # record temperatures and ratings in calibration data file
        for i in range(len(rating)):
            writercalib.writerow([temperatures_calibration[i], rating[i]]) # data calibration file column headers
        
        # need to convert to array otherwise the maths doesn't work
        x = numpy.array(temperatures_calibration)
        print (x)
        y = numpy.array(rating)
        print (y)
        x = x[~numpy.isnan(y)]
        y = y[~numpy.isnan(y)]
        arr1inds = x.argsort()
        x = x[arr1inds[::1]]
        y = y[arr1inds[::1]]
    
        m,b = numpy.polyfit(x, y, 1) 
    
        # calculate the temperatures x corresponding to ratings 30 and 75
        temp_30 = (30-b)/m
        temp_75 = (75-b)/m
        temp_50 = (50-b)/m
        temp_80 = (80-b)/m
        print(temp_30)
        print(temp_75)
        print(temp_50)
        print(temp_80)
        
        # add temp_30, 50 and 75 to file
        writercalib.writerow(["Temp 30", temp_30]) 
        writercalib.writerow(["Temp 50", temp_50]) 
        writercalib.writerow(["Temp 75", temp_75]) 
        writercalib.writerow(["Temp 80", temp_80]) 
        
        # generate a range of temperatures to use in main expt
        temperatures_calibrated = numpy.linspace(temp_50, temp_80, 5) # we want 5 numbers for the psychometric function
        writercalib.writerow(["Stim 1", temperatures_calibrated[0]]) 
        writercalib.writerow(["Stim 2", temperatures_calibrated[1]]) 
        writercalib.writerow(["Stim 3", temperatures_calibrated[2]]) 
        writercalib.writerow(["Stim 4", temperatures_calibrated[3]]) 
        writercalib.writerow(["Stim 5", temperatures_calibrated[4]]) 
        print(temperatures_calibrated)
    
        # plot it
        plt.figure()
        plt.xlabel('temperature')
        plt.ylabel('ratings')
        plt.title((temp_30, temp_80))
        plt.plot(x, y, 'yo', x, m*x+b, '--b',temp_30,30,'bo',temp_80,80,'bo') 
        plt.axis([41.5, 58.0, 0, 100])

        plt.savefig(filenamesaveplot+'.png',dpi=80,transparent=True)
        
        
        
        return temperatures_calibrated, temp_30, temp_50, temp_75, temp_80
    
    
def RecordTemperature():
         [left_curr_temps, datatempleft] = thermode_left.get_temperatures()
         [right_curr_temps, datatempright] = thermode_right.get_temperatures()
         return left_curr_temps, right_curr_temps, datatempleft, datatempright