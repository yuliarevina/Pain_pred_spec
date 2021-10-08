#!/usr/bin/env python2
# -*- coding: utf-8 -*-



from psychopy import core, clock, visual, event, monitors
import pandas as pd
import time, numpy
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
        height=50, alignHoriz="center", 
        alignVert="center")
        message.draw()
        
        
        
        
