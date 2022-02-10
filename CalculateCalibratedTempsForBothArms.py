#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 18:25:29 2022

@author: user
"""

from tkinter import *
from tkinter import ttk
import numpy

root = Tk()
root.title("Calibrated temperatures for both arms")

def calculate(*args):
    try:
        value_left50 = float(left50.get())
        value_left80 = float(left80.get())
        value_right50 = float(right50.get())
        value_right80 = float(right80.get())
        myList = numpy.ndarray.tolist(numpy.linspace((value_left50 + value_right50)/2, (value_left80 + value_right80)/2, 5))
        print(myList)
        outStr = "["+",".join(str(round(element,1)) for element in myList) + "]"
        totalval = outStr
        total.set(totalval)
        print(totalval)
        #right80.set("Hello")
    except ValueError:
        pass

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


left50 = StringVar()
left50_entry = ttk.Entry(mainframe, width=7, textvariable=left50)
left50_entry.grid(column=1, row=1, sticky=(W, E))

left80 = StringVar()
left80_entry = ttk.Entry(mainframe, width=7, textvariable=left80)
left80_entry.grid(column=1, row=2, sticky=(W, E))

right50 = StringVar()
right50_entry = ttk.Entry(mainframe, width=7, textvariable=right50)
right50_entry.grid(column=3, row=1, sticky=(W, E))

right80 = StringVar()
right80_entry = ttk.Entry(mainframe, width=7, textvariable=right80)
right80_entry.grid(column=3, row=2  , sticky=(W, E))


total = StringVar()
ttk.Entry(mainframe, width=20, textvariable=total).grid(column=2, row=5, sticky=(W, E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=5, sticky=W)

ttk.Label(mainframe, text="left50").grid(column=2, row=1, sticky=W)
ttk.Label(mainframe, text="left80").grid(column=2, row=2, sticky=W)
ttk.Label(mainframe, text="right50").grid(column=4, row=1, sticky=W)
ttk.Label(mainframe, text="right80").grid(column=4, row=2, sticky=W)
ttk.Label(mainframe, text="Total").grid(column=1, row=5, sticky=W)
#ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)


for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)
#left50_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()