#!/usr/bin/env/python
import cv2, wx, os

timerID = 1000
cameraID = 0
refreshRate = 15 # fps
frameSize = (640,480) # approximate width and height of the camera

class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        # create a simple wx frame
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Photo Control')
        self.panel = wx.Panel(self.frame)
 
        # create OpenCV object for image acquisition
        self.cameraCapture = cv2.VideoCapture(cameraID)
        self.cameraCapture.set(3,frameSize[0]) # Set the width...
        self.cameraCapture.set(4,frameSize[1]) #...and height of the image.
        
        # create the timer and bind it to refresh function
        self.frameTimer = wx.Timer()
        self.frameTimer.SetOwner(self, timerID)
        self.Bind( wx.EVT_TIMER, self.onRefresh, id=timerID)

        # initialise main frame
        self.createWidgets()
        self.frame.Show()
        
        # start the timer
        self.frameTimer.Start(int(1.0/refreshRate*1000.0))

    def createWidgets(self):
        """ Create widgets and populate the main frame """
        img = wx.EmptyImage(frameSize[0],frameSize[1])
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.BitmapFromImage(img))
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)
        self.panel.Layout()

    def getNewFrame(self):
        """ acquire a new frame and store as a bmp inside the frame class """
        ret, picture = self.cameraCapture.read()
        height, width = picture.shape[:2]
        print "Got frame with size W{:d} x H{:d}".format(width,height)
        picture = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(width, height, picture)
        
    def onRefresh(self,event):
        """ handle getting a new frame and publishing it in the GUI """
#        print "on view: {}".format(event)
#        filepath = self.photoTxt.GetValue()
#        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
#        # scale the image, preserving the aspect ratio
#        W = img.GetWidth()
#      5  H = img.GetHeight()
#        if W > H:
#            NewW = self.PhotoMaxSize
#            NewH = self.PhotoMaxSize * H / W
#        else:
#            NewH = self.PhotoMaxSize
#            NewW = self.PhotoMaxSize * W / H
#        img = img.Scale(NewW,NewH)
        self.getNewFrame() # Refresh self.bmp
        self.imageCtrl.SetBitmap(self.bmp)#wx.BitmapFromImage(img))
        self.panel.Refresh()
 
if __name__ == '__main__':
    app = PhotoCtrl()
    app.MainLoop()
