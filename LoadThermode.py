#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 18:10:34 2022

@author: user
"""

import sys
from psychopy import core, clock, data, visual, event, gui, monitors, logging #parallel


sys.path.insert(1, '/NOBACKUP2/Controlling_QST/')
sys.path.insert(1, '/NOBACKUP2/Pred_spec/Ulrike_functions/')
directory="//NOBACKUP2//Pred_spec//"
import QST_functions


core.wait(5.0)
QST_functions.Burn_left([45, 25, 31, 25, 45], [1]*5, [100]*5, [100]*5)
core.wait(5.0)
QST_functions.Burn_left([26, 46, 31, 46, 26], [1]*5, [100]*5, [100]*5)
core.wait(5.0)
QST_functions.Burn_right([45, 25, 31, 25, 45], [1]*5, [100]*5, [100]*5)
core.wait(5.0)
QST_functions.Burn_right([26, 46, 31, 46, 26], [1]*5, [100]*5, [100]*5)
core.wait(5.0)
    
