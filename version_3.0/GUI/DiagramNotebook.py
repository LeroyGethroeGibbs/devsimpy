#!/usr/bin/env python
# -*- coding: utf-8 -*-

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# main.py --- DEVSimPy - The Python DEVS GUI modeling and simulation software 
#                     --------------------------------
#                            Copyright (c) 2013
#                              Laurent CAPOCCHI
#                        SPE - University of Corsica
#                     --------------------------------
# Version 3.0                                      last modified:  08/01/13
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#
# GENERAL NOTES AND REMARKS:
#
#
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#
# GLOBAL VARIABLES AND FUNCTIONS
#
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

import os
import sys
import __builtin__

import wx

import Core.Components.Container as Container
import GUI.ShapeCanvas as ShapeCanvas
import GUI.Menu as Menu
import Mixins.Printable as Printable
import GUI.DetachedFrame as DetachedFrame



# to send event
if wx.VERSION_STRING < '2.9':
	from wx.lib.pubsub import Publisher as pub
else:
	from wx.lib.pubsub import pub

#-------------------------------------------------------------------
class DiagramNotebook(wx.Notebook, Printable.Printable):
	"""
	"""

	def __init__(self, *args, **kwargs):
		"""
		Notebook class that allows overriding and adding methods.

		@param parent: parent windows
		@param id: id
		@param pos: windows position
		@param size: windows size
		@param style: windows style
		@param name: windows name
		"""

		# for spash screen
		pub.sendMessage('object.added', 'Loading notebook diagram...\n')

		wx.Notebook.__init__(self, *args, **kwargs)
		Printable.Printable.__init__(self)

		# local copy
		self.parent = args[0]
		self.pages = []            # keeps track of pages

		#icon under tab
		imgList = wx.ImageList(16, 16)
		for img in [os.path.join(ICON_PATH_16_16, 'network.png')]:
			imgList.Add(wx.Image(img, wx.BITMAP_TYPE_PNG).ConvertToBitmap())
		self.AssignImageList(imgList)

		### binding
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.__PageChanged)
		self.Bind(wx.EVT_RIGHT_DOWN, self.__ShowMenu)
		self.Bind(wx.EVT_LEFT_DCLICK, self.__AddPage)

	def GetPages(self):
		return self.pages

	def __AddPage(self, event):
		self.AddEditPage(_("Diagram%d") % len(self.pages))

	def AddEditPage(self, title, defaultDiagram=None):
		"""
		Adds a new page for editing to the notebook and keeps track of it.
		
		@type title: string
		@param title: Title for a new page
		"""

		### title page list
		title_pages = map(lambda p: p.name, self.pages)

		### occurence of title in existing title pages
		c = title_pages.count(title)

		title = title + "(%d)" % c if c != 0 else title

		### new page
		newPage = ShapeCanvas.ShapeCanvas(self, wx.NewId(), name=title)

		### new diagram
		d = defaultDiagram or Container.Diagram()
		d.SetParent(newPage)

		### diagram and background newpage setting
		newPage.SetDiagram(d)

		### print canvas variable setting
		self.print_canvas = newPage
		self.print_size = self.GetSize()

		self.pages.append(newPage)
		self.AddPage(newPage, title, imageId=0)
		self.SetSelection(self.GetPageCount() - 1)

	def GetPageByName(self, name=''):
		"""
		"""
		for i in xrange(len(self.pages)):
			if name == self.GetPageText(i):
				return self.GetPage(i)
		return None

	def __PageChanged(self, evt):
		"""
		"""

		try:
			canvas = self.GetPage(self.GetSelection())
			self.print_canvas = canvas
			self.print_size = self.GetSize()

			### permet d'activer les redo et undo pour chaque page
			self.parent.tb.EnableTool(wx.ID_UNDO, not len(canvas.stockUndo) == 0)
			self.parent.tb.EnableTool(wx.ID_REDO, not len(canvas.stockRedo) == 0)

			canvas.deselect()
			canvas.Refresh()

		except Exception:
			pass
		evt.Skip()

	def __ShowMenu(self, evt):
		"""	Callback for the right click on a tab. Displays the menu.
		
			@type   evt: event
			@param  evt: Event Objet, None by default
		"""

		### mouse position
		pos = evt.GetPosition()
		### pointed page and flag
		page, flag = self.HitTest(pos)

		### if no where click
		if flag == wx.BK_HITTEST_NOWHERE:
			self.PopupMenu(Menu.DiagramNoTabPopupMenu(self), pos)
		### if tab has been clicked
		elif flag == wx.BK_HITTEST_ONLABEL:
			self.PopupMenu(Menu.DiagramTabPopupMenu(self), pos)
		else:
			pass

	def OnClearPage(self, evt):
		""" Clear page.

			@type evt: event
			@param  evt: Event Objet, None by default
		"""
		if self.GetPageCount() > 0:
			canvas = self.GetPage(self.GetSelection())
			diagram = canvas.diagram

			diagram.DeleteAllShapes()
			diagram.modified = True

			canvas.deselect()
			canvas.Refresh()

	def OnClosePage(self, evt):
		""" Close current page.
		
			@type evt: event
			@param  evt: Event Objet, None by default
		"""

		if self.GetPageCount() > 0:

			id = self.GetSelection()
			title = self.GetPageText(id)
			canvas = self.GetPage(id)
			diagram = canvas.GetDiagram()

			mainW = self.GetTopLevelParent()

			if diagram.modify:
				dlg = wx.MessageDialog(self, _('%s\nSave changes to the current diagram ?') % title, _('Save'), wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
				val = dlg.ShowModal()
				if val == wx.ID_YES:
					mainW.OnSaveFile(evt)
				elif val == wx.ID_NO:
					self.DeleteBuiltinConstants()
					self.pages.remove(canvas)
					if not self.DeletePage(id):
						sys.stdout.write(_(" %s not deleted ! \n" % title))
				else:
					dlg.Destroy()
					return False

				dlg.Destroy()

			else:

				self.DeleteBuiltinConstants()
				self.pages.remove(canvas)

				if not self.DeletePage(id):
					sys.stdout.write(_("%s not deleted ! \n" % title))

			### effacement du notebook "property"
			nb1 = mainW.nb1
			activePage = nb1.GetSelection()
			### si la page active est celle de "properties" alors la met a jour et on reste dessus
			if activePage == 1:
				nb1.UpdatePropertiesPage(nb1.defaultPropertiesPage())

			return True

	def OnRenamePage(self, evt):
		"""Rename the title of notebook page.

		@type evt: event
		@param  evt: Event Objet, None by default
		"""
		selection = self.GetSelection()
		dlg = wx.TextEntryDialog(self, _("Enter a new name:"), _("Diagram Manager"))
		dlg.SetValue(self.GetPageText(selection))

		if dlg.ShowModal() == wx.ID_OK:
			txt = dlg.GetValue()
			self.SetPageText(selection, txt)

		dlg.Destroy()

	def OnDetachPage(self, evt):
		""" 
		Detach the notebook page on frame.
		
		@type evt: event
		@param  evt: Event Objet, None by default
		"""

		mainW = self.GetTopLevelParent()
		selection = self.GetSelection()
		canvas = self.GetPage(selection)
		title = self.GetPageText(selection)

		frame = DetachedFrame.DetachedFrame(canvas, wx.ID_ANY, title, canvas.GetDiagram())
		frame.SetIcon(mainW.icon)
		frame.SetFocus()
		frame.Show()

	def DeleteBuiltinConstants(self):
		""" Delete builtin constants for the diagram.
		"""
		try:
			name = self.GetPageText(self.GetSelection())
			del __builtin__.__dict__[str(os.path.splitext(name)[0])]
		except Exception:
			pass
		#print "Constants builtin not delete for %s : %s"%(name, info)

