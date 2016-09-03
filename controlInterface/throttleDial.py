#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 20:18:07 2015
@author: alek
"""

import wx

class Throttle(wx.Panel):
    " A panel with a throttle display and a manual selector. "
    def __init__(self, parent, ID, sizeTuple=(50,200)):
        wx.Panel.__init__(self, parent, ID, size=sizeTuple)
        self.parent = parent
        self.SetBackgroundColour('#000000')
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.currentThrottle = 0 # How much throttle is currently selected.
        self.resolution = 5 # How many throttle levels can be displayed. This is the throttle step.
        self.maxNoSteps = int(sizeTuple[1]/2./self.resolution) # How many steps can be plotted for +ve and -ve throttle.
        
        self.width = 5
        self.stepHeight = 4
        
    def OnPaint(self, event):
        " Update the display to show the current throttle. "
        dc = wx.PaintDC(self) # Paint on the panel with recangles.
        dc.SetDeviceOrigin(0, self.Size[1]/2.)
        dc.SetAxisOrientation(True, True)

        pos = self.currentThrottle # We have to know how much throttle is
        limit = int(pos / float(self.resolution)) # How much throttle is actually displayed.

        for i in range(1, self.maxNoSteps+1): # Plot the positive throttle part.
            if i > limit: # Possible +ve throttle levels.
                dc.SetBrush(wx.Brush('#075100')) 
                dc.DrawRectangle(self.width, i*self.stepHeight-5, 30, self.resolution)
            elif pos > 0: # Current +ve throttle - bright green.
                dc.SetBrush(wx.Brush('#36ff27'))
                dc.DrawRectangle(self.width, i*self.stepHeight-5, 30, self.resolution)

        for i in range(1, self.maxNoSteps+1): # Plot the negative throttle part.
            if i > abs(limit) or pos > 0: # Possible -ve throttle levels. Use abs because limit can be negative.
                dc.SetBrush(wx.Brush('#8B0000'))
                dc.DrawRectangle(self.width, -i*self.stepHeight-5, 30, self.resolution)
            elif pos < 0: # Current -ve throttle - bright red.
                dc.SetBrush(wx.Brush('#FF0000'))
                dc.DrawRectangle(self.width, -i*self.stepHeight-5, 30, self.resolution)

if __name__ == '__main__':
    class ThrottleWidget(wx.Frame):
        " A frame that holds a throttle display and manual selection slider. "
        def __init__(self, parent, id, title):
            wx.Frame.__init__(self, parent, id, title, size=(190, 280))
    
            self.sel = 0 # Current selection of the throttle.
            panel = wx.Panel(self, -1) # Main panel.
            
            # Throttle display.
            centerPanel = wx.Panel(panel, -1)
            self.throttle = Throttle(centerPanel, -1)
    
            # Manual selection slider.
            self.slider = wx.Slider(panel, -1, self.sel, -100, 100, (-1, -1), (25, 180), 
    		wx.VERTICAL | wx.SL_LABELS | wx.SL_INVERSE)
            self.slider.SetFocus()
    
            # Put the slider beside the display.
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(centerPanel, 0,  wx.LEFT | wx.TOP, 20)
            hbox.Add(self.slider, 0, wx.LEFT | wx.TOP, 23)
    
            # Whenever the slider is moved update the display.
            self.Bind(wx.EVT_SCROLL, self.OnScroll)
            panel.SetSizer(hbox)
    
            self.Centre()
            self.Show(True)
    
    
        def OnScroll(self, event):
            " Update the display to match the slider. "
            self.sel = event.GetInt()
            self.throttle.currentThrottle = self.sel # Tell the display what throttle to show.
            self.throttle.Refresh()
    
    
    app = wx.App()
    ThrottleWidget(None, -1, 'PORT')
    app.MainLoop()
