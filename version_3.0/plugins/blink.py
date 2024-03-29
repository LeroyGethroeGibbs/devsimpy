# -*- coding: utf-8 -*-

""" 
	Authors: L. Capocchi (capocchi@univ-corse.fr), C. Nicolai
	Date: 21/10/2010
	Description:
		Atomic models blink when there external or internal function are invocked.
		Moreover, this plugins allows you the step by step simulation.
		Warning: the module is enabled when the run button is pressed.
	Depends: Nothing
"""

import os
from types import MethodType

import wx
import Core.Utilities.pluginmanager as pluginmanager
import Core.Utilities.Utilities as Utilities
import Core.Components.Container as Container

import GUI.FindGUI as FindGUI

import Core.Patterns.Observer as Observer
import GUI.DetachedFrame as DetachedFrame


def InternalLog(model):
	txt = ["\n\tINTERNAL TRANSITION: %s (%s)\n" % (model.__class__.__name__, model.myID),
		   "\t  New State: %s\n" % model.state,
		   "\t  Output Port Configuration:\n"]

	for m in model.OPorts:
		if m in model.myOutput.keys():
			txt.append("\t    %s: %s\n" % (m, model.myOutput[m]))
		else:
			txt.append("\t    %s: None\n" % m)

	if model.myTimeAdvance == INFINITY:
		txt.append("\t  Next scheduled internal transition at INFINITY\n")
	else:
		txt.append("\t  Next scheduled internal transition at %f\n" % model.myTimeAdvance)

	return ''.join(txt)


def ExternalLog(model):
	txt = ["\n\tEXTERNAL TRANSITION: %s (%s)\n" % (model.__class__.__name__, model.myID),
		   "\t  New State: %s\n" % model.state,
		   "\t  Input Port Configuration:\n"]

	txt.extend(["\t    %s: %s\n" % (m, model.peek(m)) for m in model.IPorts])

	if model.myTimeAdvance == INFINITY:
		txt.append("\t  Next scheduled internal transition at INFINITY\n")
	else:
		txt.append("\t  Next scheduled internal transition at %f\n" % model.myTimeAdvance)

	return ''.join(txt)


def TimeAdvanceLog(model):
	txt = "\n\tTA CHECKING for %s (%s) : %f\n" % (model.__class__.__name__, model.myID, model.myTimeAdvance)
	return txt


def GetState(self):
	return self.__state

#def extTransition(self):
#AtomicDEVS.extTransition(self)
#pluginmanager.trigger_event("SIM_BLINK", model = self, msg = 0)

#def intTransition(self):
#AtomicDEVS.intTransition(self)
#pluginmanager.trigger_event("SIM_BLINK", model = self, msg = 1)

#def timeAdvance(self):
#AtomicDEVS.timeAdvance(self)
#pluginmanager.trigger_event("SIM_BLINK", model = self, msg = 2)

#def extends_model_for_blink(L):
#for m in L:
#if isinstance(m, AtomicDEVS):
#m.extTransition = MethodType(extTransition,m)
#m.intTransition = MethodType(intTransition,m)
#m.timeAdvance = MethodType(timeAdvance,m)
#elif isinstance(m, CoupledDEVS):
#extends_model_for_blink(m.componentSet)

@pluginmanager.register("START_BLINK")
def start_blink(*args, **kwargs):
	global frame
	global sender

	parent = kwargs['parent']
	master = kwargs['master']

	mainW = wx.GetApp().GetTopWindow()
	nb = mainW.nb2
	actuel = nb.GetSelection()
	diagram = nb.GetPage(actuel).diagram

	frame = BlinkFrame(parent, wx.ID_ANY, _('Blink Logger'))
	frame.SetIcon(mainW.icon)
	frame.SetTitle("%s Blink Logger" % os.path.basename(diagram.last_name_saved))
	frame.Show()

	sender = Observer.Subject()
	sender.__state = {}
	sender.canvas = None
	sender.GetState = MethodType(GetState, sender)

	#extends_model_for_blink(master.componentSet)

	### disable suspend and log button
	parent._btn3.Disable()
	parent._btn4.Disable()


@pluginmanager.register("SIM_BLINK")
def blink_manager(*args, **kwargs):
	""" Start blink.
	"""

	global frame
	global sender

	d = kwargs['model']
	msg = kwargs['msg']

	### if frame is deleted (occur for dynamic coupled model)
	if not isinstance(frame, wx.Frame):
		return

	### DEVSimPy block
	if hasattr(d, 'getBlockModel'):

		block = d.getBlockModel()

		main = wx.GetApp().GetTopWindow()
		nb2 = main.nb2
		child = main.GetChildren()

		canvas = None

		### find CodeBlock in the nb2
		for can in nb2.pages:
			if block in filter(lambda a: not isinstance(a, Container.ConnectionShape), can.diagram.shapes):
				canvas = can
				break

		### find CodeBlock in detached_frame
		if canvas is None:
			for detached_frame in filter(
					lambda child: isinstance(child, DetachedFrame.DetachedFrame) and hasattr(child, 'canvas'), child):
				can = detached_frame.canvas
				if block in filter(lambda a: not isinstance(a, Container.ConnectionShape), can.diagram.shapes):
					canvas = can
					break

		sender.canvas = canvas

		if canvas is not None and isinstance(frame, wx.Frame):

			#### add model d to observer list
			sender.attach(block)

			old_fill = block.fill

			### write external transition result
			if type(msg[0]) == type({}):
			#if msg == 0:
				color = ["#e90006"]
				dastyle = wx.TextAttr()
				dastyle.SetTextColour("#e90006")
				frame.txt.SetDefaultStyle(dastyle)
				wx.CallAfter(frame.txt.write, (ExternalLog(d)))

			### write ta checking result
			elif msg[0] == 0:
			#elif msg == 2:
				color = ["#0c00ff"]
				dastyle = wx.TextAttr()
				dastyle.SetTextColour("#0c00ff")
				frame.txt.SetDefaultStyle(dastyle)
				wx.CallAfter(frame.txt.write, (TimeAdvanceLog(d)))

			### write internal transition result
			elif msg[0] == 1:
			#elif msg == 1:
				color = ["#2E8B57"]
				dastyle = wx.TextAttr()
				dastyle.SetTextColour("#2E8B57")
				frame.txt.SetDefaultStyle(dastyle)
				wx.CallAfter(frame.txt.write, (InternalLog(d)))

			else:
				color = old_fill

			state = sender.GetState()
			state['fill'] = color
			sender.notify()

			try:
			### step engine
				frame.flag = False
				while not frame.flag:
					pass
			except:
				pass


			### update color
			state['fill'] = old_fill
			sender.notify()

			### add model d to observer list
			sender.detach(block)

	else:
		wx.CallAfter(frame.txt.write, (_("No blink for %s dynamic model (%s)!\n") % (str(d), d.myID)))


def Config(parent):
	""" Plugin settings frame.
	"""
	dlg = wx.MessageDialog(parent, _('No settings available for this plugin\n'), _('Exclamation'),
						   wx.OK | wx.ICON_EXCLAMATION)
	dlg.ShowModal()


class BlinkFrame(wx.Frame):
	"""
	"""

	def __init__(self, *args, **kwds):
		""" Constructor.
		"""

		kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
		kwds["size"] = (400, 420)

		wx.Frame.__init__(self, *args, **kwds)

		self.panel = wx.Panel(self, wx.ID_ANY)
		self.button_clear = wx.Button(self.panel, wx.ID_CLEAR)
		self.button_step = wx.Button(self.panel, wx.ID_FORWARD)
		self.button_find = wx.Button(self.panel, wx.ID_FIND)
		self.button_selectall = wx.Button(self.panel, wx.ID_SELECTALL)
		self.txt = wx.TextCtrl(self.panel, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY)

		Utilities.MoveFromParent(self, interval=10, direction='right')

		self.__set_properties()
		self.__do_layout()

		### just for the start of the frame
		self.flag = True

		### to close the frame when this attribute dont change
		self.lenght = self.txt.GetNumberOfLines()

		### just for window
		self.SetClientSize(self.panel.GetBestSize())

		self.Bind(wx.EVT_BUTTON, self.OnStep, id=self.button_step.GetId())
		self.Bind(wx.EVT_BUTTON, self.OnClear, id=self.button_clear.GetId())
		self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=self.button_selectall.GetId())
		self.Bind(wx.EVT_BUTTON, self.OnFindReplace, id=self.button_find.GetId())

	def __set_properties(self):
		self.txt.SetMinSize((390, 300))
		self.button_step.SetToolTipString(_("Press this button in order to go step by step in the simulation."))
		self.button_clear.SetToolTipString(_("Press this button in order to clean the output of the simulation."))
		self.button_find.SetToolTipString(_("Press this button in order to lauch the search window."))
		self.button_step.SetDefault()

	def __do_layout(self):

		sizer_2 = wx.BoxSizer(wx.VERTICAL)
		sizer_2.Add(self.txt, 1, wx.EXPAND)

		grid_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		grid_sizer_1.Add(self.button_selectall, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE)
		grid_sizer_1.Add(self.button_find, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE)
		grid_sizer_1.Add(self.button_clear, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE)

		sizer_2.Add(grid_sizer_1, 0, wx.EXPAND)

		sizer_2.Add(self.button_step, 0, wx.ALIGN_RIGHT)

		self.panel.SetSizerAndFit(sizer_2)

	def OnStep(self, evt):
		"""
		"""
		nb = self.txt.GetNumberOfLines()
		parent = self.GetParent()
		### si plus de sortie text dans le Logger, alors on ferme la fentre et on stop la simulation
		if nb != self.lenght:
			self.lenght = nb
		else:
			self.Close()
			parent.OnStop(evt)
		self.flag = True
		self.button_clear.Enable(True)

	def OnClear(self, evt):
		""" Clear selection or all text
		"""
		s = self.txt.GetSelection()
		self.txt.Remove(s[0], s[1])

	def OnSelectAll(self, evt):
		"""
		"""
		self.txt.SelectAll()

	def OnFindReplace(self, evt):
		FindGUI.FindReplace(self, wx.ID_ANY, _('Find/Replace'))
