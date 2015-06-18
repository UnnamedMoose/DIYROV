# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class mainFrame
###########################################################################

class mainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		mainVertSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.videoPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		videoPanelSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		self.videoPanel.SetSizer( videoPanelSizer )
		self.videoPanel.Layout()
		videoPanelSizer.Fit( self.videoPanel )
		mainVertSizer.Add( self.videoPanel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( mainVertSizer )
		self.Layout()
		self.frameTimer = wx.Timer()
		self.frameTimer.SetOwner( self, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_TIMER, self.onNewFrame, id=wx.ID_ANY )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onNewFrame( self, event ):
		event.Skip()
	

