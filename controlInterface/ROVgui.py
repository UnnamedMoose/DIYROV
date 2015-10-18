#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:34:31 2015

@author: artur
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

class rovGuiMainFrame( ROVguiBaseClasses.mainFrame ):
    
    def __init__(self):
        """ Create the main frame, deriving from a baseline object which has all the panels, buttons, etc.
        already defined. """
        # initialise the underlying object
        ROVguiBaseClasses.mainFrame.__init__( self, None )
        
        # set-up own fields
        self.freqArduino = 100 # default refresh rate for the Arduino in Hz
        
        # video feed
        self.freqVideo = 5 # frame rate update frquency
        self.HUDcolour = (0,255,0) # RGB colour of the overlay on the HUD
        self.feedOn = False # switch indicating whether the video feed is on or off
        self.cameraIndex = 1 # index of the potential candidates for OpenCV capture object to actually use
        self.cameraCapture = 0 # this will hold the OpenCV VideocameraCapture object once it gets initialised
        
        # serial communication
        self.portOpen = False # indicates if the serial communication port is open
        self.currentPort = 'None' # currently chosen port
        self.arduinoSerialConnection = 0 # holds the serial connecion object once it has been initialised
        self.freqSensorReadings = 5
        self.freqControlInputs = 5
        
        # controller
        self.controller = 0
        self.currentController = 'None'
        
        # create the internal bitmap object by using an empty bitmap, this will be projected onto the panel
        self.bmp = wx.EmptyBitmap(400,300)
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
            'forwardLED':False, # forward illumination LED on/off [True,False]
            }
        
        # names and values of sensor readings
        # need to call this for sensor readings to be sent
        self.sensorReadingsRequestObject = {'sendSensorReadings':1}
        self.sensorParameters = {
            'depthReading':0, # depth reading [m]
            }
        
        # this needs to be called for the modules to be armed
        self.armModulesCommand = {'armModules':1}
    
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
        self.getNewFrame()
    
    def onUpdateControlInputs(self,event):
        """ Send the control data to Arduino to set rps etc. """
        self.updateControlInputs()
    
    def onUpdateSensorReadings(self,event):
        """ Send a request for new sensor data to Arduino, read it from serial and
        update the displays, plots, etc. """
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

    def newSliderValue(self,event):
        """ temp function """
        # TODO remove when no longer needed
        self.controlParameters['motorPortHor'] = self.tempSlider.GetValue()
        print self.controlParameters['motorPortHor']
        
    #=================================
    # non-event funtion declarations
        
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
            self.controllerChoice.Append(controller)
            
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
    
    def getNewFrame(self):
        """ This gets called when the internal timer requests a new frame to be updated.
        The function cameraCaptures a new frame and sends it to the static bitmap inside
        video feed panel """

        # see if the video feed is on
        if self.feedOn:
            
            # get a new frame, if it's OK then update the display
            ret, frame = self.cameraCapture.read()
            
            if ret:
                # apply any colour filters, get the size of the frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame.shape[:2]

                # put on overlay of telemetry
                cv2.putText(frame,'DEPTH: {:6.2f} m'.format(self.sensorParameters['depthReading']),
                            (int(0.05*width),int(0.05*height)),
                            cv2.FONT_HERSHEY_PLAIN, 1, self.HUDcolour, 2) # size, colour, thickness modifier
                
                # put on tactical overlay
                frame=cv2.line(frame,(int(0.2*width),int(0.5*height)),(int(0.8*width),int(0.5*height)),self.HUDcolour,2)
                frame=cv2.line(frame,(int(0.5*width),int(0.1*height)),(int(0.5*width),int(0.9*height)),self.HUDcolour,2)
                frame=cv2.circle(frame,(int(0.5*width),int(0.5*height)), int(0.25*width), self.HUDcolour, 2)
                
                # update the bitmap shown in the GUI panel, thus refreshing the frame
                self.bmp.CopyFromBuffer(frame)
                self.videoFeed.SetBitmap(self.bmp)
            
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
            
            # TODO need to work out how to map raw controller inputs into actual values
            self.controlParameters['motorPortVer'] = self.controller.axesValues['lhsStickYaxis']*100.
            self.controlParameters['motorStbdVer'] = self.controller.axesValues['rhsStickYaxis']*100.
            self.controlParameters['motorPortHor'] = self.controller.axesValues['lhsStickXaxis']*100.
            self.controlParameters['motorStbdHor'] = self.controller.axesValues['rhsStickXaxis']*100.
#            print self.controller.axesValues.values(), self.controller.buttonValues.values()
        
        if self.portOpen:
            # make sure the connection has not been broken
            if self.checkConnection():
                # send the control variables
                communicationProtocol.sendMessage(self.arduinoSerialConnection,self.controlParameters)
                
        # update the display of engine throttles
        self.throttleDial_portVer.currentThrottle = self.controlParameters['motorPortVer']
        self.throttleDial_portVer.Refresh()
        self.throttleDial_portHor.currentThrottle = self.controlParameters['motorPortHor']
        self.throttleDial_portHor.Refresh()
        self.throttleDial_stbdVer.currentThrottle = self.controlParameters['motorStbdVer']
        self.throttleDial_stbdVer.Refresh()
        self.throttleDial_stbdHor.currentThrottle = self.controlParameters['motorStbdHor']
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
