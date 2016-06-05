# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 21:32:32 2015

@author: artur
"""

#import pygame
#pygame.init()
#nSticks = pygame.joystick.get_count()
#print nSticks

import pygame
from pygame.locals import *

# initialise pygame
pygame.init()

def getControllerCount():
    """ Return the number of available controllers """
    return pygame.joystick.get_count()

def refreshJoysticks():
    """ Needs to be called in order to re-establish connection with all available
    joysticks; unless this is called any new connections or disconnections will
    not be recognised. """
    pygame.joystick.quit()
    pygame.joystick.init()

def getControllerNames(refresh=True):
    """ Return the names of all the available controllers and joysticks.
    Optional arguments
    ------------------
        refresh - ask pygame to check for connections/disconnections since last update;
            safer to do so (default True) as otherwise a seg fault will occur in case
            one of the pads got disconnected
    """
    if refresh: refreshJoysticks()
    
    controllerNames = []
    for i in range(0, getControllerCount()):
        controllerNames.append( pygame.joystick.Joystick(i).get_name() )
    
    return controllerNames

class controller(object):
    """ Interfaces a USB xbox controller and maps its direct outputs into a 
    desired set of control variables"""
    
    # maps individual keys and axes to more recognisable names
    # note: there is only one hat (4-position circular selection thingy)
    axesMap = {
        0:'lhsStickXaxis',
        1:'lhsStickYaxis',
        3:'rhsStickXaxis',
        4:'rhsStickYaxis',
        2:'lhsTriggerAxis',
        5:'rhsTriggerAxis',
        }
    buttonsMap = {
        0:'butA',
        1:'butB',
        2:'butX',
        3:'butY',
        4:'lhsTriggerBut',
        5:'rhsTriggerBut',
        6:'lhsChoiceBut',
        7:'rshChoiceBut',
        8:'midChoiceBut',
        9:'lhsStickBut',
        10:'rhsStickBut',
        }
    
    def __init__(self):
        # index of this controller in the list of available ones
        # value -1 denotes an inactie connection
        self.controllerIndex = -1
        # pygame joystick object
        self.josyickObject = -1
        # name identifier
        self.name = 'None'
        
        # direct values of the controller outputs
        # map name of each button and controller axis to a dict of values
        # note: for sticks the x-direction +ve RIGHT, y-direction +ve DOWN
        # BUT for the hat (round 4-option select thingy) they are x +ve right and y +ve up
        self.axesValues = dict(zip(controller.axesMap.values(),
                                   [0 for i in range(len(controller.axesMap))]))
        self.buttonValues = dict(zip(controller.buttonsMap.values(),
                                   [False for i in range(len(controller.buttonsMap))]))
        self.hatX,self.hatY = 0,0
        
        # zero position of the triggers is at -1 (when they are not pressed)
        self.axesValues['lhsTriggerAxis'] = -1
        self.axesValues['rhsTriggerAxis'] = -1
    
    def setControllerIndex(self,newIndex):
        """ Change the controller index - there may be a few connected at any one time """
        self.controllerIndex = newIndex
        try:
            self.name = pygame.joystick.Joystick(newIndex).get_name()
            self.josyickObject = pygame.joystick.Joystick(newIndex)
            self.josyickObject.init()
            
        except pygame.error as e:
            # if can't connect then set the current connection status to off
            print e
            self.controllerIndex = -1
            self.name = 'None'
            self.josyickObject = -1
    
    def parseEvents(self):
        """ Key method which reads-in all the events from the controller and
        sets the internal field values accordingly.
        Should be called with a refresh rate sufficient to ensure smooth use as
        it will take all of the event available on the stack and parse them in one
        go, clearing the stack afterwards """

        # go over each pygame event
        for event in pygame.event.get():
            if event.type == JOYAXISMOTION:
                # check if this event relates to this controller, ignore if not
                if event.joy != self.controllerIndex: continue
                    
                axisName = controller.axesMap[event.axis]
                self.axesValues[axisName] = event.value
            
            elif event.type == JOYBUTTONDOWN:
                # do nothing when a button is pressed down
                pass
            
            elif event.type == JOYBUTTONUP:
                # flip the bool value when a button is released
                buttonName = controller.buttonsMap[event.button]
                self.buttonValues[buttonName] = not self.buttonValues[buttonName]

            elif event.type == JOYHATMOTION:
                self.hatX = event.value[0]
                self.hatY = event.value[1]

def main():
    "Opens a window and prints events to the terminal. Closes on ESC or QUIT."
    pygame.init()
#    screen = pygame.display.set_mode((640, 480))
#    pygame.display.set_caption("JOYTEST")
    clock = pygame.time.Clock()
    
    joysticks = []
    for i in range(0, pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))
            joysticks[-1].init()
            print "Detected joystick '",joysticks[-1].get_name(),"'"
    while 1:
            clock.tick(60)
            for event in pygame.event.get():
                    if event.type == QUIT:
                            print "Received event 'Quit', exiting."
                            return
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                            print "Escape key pressed, exiting."
                            return
                    elif event.type == KEYDOWN:
                            print "Keydown,",event.key
                    elif event.type == KEYUP:
                            print "Keyup,",event.key
                    elif event.type == MOUSEMOTION:
                            print "Mouse movement detected."
                    elif event.type == MOUSEBUTTONDOWN:
                            print "Mouse button",event.button,"down at",pygame.mouse.get_pos()
                    elif event.type == MOUSEBUTTONUP:
                            print "Mouse button",event.button,"up at",pygame.mouse.get_pos()
                            
                    elif event.type == JOYAXISMOTION:
                            print "Joystick '",joysticks[event.joy].get_name(),"' axis",event.axis,"motion."
                            if event.axis == 2:
                                    print ' axis 2', event.value
                            elif event.axis == 5:
                                    print ' axis 5', event.value
                    elif event.type == JOYBUTTONDOWN:
                            print ("Joystick '",joysticks[event.joy].get_name(),
                                "' button",event.button,"down.")
                    elif event.type == JOYBUTTONUP:
                            print "Joystick '",joysticks[event.joy].get_name(),"' button",event.button,"up."
                    elif event.type == JOYHATMOTION:
                            print "Joystick '",joysticks[event.joy].get_name(),"' hat",event.hat," moved to",event.value



if __name__ == "__main__":
    cont = controller()
    cont.setControllerIndex(0)
    cont.parseEvents()
    main()
