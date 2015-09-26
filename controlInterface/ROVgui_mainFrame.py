# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

frameTimerID = 1000
controlInputTimerID = 1001
sensorReadingsTimerID = 1002
armTimerID = 1003

###########################################################################
## Class mainFrame
###########################################################################

class mainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 950,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 950,-1 ), wx.DefaultSize )
		
		mainHorSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		mainFlexHorSizer = wx.FlexGridSizer( 0, 2, 0, 0 )
		mainFlexHorSizer.SetFlexibleDirection( wx.HORIZONTAL )
		mainFlexHorSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.cotrolPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 350,-1 ), wx.TAB_TRAVERSAL )
		self.cotrolPanel.SetMinSize( wx.Size( 300,-1 ) )
		self.cotrolPanel.SetMaxSize( wx.Size( 450,-1 ) )
		
		controlSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.statusDisplay = wx.Panel( self.cotrolPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		statusDisplaySizer = wx.BoxSizer( wx.HORIZONTAL )
		
		fgSizer2 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		throttleSizerPort = wx.BoxSizer( wx.VERTICAL )
		
		self.throttleDial_portVer = wx.Panel( self.statusDisplay, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.throttleDial_portVer.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DDKSHADOW ) )
		self.throttleDial_portVer.SetMinSize( wx.Size( 40,115 ) )
		
		throttleSizerPort.Add( self.throttleDial_portVer, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.throttleDial_portHor = wx.Panel( self.statusDisplay, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.throttleDial_portHor.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DDKSHADOW ) )
		
		throttleSizerPort.Add( self.throttleDial_portHor, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer2.Add( throttleSizerPort, 1, wx.EXPAND, 5 )
		
		self.arrangementGraphic = wx.StaticBitmap( self.statusDisplay, wx.ID_ANY, wx.Bitmap( u"../Documentation/Drawings/arrangementOverview.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.Size( 100,250 ), 0 )
		fgSizer2.Add( self.arrangementGraphic, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		throttleSizerStbd = wx.BoxSizer( wx.VERTICAL )
		
		self.throttleDial_stbdVer = wx.Panel( self.statusDisplay, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.throttleDial_stbdVer.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DDKSHADOW ) )
		self.throttleDial_stbdVer.SetMinSize( wx.Size( 40,115 ) )
		
		throttleSizerStbd.Add( self.throttleDial_stbdVer, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.throttleDial_stbdHor = wx.Panel( self.statusDisplay, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.throttleDial_stbdHor.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DDKSHADOW ) )
		
		throttleSizerStbd.Add( self.throttleDial_stbdHor, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer2.Add( throttleSizerStbd, 1, wx.EXPAND, 5 )
		
		
		statusDisplaySizer.Add( fgSizer2, 1, wx.EXPAND, 5 )
		
		
		self.statusDisplay.SetSizer( statusDisplaySizer )
		self.statusDisplay.Layout()
		statusDisplaySizer.Fit( self.statusDisplay )
		controlSizer.Add( self.statusDisplay, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.controls = wx.Panel( self.cotrolPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		controlsSizerVert = wx.BoxSizer( wx.VERTICAL )
		
		portChoiceVertSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		portChoiceVertSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		portChoiceDropdownHorSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.portChoiceLabel = wx.StaticText( self.controls, wx.ID_ANY, u"Serial port:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.portChoiceLabel.Wrap( -1 )
		portChoiceDropdownHorSizer.Add( self.portChoiceLabel, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		portChoiceDropdownHorSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		portChoiceChoices = []
		self.portChoice = wx.Choice( self.controls, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, portChoiceChoices, 0 )
		self.portChoice.SetSelection( 0 )
		portChoiceDropdownHorSizer.Add( self.portChoice, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )
		
		
		portChoiceVertSizer.Add( portChoiceDropdownHorSizer, 1, wx.EXPAND, 5 )
		
		portChoiceButtonHorSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		portChoiceButtonHorSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.updatePortsButton = wx.Button( self.controls, wx.ID_ANY, u"Update ports", wx.DefaultPosition, wx.DefaultSize, 0 )
		portChoiceButtonHorSizer.Add( self.updatePortsButton, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		portChoiceVertSizer.Add( portChoiceButtonHorSizer, 1, wx.EXPAND, 5 )
		
		
		controlsSizerVert.Add( portChoiceVertSizer, 1, wx.EXPAND, 5 )
		
		cameraChoiceVertSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		cameraChoiceVertSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		cameraChoiceDropdownHorSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.cameraChoiceLabel = wx.StaticText( self.controls, wx.ID_ANY, u"Camera index:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.cameraChoiceLabel.Wrap( -1 )
		cameraChoiceDropdownHorSizer.Add( self.cameraChoiceLabel, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		cameraChoiceDropdownHorSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		cameraChoiceChoices = [ u"0", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"10", wx.EmptyString, wx.EmptyString, wx.EmptyString ]
		self.cameraChoice = wx.Choice( self.controls, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cameraChoiceChoices, 0 )
		self.cameraChoice.SetSelection( 1 )
		cameraChoiceDropdownHorSizer.Add( self.cameraChoice, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )
		
		
		cameraChoiceVertSizer.Add( cameraChoiceDropdownHorSizer, 1, wx.EXPAND, 5 )
		
		cameraChoiceButtonHorSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		cameraChoiceButtonHorSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.cameraReconnectButton = wx.Button( self.controls, wx.ID_ANY, u"Reconnect video feed", wx.DefaultPosition, wx.DefaultSize, 0 )
		cameraChoiceButtonHorSizer.Add( self.cameraReconnectButton, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		cameraChoiceVertSizer.Add( cameraChoiceButtonHorSizer, 1, wx.EXPAND, 5 )
		
		
		controlsSizerVert.Add( cameraChoiceVertSizer, 1, wx.EXPAND, 5 )
		
		self.armModules = wx.Button( self.controls, wx.ID_ANY, u"Arm modules", wx.DefaultPosition, wx.DefaultSize, 0 )
		controlsSizerVert.Add( self.armModules, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.tempSlider = wx.Slider( self.controls, wx.ID_ANY, 0, -100, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		controlsSizerVert.Add( self.tempSlider, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.controls.SetSizer( controlsSizerVert )
		self.controls.Layout()
		controlsSizerVert.Fit( self.controls )
		controlSizer.Add( self.controls, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.cotrolPanel.SetSizer( controlSizer )
		self.cotrolPanel.Layout()
		mainFlexHorSizer.Add( self.cotrolPanel, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.videoFeedPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		self.videoFeedPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.videoFeedPanel.SetMinSize( wx.Size( 600,450 ) )
		
		ideoFeedSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		self.videoFeedPanel.SetSizer( ideoFeedSizer )
		self.videoFeedPanel.Layout()
		ideoFeedSizer.Fit( self.videoFeedPanel )
		mainFlexHorSizer.Add( self.videoFeedPanel, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		mainHorSizer.Add( mainFlexHorSizer, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( mainHorSizer )
		self.Layout()
		self.frameTimer = wx.Timer()
		self.frameTimer.SetOwner( self, frameTimerID )
		self.controlInputTimer = wx.Timer()
		self.controlInputTimer.SetOwner( self, controlInputTimerID )
		self.sensorReadingsTimer = wx.Timer()
		self.sensorReadingsTimer.SetOwner( self, sensorReadingsTimerID )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.onClose )
		self.portChoice.Bind( wx.EVT_CHOICE, self.onChoseSerialPort )
		self.updatePortsButton.Bind( wx.EVT_BUTTON, self.onUpdatePorts )
		self.cameraChoice.Bind( wx.EVT_CHOICE, self.onChoseCameraIndex )
		self.cameraReconnectButton.Bind( wx.EVT_BUTTON, self.onReconnectVideoFeed )
		self.armModules.Bind( wx.EVT_BUTTON, self.onArmModules )
		self.tempSlider.Bind( wx.EVT_SCROLL, self.newSliderValue )
		self.Bind( wx.EVT_TIMER, self.onUpdateFrame, id=frameTimerID )
		self.Bind( wx.EVT_TIMER, self.onUpdateControlInputs, id=controlInputTimerID )
		self.Bind( wx.EVT_TIMER, self.onUpdateSensorReadings, id=sensorReadingsTimerID )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onClose( self, event ):
		event.Skip()
	
	def onChoseSerialPort( self, event ):
		event.Skip()
	
	def onUpdatePorts( self, event ):
		event.Skip()
	
	def onChoseCameraIndex( self, event ):
		event.Skip()
	
	def onReconnectVideoFeed( self, event ):
		event.Skip()
	
	def onArmModules( self, event ):
		event.Skip()
	
	def newSliderValue( self, event ):
		event.Skip()
	
	def onUpdateFrame( self, event ):
		event.Skip()
	
	def onUpdateControlInputs( self, event ):
		event.Skip()
	
	def onUpdateSensorReadings( self, event ):
		event.Skip()
	

###########################################################################
## Class armDialog
###########################################################################

class armDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 300,150 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		armDialogSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.armText = wx.StaticText( self, wx.ID_ANY, u"Arming modules, please wait ...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.armText.Wrap( -1 )
		armDialogSizer.Add( self.armText, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.SetSizer( armDialogSizer )
		self.Layout()
		self.armTimer = wx.Timer()
		self.armTimer.SetOwner( self, armTimerID )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_TIMER, self.onClose, id=armTimerID )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onClose( self, event ):
		event.Skip()
	

