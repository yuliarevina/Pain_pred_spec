#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 11:36:53 2023

@author: user
"""


import sys
from psychopy import core, clock, data, visual, event, gui, monitors, logging #parallel


sys.path.insert(1, '/NOBACKUP2/Controlling_QST/')
sys.path.insert(1, '/NOBACKUP2/Pred_spec/Ulrike_functions/')
sys.path.append('/data/pt_02650/fMRI/Experiment_scripts/')
directory="/data/pt_02650/fMRI/Experiment_scripts/"
import QST_functions

mytemp = 54.9


core.wait(5.0)
QST_functions.Burn_left([mytemp]*5, [1]*5, [100]*5, [100]*5)
core.wait(5.0)
QST_functions.Burn_left([mytemp]*5, [1]*5, [100]*5, [100]*5)
core.wait(5.0)
QST_functions.Burn_right([mytemp]*5, [1]*5, [100]*5, [100]*5)
core.wait(5.0)
QST_functions.Burn_right([mytemp]*5, [1]*5, [100]*5, [100]*5)
core.wait(5.0)
    