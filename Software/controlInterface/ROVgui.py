#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:34:31 2015

@author: Artur, Alek
"""

import ROVguiBaseClasses
import throttleDial
import communicationProtocol
import controllerInterface

import wx, string
from wx.lib import statbmp
import cv2
import os
import serial
import numpy as np
import datetime, multiprocessing
from scipy import interpolate

CONTROLLER_NAME_CHUNK_LENGTH=20 # Have to split controller names into lines, each with at most this many characters.

def savePhotos(imgList,directory):
    """ Save every photo from a list into separate files, the image name will
    contain the current time to make sure nothing is overwritten. Intended to
    be used in a separate process not to block the GUI.
    
    Arguments
    ----------
    imgList - list of images as output of cv2.VideoCapture.read.
    directory - str with the directory where the photo will be written.
    
    Example
    ----------
    p = multiprocessing.Process(target=savePhotos, args=(self.imgBuff,self.videoDirectory))
    p.start() # Don't p.join - will block the GUI thread.
    """
    outName=datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") # Time stamp the images.
    for i in range(len(imgList)):
        cv2.imwrite(os.path.join(directory,outName)+"_{}.jpg".format(i), imgList[i])

class IntValidator(wx.PyValidator):
    """ Validates data as it is entered into the text controls. """
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        """ Required Validator method """
        return IntValidator()

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def OnChar(self, event):
        """ Do the validation """
        keycode = int(event.GetKeyCode())
        if keycode < 256:
            key = chr(keycode)
            if not key in string.digits: # skip this char since it's not a digit
                return
        event.Skip()

class rovGuiArmDialog( ROVguiBaseClasses.armDialog ):
    """ Halts the application while the arm method is active """
    def __init__(self,delay):
        ROVguiBaseClasses.armDialog.__init__(self,None)
        self.armTimer.Start(delay*1000.0)
    
    def onClose(self,event):
        self.Destroy()

class rovGuiCommunicationsSettingsDialog( ROVguiBaseClasses.communicationsSettingsDialog ):
    """ Allows the user to adjust frequencies of sending and receiving data as well as
    adjust Arduino clock speed """
    def __init__(self,parent):
        ROVguiBaseClasses.communicationsSettingsDialog.__init__(self,parent)
        
        # set up validators to prevent non-numeric stuff from being entered
        self.arduinoLoopFreqTextControl.SetValidator(IntValidator())
        self.videoFrameFreqTextControl.SetValidator(IntValidator())
        self.controlInputsFreqTextControl.SetValidator(IntValidator())
        self.sensorReadingsFreqTextControl.SetValidator(IntValidator())
        
        # set initial values
        self.arduinoLoopFreqTextControl.SetValue(str(self.GetParent().freqArduino))
        self.videoFrameFreqTextControl.SetValue(str(self.GetParent().freqVideo))
        self.controlInputsFreqTextControl.SetValue(str(self.GetParent().freqControlInputs))
        self.sensorReadingsFreqTextControl.SetValue(str(self.GetParent().freqSensorReadings))
    
    def setArduinoFreq(self,event):
        if self.arduinoLoopFreqTextControl.GetValue():
            self.GetParent().freqArduino = int(self.arduinoLoopFreqTextControl.GetValue())
            self.GetParent().controlParameters['refreshRate'] = int(1000./self.GetParent().freqArduino)
    
    def setVideoFreq(self,event):
        # TODO there should be a built-in way to transfer data, can't find it right now
        if self.videoFrameFreqTextControl.GetValue():
            self.GetParent().freqVideo = int(self.videoFrameFreqTextControl.GetValue())
            self.GetParent().frameTimer.Start(int(1.0/self.GetParent().freqVideo*1000.0))
    
    def setControlFreq(self,event):
        if self.controlInputsFreqTextControl.GetValue():
            self.GetParent().freqControlInputs = int(self.controlInputsFreqTextControl.GetValue())
            self.GetParent().controlInputTimer.Start(int(1.0/self.GetParent().freqControlInputs*1000.0))
    
    def setSensorsFreq(self,event):
        if self.sensorReadingsFreqTextControl.GetValue():
            self.GetParent().freqSensorReadings = int(self.sensorReadingsFreqTextControl.GetValue())
            self.GetParent().sensorReadingsTimer.Start(int(1.0/self.GetParent().freqSensorReadings*1000.0))
    
    def changedFrameDir(self,event):
        self.GetParent().videoDirectory = self.videoFramePathPicker.GetPath()
    
    def closedSettingsDialog(self,even):
        self.Destroy()

class rovGuiMainFrame( ROVguiBaseClasses.mainFrame ):
    
    def __init__(self):
        """ Create the main frame, deriving from a baseline object which has all the panels, buttons, etc.
        already defined. """
        # initialise the underlying object
        ROVguiBaseClasses.mainFrame.__init__( self, None )
        
        # set-up own fields
        self.freqArduino = 100 # default refresh rate for the Arduino in Hz
        
        # video feed
        self.freqVideo = 5 # frame rate update frequency
        self.HUDcolour = (0,255,0) # RGB colour of the overlay on the HUD
        self.feedOn = False # switch indicating whether the video feed is on or off
        self.cameraIndex = 1 # index of the potential candidates for OpenCV capture object to actually use
        self.cameraCapture = 0 # this will hold the OpenCV VideocameraCapture object once it gets initialised
        self.frameSize = (640,480) # approximate width and height of the camera
        self.videoDirectory="/home/artur/Desktop" # will save every captured frame into this directory.
        self.imgBuff=[] # Hold images here and save them to HD every so often.
        self.imgBufLen=1000 # Will save photos to HD when the buffer holds this many images. Need this to avoid saving every single photo to HD.
        
        # serial communication
        self.portOpen = False # indicates if the serial communication port is open
        self.currentPort = 'None' # currently chosen port
        self.arduinoSerialConnection = 0 # holds the serial connection object once it has been initialised
        self.freqSensorReadings = 5
        self.freqControlInputs = 5
        
        # controller
        self.controller = 0
        self.currentController = 'None'
        self.upperRpmLimit = 50.0 # limit rpm of the motors to avoid overloading
        self.deadZone = 0.05 # extent of raw input which gets treated like zero
        self.lowerRpmLimit = 20 # lower value of output to Arduino
        self.zeroRpmValue = 10 # Arduino doesn't appear to like an actual 0, fool it by giving a small output
        
        # for translating xy of the controller axes (x-columns,y-rows) into actual motor rpm demand
        mapCoordsX = np.array([[-1, 0, 1],
                               [-1, 0, 1],
                               [-1, 0, 1]],dtype=np.float64)
        mapCoordsY = np.array([[ 1, 1, 1],
                               [ 0, 0, 0],
                               [-1,-1,-1]],dtype=np.float64)
        
        mapPort = np.array([[ 0,-1,-1],
                            [-1, 0, 1],
                            [ 0, 1, 1]],dtype=np.float64)
        mapStbd = np.array([[-1,-1, 0],
                            [ 1, 0,-1],
                            [ 1, 1, 0]],dtype=np.float64)
        
        self.rpsInterpPort = interpolate.interp2d(mapCoordsX, mapCoordsY, mapPort, kind='linear')
        self.rpsInterpStbd = interpolate.interp2d(mapCoordsX, mapCoordsY, mapStbd, kind='linear')
        
        # create the internal bitmap object by using an empty bitmap, this will be projected onto the panel
        self.bmp = wx.EmptyBitmap(self.frameSize[0],self.frameSize[1])
        self.videoFeed = statbmp.GenStaticBitmap(self.videoFeedPanel, wx.ID_ANY,self.bmp)
        
        # add to the panel and resize to fit everything
        self.videoFeedPanel.GetSizer().Add( self.videoFeed, 1,
            wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.videoFeedPanel.Layout()
        self.videoFeedPanel.SetFocus()
        
        # initialise the timing functions - will send and receive the data to/from Arduino at a specific interval
        self.frameTimer.Start(int(1.0/self.freqVideo*1000.0))
        self.sensorReadingsTimer.Start(int(1.0/self.freqSensorReadings*1000.0))
        self.controlInputTimer.Start(int(1.0/self.freqControlInputs*1000.0))
        
        # initialise throttle indicators
        self.throttleDial_portHor = throttleDial.Throttle(self.throttleDial_portHor, -1,sizeTuple=(40,115))
        self.throttleDial_portVer = throttleDial.Throttle(self.throttleDial_portVer, -1,sizeTuple=(40,115))
        self.throttleDial_stbdHor = throttleDial.Throttle(self.throttleDial_stbdHor, -1,sizeTuple=(40,115))
        self.throttleDial_stbdVer = throttleDial.Throttle(self.throttleDial_stbdVer, -1,sizeTuple=(40,115))
        
        # update the ports available at start-up
        self.updatePorts()
        self.portChoice.SetSelection(0)
        
        # repeat for controllers
        self.updateControllers()
        self.controllerChoice.SetSelection(0)
        
        # keeps the names and values of all control parameters
        self.controlParameters = {
            'refreshRate':int(1000./self.freqArduino), # delay needed after each loop() pass in ROVmain.ino
            'motorPortVer':0, # throttle of the port vert motor <-100,100>
            'motorPortHor':0,
            'motorStbdVer':0,
            'motorStbdHor':0,
            'forwardLED':0, # forward illumination LED on/off [True,False]
            }
        
        # names and values of sensor readings
        # need to call this for sensor readings to be sent
        self.sensorReadingsRequestObject = {'sendSensorReadings':1}
        self.sensorParameters = {
            'depthReading':0, # depth reading [m]
            }
        
        # this needs to be called for the modules to be armed
        self.armModulesCommand = {'armModules':1}
        
        self.Layout() # Make sure everything is nicely located in the sizers on startup.
    
    def onClose( self, event ):
        # close the serial port before terminating, need to make sure it isn't left hanging
        if self.portOpen:
            self.arduinoSerialConnection.close()
        # release the video capture object
        if self.feedOn:
            self.cameraCapture.release()
        self.Destroy()

    def onChoseSerialPort( self, event ):
        """ picks up the newly selected port and attempts to connect to Arduino via it """
        # ignore the None option
        if self.portChoice.GetStringSelection() != 'None':
            try:
                # don't re-open a working stream
                if self.portChoice.GetStringSelection() != self.currentPort:
                    # close any open ports if present
                    if self.portOpen:
                        self.arduinoSerialConnection.close()
    
                    self.arduinoSerialConnection = serial.Serial(self.portChoice.GetStringSelection(),
                                                                 19200, timeout = 2)
                    
                    if self.checkConnection():
                        self.portOpen = True
                        self.currentPort = self.portChoice.GetStringSelection()
                          
            except:
                wx.MessageBox('Unknown problem occurred while establishing connection using the chosen port!', 'Error', 
                          wx.OK | wx.ICON_ERROR)
                self.arduinoSerialConnection = 0
                self.portOpen = False
                self.updatePorts()
        
        # if None is chosen then close the current port
        else:
            if self.portOpen:
                self.arduinoSerialConnection.close()
            self.arduinoSerialConnection = 0
            self.portOpen = False
            self.currentPort = 'None'
    
    def onUpdatePorts( self, event ):
        # call the update ports method - need a wrapper to be able to call it during initialisation
        self.updatePorts()
        self.Layout() # makes sure the choice dropdown is big enough to fit all the choice options
    
    def onChoseCameraIndex( self, event ):
        """ Update the camera index selection """
        # do nothing if the new selection is the same as the current one
        if self.cameraIndex != int(self.cameraChoice.GetStringSelection()):
            # otherwise close the current camera feed and update the internal field
            self.cameraIndex = int(self.cameraChoice.GetStringSelection())
            # do nothing if the camera is off
            if self.feedOn:
                self.feedOn = False
                self.cameraCapture.release()
                self.cameraCapture = 0
        
    def onReconnectVideoFeed( self, event ):
        """ Setup a new capture """
        self.setupCapture()
    
    def onUpdateFrame(self,event):
        """ call the frame update when timer is activated """
#        print "updateFrame"
        self.getNewFrame()
    
    def onUpdateControlInputs(self,event):
        """ Send the control data to Arduino to set rps etc. """
#        print "updateControlInputs"
        self.updateControlInputs()
    
    def onUpdateSensorReadings(self,event):
        """ Send a request for new sensor data to Arduino, read it from serial and
        update the displays, plots, etc. """
#        print "updateSensorReadings"
        self.updateSensorReadings()
    
    def onArmModules(self,eent):
        """ Call the Arduino and ask it to arm modules; will wait for a gien time
        to give the MC enough slack to finish all tasks required """

        if self.portOpen and self.checkConnection:
            communicationProtocol.sendMessage(self.arduinoSerialConnection,self.armModulesCommand)
        
            line = self.arduinoSerialConnection.readline()
                
            readings = communicationProtocol.readMessage(line)
            
            try:
                delay = readings['setupDelay']
                dialog = rovGuiArmDialog(float(delay)/1000.)
                dialog.ShowModal()
            except KeyError:
                wx.MessageBox('Something fell over while asking Arduino to arm!', 'Error', wx.OK | wx.ICON_ERROR)

    def onCommunicationsSettings(self,event):
        """ show a dialog for customising communicaitons settings """
        dialog = rovGuiCommunicationsSettingsDialog(self)
        dialog.ShowModal()
        
    def onUpdateControllers(self,event):
        """ update the list of choices for available controllers """
        self.updateControllers()
        self.Layout() # makes sure the choice dropdown is big enough to fit all the choice options
    
    def onChoseController(self,event):
        """ set the newly chosen controller """
        # ignore the None option
        if self.controllerChoice.GetStringSelection() != 'None':
            try:
                # don't re-connect a controller which is already selected
                if self.controllerChoice.GetStringSelection() != self.currentController:
                    self.controller = controllerInterface.controller()
                    self.controller.setControllerIndex( self.controllerChoice.GetSelection()-1 )
                    self.currentController = self.controllerChoice.GetStringSelection()
                          
            except:
                wx.MessageBox('Unknown problem occurred while establishing connection with the chosen controller!', 'Error', 
                          wx.OK | wx.ICON_ERROR)
                self.controller = 0
                self.currentController = 'None'
                self.updateControllers()
        
        # if None is chosen then close the current port
        else:
            self.controller = 0
            self.currentController = 'None'

    #=================================
    # non-event function declarations
        
    def updateControllers(self):
        """ Check what controllers are now plugged in and refresh the available choices """
         # check what controllers are currently connected
        controllers = controllerInterface.getControllerNames()
        
        # save current selection
        currentSelection = self.controllerChoice.GetStringSelection()
        
        # Remove the current options
        for i in range(len(self.controllerChoice.GetStrings())-1,-1,-1):
            self.controllerChoice.Delete(i)

        # add the newly found controllers
        self.controllerChoice.Append('None')
        for controller in controllers:
        	# Make sure controller label isn't too long, which will make the layout explode - split it into parts if need be.
        	chunkIDs=range(0,len(controller),CONTROLLER_NAME_CHUNK_LENGTH) # At least [0]
        	chunkIDs.append(len(controller)) # Always need to go up to the entire length of the name.
        	# This is the name of the controller, or the first part of it that's shorter than the desired length.
        	controllerName=controller[chunkIDs[0]:chunkIDs[1]]
        	for i in range(1,len(chunkIDs)-1): # Add further parts of the controller's name.
	        	# Put this part of the controller's name in another line and indent slightly
				controllerName=controllerName+"\n"+"    "+controller[chunkIDs[i]:chunkIDs[i+1]]
        	self.controllerChoice.Append(controllerName) # Append this string to the selection.
            
        # attempt to return to the last selected controller, use None if it's not found
        if currentSelection in controllers:
            for i in range(len(controllers)):
                if controllers[i] == currentSelection:
                    self.controllerChoice.SetSelection(i+1)
        else:
            self.controllerChoice.SetSelection(0)
            self.currentController = 'None'
    
    def updatePorts(self):
        """ Checks the list of open serial ports and updates the internal list
        and the options shown in the dropdown selection menu. """
        
        # check what ports are currently open
        ports = communicationProtocol.getActivePorts()
        
        # save current selection
        currentSelection = self.portChoice.GetStringSelection()
        
        # Remove the current options
        for i in range(len(self.portChoice.GetStrings())-1,-1,-1):
            self.portChoice.Delete(i)

        # add the newly found ports
        self.portChoice.Append('None')
        for port in ports:
            self.portChoice.Append(port)
            
        # attempt to return to the last selected port, use None if it's not found
        if currentSelection in ports:
            for i in range(len(ports)):
                if ports[i] == currentSelection:
                    self.portChoice.SetSelection(i+1)
        else:
            self.portChoice.SetSelection(0)
            self.currentPort = 'None'
        
    def checkConnection( self ):
        """ Checks if the Arduino is still connected. """
        
        testMsgGood = True
        try:
            self.arduinoSerialConnection.inWaiting()
        except:
            testMsgGood = False

        if not self.arduinoSerialConnection or not self.arduinoSerialConnection.readable() or not testMsgGood:
            wx.MessageBox('Arduino isn\'t readable! Check the connection...', 'Error', 
                  wx.OK | wx.ICON_ERROR)
            
            # close the connection
            self.arduinoSerialConnection.close()
            self.arduinoSerialConnection = 0
            self.portOpen = False
            self.currentPort = 'None'
            
            # check what ports are open - will set choice as None if current port has been lost
            self.updateActivePorts()
            
            return False
        else:
            return True
    
    def setupCapture(self):
        """ Creates the camera capture object used to retrieve new frames """
        
        try:
            # create a cameraCapture object using OpenCV
            self.cameraCapture = cv2.VideoCapture(self.cameraIndex)
            self.cameraCapture.set(3,self.frameSize[0]) # set the size of the capture
            self.cameraCapture.set(4,self.frameSize[1])

            # get the current frame, convert colours and store
            ret, frame = self.cameraCapture.read()
            height, width = frame.shape[:2]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # update the internal bitmap with the current frame and update the display
            self.bmp = wx.BitmapFromBuffer(width, height, frame)
            self.videoFeed.SetBitmap(self.bmp)

            # resize the feed panel to fit everything
            self.videoFeedPanel.Layout()
            self.videoFeedPanel.SetFocus()

            # set the video feed as open
            self.feedOn = True
        
        except AttributeError:
            self.feedOn = False
            wx.MessageBox('Could not start video feed!', 'Error', wx.OK | wx.ICON_ERROR)
            
            # Create the bitmap object - converted photo from the ROV camera in wx format.
            self.videoFeed = statbmp.GenStaticBitmap(self.videoPanel, wx.ID_ANY,
                                                     #wx.Bitmap( u"../../Pictures/dron.jpg", wx.BITMAP_TYPE_ANY )
                                                     #wx.EmptyBitmap(640,480)
                                                     self.bmp
                                                     )
            
            # Add the photo to the panel and resize to fit everything.
            self.videoPanel.GetSizer().Add( self.videoFeed, 1, wx.ALL|wx.EXPAND, 5 )
            self.videoPanel.GetSizer().SetSizeHints(self)
            self.videoPanel.Layout()
            self.videoPanel.SetFocus()
            
        except:
            # TODO throw error - cannot start video feed
            pass
        
    def onNewFrame( self, event ):
        " Called when the internal timer requests a new frame to be updated. "
        try:
            # get a new frame, if it's OK then update the display
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame.shape[:2]
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.bmp = wx.BitmapFromBuffer(width, height, frame)
    
                self.videoFeed = statbmp.GenStaticBitmap(self.videoFeedPanel, wx.ID_ANY,self.bmp)
    
                # add to the panel and resize to fit everything
#                self.videoFeedPanel.GetSizer().Add( self.videoFeed, 1,
#                    wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
                self.videoFeedPanel.Layout()
                self.videoFeedPanel.SetFocus()
    
                # set the video feed as open
                self.feedOn = True
        
        except AttributeError:
            self.feedOn = False
            
            wx.MessageBox('Error while getting new frame', 'Error', 
                    wx.OK | wx.ICON_ERROR)
    
    def getNewFrame(self):
        """ This gets called when the internal timer requests a new frame to be updated.
        The function cameraCaptures a new frame and sends it to the static bitmap inside
        video feed panel. It also saves the capture to a file into self.videoDirectory. """

        # see if the video feed is on
        if self.feedOn:
            
            # get a new frame, if it's OK then update the display
            ret, frame = self.cameraCapture.read()
            
            if ret:
                # apply any colour filters, get the size of the frame
                editedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Keep the original image in RGB  to be able to save that one.
                height, width = frame.shape[:2]
                
                # will save this photo later
                self.imgBuff.append(frame)
                
                # put on overlay of telemetry
                cv2.putText(editedFrame,'DEPTH: {:6.2f} m'.format(self.sensorParameters['depthReading']),
                            (int(0.05*width),int(0.05*height)),
                            cv2.FONT_HERSHEY_PLAIN, 1, self.HUDcolour, 2) # size, colour, thickness modifier
                
                # put on tactical overlay
                editedFrame=cv2.line(editedFrame,(int(0.2*width),int(0.5*height)),(int(0.8*width),int(0.5*height)),self.HUDcolour,2)
                editedFrame=cv2.line(editedFrame,(int(0.5*width),int(0.1*height)),(int(0.5*width),int(0.9*height)),self.HUDcolour,2)
                editedFrame=cv2.circle(editedFrame,(int(0.5*width),int(0.5*height)), int(0.25*width), self.HUDcolour, 2)
                
                # update the bitmap shown in the GUI panel, thus refreshing the frame
                self.bmp.CopyFromBuffer(editedFrame)
                self.videoFeed.SetBitmap(self.bmp)
                
                # Save the photo to a file in a separate process (don't block the GUI).
                if len(self.imgBuff)>=self.imgBufLen:
                    p = multiprocessing.Process(target=savePhotos, args=(self.imgBuff,self.videoDirectory))
                    p.start() # Dont p.join - will block the GUI thread.
                    self.imgBuff=[] # Clear the buffer.
            
            else:
                # something went wrong with the video feed, close the cameraCapture and warn the user
                self.feedOn = False
                self.cameraCapture = 0
                
                wx.MessageBox('Video feed interrupted', 'Error', wx.OK | wx.ICON_ERROR)
                    
    def updateControlInputs(self):
        """ sends the control inputs to Arduino """
        # read the control variables
        if self.controller:
            self.controller.parseEvents()
            
            rpmPortVer = self.rpsInterpPort(self.controller.axesValues['lhsStickXaxis'],
                                            self.controller.axesValues['lhsStickYaxis'])
            rpmPortHor = self.rpsInterpPort(self.controller.axesValues['rhsStickXaxis'],
                                            self.controller.axesValues['rhsStickYaxis'])
            
            rpmStbdVer = self.rpsInterpStbd(self.controller.axesValues['lhsStickXaxis'],
                                            self.controller.axesValues['lhsStickYaxis'])
            rpmStbdHor = self.rpsInterpStbd(self.controller.axesValues['rhsStickXaxis'],
                                            self.controller.axesValues['rhsStickYaxis'])
            
            def mapMotorInputs(throttleDemand):
               # Accepts raw values between -1 and 1, scale and bound them to suit the Arduino side
                
                if np.abs(throttleDemand) < self.deadZone:
                    controlParameter = self.zeroRpmValue # actual demand sent to Arduino
                    thrustReading = 0. # for displaying throttle on dials
                
                else:
                    controlParameter = int(np.sign(throttleDemand)*((self.upperRpmLimit-self.lowerRpmLimit)/(1.0-self.deadZone)*(np.abs(throttleDemand)-self.deadZone) + self.lowerRpmLimit))
                    thrustReading = np.sign(controlParameter)*(np.abs(controlParameter)-self.lowerRpmLimit)/(self.upperRpmLimit-self.lowerRpmLimit)*100.

                return controlParameter,thrustReading
            
            # set the Arduino demands for motor rpm and update dial values
            self.controlParameters['motorPortVer'],self.throttleDial_portVer.currentThrottle = \
                    mapMotorInputs(rpmPortVer)
            self.controlParameters['motorStbdVer'],self.throttleDial_stbdVer.currentThrottle = \
                    mapMotorInputs(rpmStbdVer)
            self.controlParameters['motorPortHor'],self.throttleDial_portHor.currentThrottle = \
                    mapMotorInputs(rpmPortHor)
            self.controlParameters['motorStbdHor'],self.throttleDial_stbdHor.currentThrottle = \
                    mapMotorInputs(rpmStbdHor)
                    
            # set forward LED
            self.controlParameters['forwardLED'] = int(self.controller.buttonValues['butB'])
                    
        if self.portOpen:
            # make sure the connection has not been broken
            if self.checkConnection():
                # send the control variables
                communicationProtocol.sendMessage(self.arduinoSerialConnection,self.controlParameters)
                
        # update the display of engine throttles
        self.throttleDial_portVer.Refresh()
        self.throttleDial_portHor.Refresh()
        self.throttleDial_stbdVer.Refresh()
        self.throttleDial_stbdHor.Refresh()
    
    def updateSensorReadings(self):
        """ Go over each sensor and get its reading, updating the internally stored values """
        if self.portOpen:
            # make sure the connection has not been broken
            if self.checkConnection():
                pass
                # ask the Arduino nicely to return the current readings
                communicationProtocol.sendMessage(self.arduinoSerialConnection,
                                                  self.sensorReadingsRequestObject)
                
                # get the most recent line from the serial port
                line = self.arduinoSerialConnection.readline()
                
                # pass on to the parser
                readings = communicationProtocol.readMessage(line)
                
                # update sensor and other readings
                for readingKey in readings:
                    self.sensorParameters[readingKey] = float(readings[readingKey])
                    
# implements the GUI class to run a wxApp
class rovGuiApp(wx.App):
    def OnInit(self):
        self.frame = rovGuiMainFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        return True

if __name__ == "__main__":
    # need an environment variable on Ubuntu to make the menu bars show correctly
    env = os.environ
    if not(('UBUNTU_MENUPROXY' in env) and (env['UBUNTU_MENUPROXY'] == 0)):
        os.environ["UBUNTU_MENUPROXY"] = "0"
    
    # start the app
    app = rovGuiApp()
    app.MainLoop()
