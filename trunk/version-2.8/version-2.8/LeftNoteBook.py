# -*- coding: utf-8 -*-

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# LeftNoteBook.py ---
#                     --------------------------------
#                        Copyright (c) 2013
#                       Laurent CAPOCCHI
#                      University of Corsica
#                     --------------------------------
# Version 1.0                                        last modified: 10/11/2013
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#
# GENERAL NOTES AND REMARKS:
#
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#
# GLOBAL VARIABLES AND FUNCTIONS
#
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

import wx
import os

import Container

from Patterns.Observer import Observer
from LibPanel import LibPanel
from PropPanel import PropPanel

### --------------------------------------------------------------------------
class GeneralNotebook(Observer):
	def __init__(self, *args, **kwargs):
		"""
		"""

		### label list
		self.labelList = (_("Libraries"), _("Properties"))
		
		### Create panels with name used for label tab definition...
		libPanel = LibPanel(self, self.labelList[0])
		propPanel = PropPanel(self, self.labelList[1])
		
		### selected model for libPanel managing
		self.selected_model = None

		self.__set_properties()

		### must be invoked here, at the end of constructor
		self.AddPage(libPanel, libPanel.GetName(), imageId=0)
		self.AddPage(propPanel, propPanel.GetName(), imageId=1)
		
		### binding event
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.__PageChanged)
		
	def __set_properties(self):
			"""
			"""
			imgList = wx.ImageList(16, 16)
			for img in [os.path.join(ICON_PATH_16_16,'db.png'), os.path.join(ICON_PATH_16_16,'properties.png'), os.path.join(ICON_PATH_16_16,'simulation.png')]:
				imgList.Add(wx.Image(img, wx.BITMAP_TYPE_PNG).ConvertToBitmap())
			self.AssignImageList(imgList)
			
	def __PageChanged(self, evt):
			"""
			"""
			if evt.GetSelection() == 1:
				pass
			evt.Skip()
			
	def GetLibPanel(self):
			""" Get Libraries panel if exist
			"""
			### list of label of all exsiting panel
			labelList = map(self.GetPageText, [i for i in range(self.GetPageCount())])
			try:
				### try to find if panel exist from label
				index = labelList.index(self.labelList[0])
			except ValueError, info:
				### index not match, panel not existing
				return None
			else:
				### return the Panel object from the finded index
				return self.GetPage(index)
			
	def GetPropPanel(self):
		""" Get Properties panel ef exist
		"""
		### list of label of all exsiting panel
		labelList = map(self.GetPageText, [i for i in range(self.GetPageCount())])
		try:
			### try to find if panel exist from label
			index = labelList.index(self.labelList[1])
		except ValueError, info:
			### index not match, panel not existing
			return None
		else:
			### return the Panel object from the finded index
			return self.GetPage(index)
	
	def GetTree(self):
		""" Get tree attribut from librairies panel
		"""
		libPanel = self.GetLibPanel()
		return libPanel.tree if libPanel else None

	def GetSearchTree(self):
		""" Get searchtree attribut from librairies panel
		"""
		libPanel = self.GetLibPanel()
		return libPanel.searchTree if libPanel else None

	def GetSearch(self):
		""" Get search attribut from librairies panel
		"""
		libPanel = self.GetLibPanel()
		return libPanel.search
	
	def update(self, concret_subject=None):
			""" Update method that manages the panel propertie depending of the selected model in the canvas
			"""

			state = concret_subject.GetState()
			canvas = state['canvas']
			model = state['model']

			propPanel = self.GetPropPanel()
			
			if propPanel:
				
				if model:
					if model != self.selected_model:
						newContent = Container.AttributeEditor(propPanel, wx.ID_ANY, model, canvas)
						propPanel.UpdatePropertiesPage(newContent)
						self.selected_model = model
						propPanel.SetToolTipString(propPanel.propToolTip[1])
				else:
					propPanel.UpdatePropertiesPage(propPanel.defaultPropertiesPage())
					self.selected_model = None
					propPanel.SetToolTipString(propPanel.propToolTip[0])
	

### ---------------------------------------------
### if flatnotebook can be imported, we work with it
### more information about FlatNotebook http://wiki.wxpython.org/Flatnotebook%20(AGW)

FLATNOTEBOOK = False

try:
	if (wx.VERSION >= (2, 8, 9, 2)):
		import wx.lib.agw.flatnotebook as fnb
	else:
		import wx.lib.flatnotebook as fnb
	FLATNOTEBOOK = True	
except:
	pass


MENU_EDIT_DELETE_PAGE = wx.NewId()

if FLATNOTEBOOK:
	#-------------------------------------------------------------------
	class LeftNotebook(fnb.FlatNotebook, GeneralNotebook):
		"""
		"""

		def __init__(self, *args, **kwargs):
			"""
			Notebook class that allows overriding and adding methods for the left pane of DEVSimPy

			@param parent: parent windows
			@param id: id
			@param pos: windows position
			@param size: windows size
			@param style: windows style
			@param name: windows name
			"""

			fnb.FlatNotebook.__init__(self, *args, **kwargs)
			GeneralNotebook.__init__(self)
			
			### FlatNotebook can be styled
			#self.SetWindowStyleFlag(fnb.FNB_VC8)
			
			self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.__OnClosingPage)
			
			self.CreateRightClickMenu()
			self.SetRightClickMenu(self._rmenu)
			
		def __OnClosingPage(self, evt):
			""" The close btutton of FlatNotebook has been invoked
				We update the Show menu depending on the deleted tab
			"""
				
			mainW = wx.GetApp().GetTopWindow()
			
			### label which will be deleted
			label = self.GetPageText(evt.GetSelection())
			
			### find the correspondig submenu in the Show menu and deselect the label
			### Show meni is in postion 2 on the Menu Bar of DEVSimPy
			show_menu = mainW.GetMenuBar().GetMenu(2)
			### Control menu is in postion 0 (first)
			control_item = show_menu.FindItemByPosition(0)
			### list of submenu for the Control menu
			items_list = control_item.GetSubMenu().GetMenuItems()
			### for all items (Simulation, Properties, Libraries)
			for item in items_list:
				### if label that will be deleted is equal to the label of current item, we deselect it
				if item.GetLabel() == label:
					item.Check(False)
		
		def __OnClosePage(self, evt):
			self.DeletePage(self.GetSelection())
			
		def CreateRightClickMenu(self):
			self._rmenu = wx.Menu()
			item = wx.MenuItem(self._rmenu, MENU_EDIT_DELETE_PAGE, _("Close Tab\tCtrl+F4"), _("Close Tab"))
			self._rmenu.AppendItem(item)
			self.Bind(wx.EVT_MENU, self.__OnClosePage, item)
			
else:
	
	#-------------------------------------------------------------------
	class LeftNotebook(wx.Notebook, GeneralNotebook):
		"""
		"""

		def __init__(self, *args, **kwargs):
			"""
			Notebook class that allows overriding and adding methods for the left pane of DEVSimPy

			@param parent: parent windows
			@param id: id
			@param pos: windows position
			@param size: windows size
			@param style: windows style
			@param name: windows name
			"""

			wx.Notebook.__init__(self, *args, **kwargs)
			GeneralNotebook.__init__(self)
			