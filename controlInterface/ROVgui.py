# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:34:31 2015

@author: artur
"""

import ROVgui_mainFrame

import wx
from wx.lib import statbmp
import cv2
import os

class rovGuiMainFrame( ROVgui_mainFrame.mainFrame ):
    def __init__(self):
        # initialise the underlying object
        ROVgui_mainFrame.mainFrame.__init__( self, None )
        
        # own fields
        self.fps = 15 # frame rate of the timer
        self.HUDcolour = (0,255,0)
        
        # initialise the timing function
        self.frameTimer.Start(int(1.0/self.fps*1000.0))
        
        # create a capture object using OpenCV
        self.capture = cv2.VideoCapture(1)
        
        # get the current frame, convert colours and store
        ret, frame = self.capture.read()
        height, width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(width, height, frame)
        
        # create the bitmap object
        self.videoFeed = statbmp.GenStaticBitmap(self.videoPanel, wx.ID_ANY,
                                                 #wx.Bitmap( u"../../Pictures/dron.jpg", wx.BITMAP_TYPE_ANY )
                                                 #wx.EmptyBitmap(640,480)
                                                 self.bmp
                                                 )
        
        # add to the panel and resize to fit everything
        self.videoPanel.GetSizer().Add( self.videoFeed, 1, wx.ALL|wx.EXPAND, 5 )
        self.videoPanel.GetSizer().SetSizeHints(self)
        self.videoPanel.Layout()
        self.videoPanel.SetFocus()
        
    # called when the internal timer requests a new frame to be updated
    def onNewFrame( self, event ):
        # get a new frame, if it's OK then update the display
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width = frame.shape[:2]
            
            # put on overlay of telemetry
            cv2.putText(frame,'DEPTH: {:6.2f} m'.format(self.getDepth()), (int(0.05*width),int(0.05*height)),
                        cv2.FONT_HERSHEY_PLAIN, 1, self.HUDcolour, 2) # size, colour, thickness modifier
            
            # put on tactical overlay
            frame=cv2.line(frame,(int(0.2*width),int(0.5*height)),(int(0.8*width),int(0.5*height)),self.HUDcolour,2)
            frame=cv2.line(frame,(int(0.5*width),int(0.1*height)),(int(0.5*width),int(0.9*height)),self.HUDcolour,2)
            frame=cv2.circle(frame,(int(0.5*width),int(0.5*height)), int(0.25*width), self.HUDcolour, 2)
            
            self.bmp.CopyFromBuffer(frame)
            self.videoFeed.SetBitmap(self.bmp)
            
    def getDepth(self):
        """ Should access the controller class and return current depth sensor reading """
        return 0.0

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
