#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 15:44:21 2022

@author: user
"""
import pylink, time
tk = pylink.EyeLink('100.1.1.1')
edf_running_name = 'data.EDF'
filenameeyetrack = "eye_" + time.strftime('%Y-%m-%dT%H.%M.%S') + ".edf"
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
