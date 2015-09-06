# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:34:31 2015

@author: artur
"""

# TODO wrap-up sending and receiving data protocols from Arduino here

import sys, serial, glob

# constants for dfinig the format of a data packet
INPUT_START_CHAR = '>'
INPUT_END_CHAR = ';'
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
    msg = INPUT_START_CHAR
    for key in keywords:
        msg += key + DATA_DELIMITER + keywords[key]
    msg += INPUT_END_CHAR
    serialConnection.write(msg)