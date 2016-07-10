# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:34:31 2015

@author: artur
"""

# TODO wrap-up sending and receiving data protocols from Arduino here

#TODO hold serial connection to the Arduino here

import sys, serial, glob

# constants for dfinig the format of a data packet
OUTPUT_START_CHAR = '>'
INPUT_START_CHAR = '<'
MESSAGE_END_CHAR = ';'
DATA_DELIMITER = ','

def getActivePorts():
    """ find the open ports - main part of the code from:
    http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    """
    if sys.platform.startswith('win'):
        candidatePorts = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        candidatePorts = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        candidatePorts = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    ports = []
    for port in candidatePorts:
        try:
            s = serial.Serial(port)
            s.close()
            ports.append(port)
        except (OSError, serial.SerialException):
            pass
    
    return ports
    
def sendMessage(serialConnection,keywords):
    """ Send a message to the given serial connection 
    Arguments
    ---------
        @param serialConnection - serial port
        @param keywords - dictionary of values and their descriptors to be sent
    """
    msg = OUTPUT_START_CHAR
    for key in keywords:
        msg += '{}{}{}{}'.format(key, DATA_DELIMITER, keywords[key], DATA_DELIMITER)
    msg = msg.rstrip(DATA_DELIMITER) + MESSAGE_END_CHAR # oerwrite the last date delimiter with end char
#    print msg
    serialConnection.write(msg)

def readMessage(s):
    """ Decode an input string into a set of keywords and values
    Arguments
    ---------
        @param s - string representation of an input message
    """
    try:
        if s:
            s = s.strip()
            if s[0] == INPUT_START_CHAR and s[-1] == MESSAGE_END_CHAR:
                # split into values and keys
                s = s.lstrip(INPUT_START_CHAR).rstrip(MESSAGE_END_CHAR).split(DATA_DELIMITER)
    
                readings = {}
                try:
                    # concentrate into a dictionary
                    for iKey in range(0,len(s),2):
                        readings[s[iKey]] = s[iKey+1]
                except IndexError:
                    pass
                return readings
    except:
        pass
    return {}