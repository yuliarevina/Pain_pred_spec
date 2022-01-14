#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=== Authors ===
Dr. Ulrike Horn: uhorn@cbs.mpg.de
Max Planck Institute for Human Cognitive and Neuroscience
Research group Pain Perception
Date: 26th May 2021
"""

import serial
import numpy as np

class TcsDevice:
    def __init__(self, port='/dev/ttyACM0'):
        # some initial parameters
        self.baseline = 30.0
        # Open serial port
        self.s_port = serial.Serial(port, 115200, timeout = 2)
        self.s_port.flushInput();
        self.s_port.write(bytes(b'H'))
        #dispTCScommands = self.s_port.read(60)
        #print(dispTCScommands)
        self.s_port.flushOutput()
        firmware_msg = self.s_port.read(30)
        print(firmware_msg)
        self.s_port.flushInput()
        id_msg = self.s_port.read(30)
        print(id_msg)
        self.s_port.flushInput()
        # read the rest
        rest = self.s_port.read(10000)
        self.s_port.flushInput()
        #print(rest)
        
        self.s_port.write(bytes(b'B'))
        self.s_port.flushOutput()
        battery = self.s_port.read(14)
        print(battery)

    def set_quiet(self):
        """
        sets thermode to quiet mode
        otherwise TCS sends regularly temperature data
        (@1Hz if no stimulation, @100Hz during stimulation)
        and that can corrupt dialog between PC and TCS
        """
        self.s_port.write(bytes(b'F'))
        self.s_port.flushOutput()
    
    
    def set_filter(self, level):
        if level=='high':
            command = b'Of3'
        elif level=='medium':
            command = b'Of2'
        elif level=='low':
            command = b'Of1'
        else:
            print('Enter a valid filter strength (high, medium, low)')
            return
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    
    def set_baseline(self, baselineTemp):
        """
        sets baseline temperature in °C (also called neutral temperature)
        :param baselineTemp: 1 float value (min 20°C, max 40°C)
        """
        if baselineTemp > 40:
            baselineTemp = 40
        if baselineTemp < 20:
            baselineTemp = 20   
        command = b'N%03d' % (baselineTemp*10)
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    
    
    def set_durations(self, stimDurations):
        """
        sets stimulus durations in s for all 5 zones
        :param stimDurations: array of 5 values (min 0.001s, max 99.999s)
        """
        for i in range(5):
            if stimDurations[i] > 99.999:
                stimDurations[i] = 99.999
            if stimDurations[i] < 0.001:
                stimDurations[i] = 0.001
        # check if speeds are equal
        if stimDurations.count(stimDurations[0]) == len(stimDurations):
            # yes: send all speeds in one command
            command = b'D0%05d' % (stimDurations[1]*1000)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:       
            # no: send speeds in separate commands
            for i in range(5):
                command = b'D%d%05d' % ((i+1) , (stimDurations[i]*1000))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    
    def set_ramp_speed(self, rampSpeeds):
        """
        sets ramp up speeds in °C/s for all 5 zones
        :param rampSpeeds: array of 5 values (min 0.1°C/s, max 300°C/s)
        """
        for i in range(5):
            if rampSpeeds[i] > 300:
                rampSpeeds[i] = 300
            if rampSpeeds[i] < 0.1:
                rampSpeeds[i] = 0.1
        
        # check if speeds are equal
        if rampSpeeds.count(rampSpeeds[0]) == len(rampSpeeds):
            # yes: send all speeds in one command
            command = b'V0%04d' % (rampSpeeds[1]*10)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:        
            # no: send speeds in separate commands
            for i in range(5):
                command = b'V%d%04d' % ((i+1), (rampSpeeds[i]*10))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    def set_return_speed(self, returnSpeeds):
        """
        sets ramp down/ return speeds in °C/s for all 5 zones
        :param returnSpeeds: array of 5 values (min 0.1°C/s, max 300°C/s)
        """
        for i in range(5):
            if returnSpeeds[i] > 300:
                returnSpeeds[i] = 300
            if returnSpeeds[i] < 0.1:
                returnSpeeds[i] = 0.1
        
        # check if speeds are equal
        if returnSpeeds.count(returnSpeeds[0]) == len(returnSpeeds):
            # yes: send all speeds in one command
            command = b'R0%04d' % (returnSpeeds[1]*10)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:        
            # no: send speeds in separate commands
            for i in range(5):
                command = b'R%d%04d' % ((i+1), (returnSpeeds[i]*10))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    
    def set_temperatures(self, temperatures):
        """
        sets target temperatures in °C for all 5 zones
        :param temperatures: array of 5 values (min 0.1°C, max 60°C)
        """
        for i in range(5):
            if temperatures[i] > 60:
                temperatures[i] = 60
            if temperatures[i] < 0.1:
                temperatures[i] = 0.1
        
        # check if temperatures are equal
        if temperatures.count(temperatures[0]) == len(temperatures):
            # yes: send all speeds in one command
            command = b'C0%03d' % (temperatures[1]*10)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:        
            # no: send speeds in separate commands
            for i in range(5):
                command = b'C%d%03d' % ((i+1), (temperatures[i]*10))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    
    def stimulate(self):
        """
        starts the stimulation protocol with the parameters that have been set
        """
        self.s_port.write(bytes(b'L'))
    
    
    
    def get_temperatures(self):
        """
        get current temperatures of zone 1 to 5 in °C
        :return: returns an array of five temperatures or empty array if 
            there is an error
        """
        self.s_port.flushInput()
        self.s_port.write(bytes(b'E'))
        self.s_port.flushOutput()
        # '/r' + 'xxx?xxx?xxx?xxx?xxx?xxx' with '?' = sign '+' ou '-'
        # neutral + t1 to t5
        datatemps = self.s_port.read(24)
        #print("Raw Datatemps")
        #print(type(datatemps))
        #print(len(datatemps))
        #print(datatemps)
        #print(datatemps[0:1])
        #print(datatemps[2:4])
        #print(datatemps[5:8])
        #print(datatemps[9:12])
        #print(datatemps[13:16])
        #print(datatemps[17:20])
        #print(datatemps[21:24])
        #print("End")
        temperatures = [0, 0, 0, 0, 0]
        if len(datatemps) > 23:
            neutral = float(datatemps[2:4]);
            temperatures[0] = float(datatemps[5:8]) / 10;
            temperatures[1] = float(datatemps[9:12]) / 10;
            temperatures[2] = float(datatemps[13:16]) / 10;
            temperatures[3] = float(datatemps[17:20]) / 10;
            temperatures[4] = float(datatemps[21:24]) / 10;
        else:
            temperatures = []
        return temperatures, datatemps
    
    
    def enable_point_to_point(self, enabled_zones):
        """
        enable/disable point to point stimulation for each zone
        :param enabled_zones:   array of 5 integers to choose zones 
                                to be enabled (1) or disabled (0)
        """
        zonestr = ''.join(str(e) for e in enabled_zones)
        command = b'Ue'+zonestr.encode('UTF-8')
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    
    
    def set_point_to_point(self, zones, timevec, temperature):
        """
        set point to point stimulation curve
        :param zones: array of 5 '0' or '1' to choose zones to be set
        :param timevec: array of time in seconds (column vector with length n,
                                               first point 0)
        :param temperature: array of temperature in °C (column vector with 
                                                        same length n, 
                                                        first point neutral temp)
        """
        timevec = np.array(timevec)
        temperature = np.array(temperature)
        
        errormsg = ""
        # check parameters
        if np.shape(timevec) != np.shape(temperature):
            errormsg = "time and temperature arrays do not have the same length";
        if (np.ndim(timevec) != 1) or (np.ndim(temperature) != 1):
            errormsg = "time and temperature must be column vectors";
        if len(timevec) > 999:
            errormsg = "length of arrays must be < 1000"
        if timevec[0] != 0:
            errormsg = "time at point 0 must be equal to 0"
        if bool(errormsg):
            print("Set point to point stimulation error: {}".format(errormsg))
            return
        
        # round time to 10 ms
        timevec = np.round(timevec*100)/100
        
        # compute time intervals between points
        deg = np.array(temperature[1:])
        delta = timevec[1:] - timevec[0:-1] # time intervals in s
        
        # intervals must be less or equal to 9.99s (9990 ms)
        # so this loop generates intermediate points if necessary
        sup9990ms = True
        while sup9990ms:
            sup9990ms = False
            for i in range(len(delta)):
                if delta[i] > 9.99:
                    sup9990ms = True
                    if i==0:
                        # add point at beginning
                        delta = np.concatenate(([delta[0]/2.0], [delta[0]/2.0], delta[1:]))
                        deg = np.insert(deg, 0, (temperature[0] + deg[0])/2.0)
                    elif i==(len(delta)-1):
                        # add point at the end
                        delta = np.concatenate((delta[0:i], [delta[i]/2.0, delta[i]/2.0]))
                        deg = np.concatenate((deg[0:i], [(deg[i-1]+deg[i])/2.0], [deg[i]]))
                    else:
                        # add intermediate point
                        delta = np.concatenate((delta[0:i], [delta[i]/2.0, delta[i]/2.0], delta[i+1:]))
                        deg = np.concatenate((deg[0:i], [(deg[i-1]+deg[i])/2.0], deg[i:]))
                    break
        
        # send array of points to thermode
        combined_str = ''.join(str(e) for e in zones) + '%03d' % (len(delta))
        command = b'Uw' + combined_str.encode('UTF-8')
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
        
        for i in range(len(delta)):
            command = b'%03d%03d' % ((round(delta[i]*100)), (round(deg[i]*10)))
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
    
    
    def enable_zones(self, enabled_zones):
        """
        enable/disable each zone
        :param enabled_zones:   array of 5 integers to choose zones 
                                to be enabled (1) or disabled (0)
        """
        zonestr = ''.join(str(e) for e in enabled_zones)
        command = b'S'+zonestr.encode('UTF-8')
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    

    def close(self):
        self.s_port.close()
    
    
    