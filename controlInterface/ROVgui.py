#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:34:31 2015

@author: artur
"""

import ROVgui_mainFrame
import throttleDial

import wx
from wx.lib import statbmp
import cv2
import os, sys, glob
import serial

class rovGuiMainFrame( ROVgui_mainFrame.mainFrame ):
    
    def __init__(self):
        """ Create the main frame, deriving from a baseline object which has all the panels, buttons, etc.
        already defined. """
        # initialise the underlying object
        ROVgui_mainFrame.mainFrame.__init__( self, None )
        
        # set-up own fields
        self.fps = 15 # frame rate of the timer
        self.HUDcolour = (0,255,0) # RGB colour of the overlay on the HUD
        
        self.feedOn = False # switch indicating whether the video feed is on or off
        self.cameraIndex = 1 # index of the potential candidates for OpenCV capture object to actually use
        self.cameraCapture = 0 # this will hold the OpenCV VideocameraCapture object once it gets initialised
        
        self.portOpen = False # indicates if the serial communication port is open
        self.currentPort = 'None' # currently chosen port
        self.arduinoSerialConnection = 0 # holds the serial connecion object once it has been initialised
        
        # create the internal bitmap object by using an empty bitmap, this will be projected onto the panel
        self.bmp = wx.EmptyBitmap(400,300)
        self.videoFeed = statbmp.GenStaticBitmap(self.videoFeedPanel, wx.ID_ANY,self.bmp)
        
        # add to the panel and resize to fit everything
        self.videoFeedPanel.GetSizer().Add( self.videoFeed, 1,
            wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.videoFeedPanel.Layout()
        self.videoFeedPanel.SetFocus()
        
        # initialise the timing function - will send the data to Arduino at a specific interval
        self.frameTimer.Start(int(1.0/self.fps*1000.0))
        
        # initialise throttle indicators
        self.throttleDial_portHor = throttleDial.Throttle(self.throttleDial_portHor, -1,sizeTuple=(40,115))
        self.throttleDial_portVert = throttleDial.Throttle(self.throttleDial_portVert, -1,sizeTuple=(40,115))
        self.throttleDial_stbdHor = throttleDial.Throttle(self.throttleDial_stbdHor, -1,sizeTuple=(40,115))
        self.throttleDial_stbdVert = throttleDial.Throttle(self.throttleDial_stbdVert, -1,sizeTuple=(40,115))
        
        # update the ports available at start-up
        self.updateActivePorts()
        self.portChoice.SetSelection(0)
    
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
                        
                        # set the initial state
                        self.updateState()
                          
            except:
                wx.MessageBox('Unknown problem occurred while establishing connection using the chosen port!', 'Error', 
                          wx.OK | wx.ICON_ERROR)
                self.arduinoSerialConnection = 0
                self.portOpen = False
        
        # if None is chosen then close the current port
        else:
            if self.portOpen:
                self.arduinoSerialConnection.close()
            self.arduinoSerialConnection = 0
            self.portOpen = False
            self.currentPort = 'None'
    
    def onUpdatePorts( self, event ):
        """ Update the available serial ports """
        self.updateActivePorts()
    
    def onChoseCameraIndex( self, event ):
        """ Update the camera index selection """
        # do nothing if the new selection is the same as the current one
        if self.cameraIndex != int(self.cameraChoice.GetStringSelection()):
            # otherwise close the current camera feed and update the internal field
            self.cameraIndex = int(self.cameraChoice.GetStringSelection())
            self.feedOn = False
            self.cameraCapture = 0
        
    def onReconnectVideoFeed( self, event ):
        self.setupCapture()
            
    def getDepth(self):
        """ Should access the controller class and return current depth sensor reading """
        return 0.0
    
    def onClose( self, event ):
        # close the serial port before terminating, need to make sure it isn't left hanging
        if self.portOpen:
            self.arduinoSerialConnection.close()
        self.Destroy()

    def onUpdateState ( self, event ):
        """ Main function responsible for sending the desired system state
        to the Arduino and updating the display """
        
        # update the video feed
        self.getNewFrame()
        
        # attempt to communicate with the Arduino
        if self.portOpen:
            # make sure the connection has not been broken
            if self.checkConnection():
                pass
                # send the message
#                self.arduinoSerialConnection.write(self.inputStartChar + 'deltaServo'
#                    + self.dataDelimiter + str(self.demandSlider.GetValue()+90) + self.inputEndChar)
                
                # store the data point in the plot
                # distinguish between first and subsequent messages
#                if len(self.plot.datat) == 0:
#                    self.plot.update( 0 + int(1.0/self.updateFrequency),
#                                 self.demandSlider.GetValue() )
#                                 
#                else:
#                    self.plot.update( self.plot.datat[-1] + int(1.0/self.updateFrequency),
#                                 self.demandSlider.GetValue() )
    
    #=================================
    # non-event funtion declarations
    
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
            
            wx.MessageBox('Could not start video feed', 'Error', 
                    wx.OK | wx.ICON_ERROR)
    
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
                cv2.putText(frame,'DEPTH: {:6.2f} m'.format(self.getDepth()), (int(0.05*width),int(0.05*height)),
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
                
                wx.MessageBox('Video feed interrupted', 'Error', 
                    wx.OK | wx.ICON_ERROR)
                    
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
    
    def updateActivePorts( self ):
        """ Checks the list of open serial ports and updates the internal list
        and the options shown in the dropdown selection menu. """
        
        # find the open ports - main part of the code from:
        # http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
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
            self.currentSelection = 'None'

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

""" THIS PIECE OF CODE GETS KEYBOARD INPUTS

btn = wx.Button(panel, label="OK")
    
        btn.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
    
    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        print "Keycode: {}".format(keycode)
        
        if event.ShiftDown():
            print "Shift is down!"
            
        if event.AltDown():
            print "Alt is down!"

        if event.CmdDown():
            print "Command is down!"

        if event.ControlDown():
            print "Control is down!"

        if keycode==wx.WXK_SPACE:
            print "space"
        elif keycode==wx.WXK_LEFT or keycode==wx.WXK_NUMPAD_LEFT:
            print "left"
        elif keycode==wx.WXK_RIGHT or keycode==wx.WXK_NUMPAD_RIGHT:
            print "right"
        elif keycode==wx.WXK_UP or keycode==wx.WXK_NUMPAD_UP:
            print "up"
        elif keycode==wx.WXK_DOWN or keycode==wx.WXK_NUMPAD_DOWN:
            print "down"
        elif keycode==wx.WXK_PAGEUP or keycode==wx.WXK_NUMPAD_PAGEUP:
            print "page up"
        elif keycode==wx.WXK_PAGEDOWN or keycode==wx.WXK_NUMPAD_PAGEDOWN:
            print "page down"

        event.Skip()

"""