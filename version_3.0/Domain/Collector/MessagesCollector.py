# -*- coding: utf-8 -*-

"""
Name : MessagesCollector.py 
Brief descritpion : collect to disk received messages 
Author(s) : Laurent CAPOCCHI (capocchi@univ-corse.fr)
Version :  1.0                                        
Last modified : 7/10/11
GENERAL NOTES AND REMARKS:
GLOBAL VARIABLES AND FUNCTIONS:
"""

### just for python 2.5
from __future__ import with_statement

import os
import random

#from Core.DomainInterface.DomainBehavior import DomainBehavior
import Core.DomainInterface.DomainBehavior as DomainBehavior

# ================================================================ #
class MessagesCollector(DomainBehavior.DomainBehavior):
	"""	Messages Collector
	"""

	###
	def __init__(self, fileName = os.path.join(os.getcwd(),"result%d"%random.randint(1,100)), ext = '.dat', comma = ""):
		""" Constructor.
		
			@param fileName : name of output fileName
			@param ext : output file extension
			@param comma: comma separated
		"""
		DomainBehavior.DomainBehavior.__init__(self)
		
		# local copy
		self.fileName = fileName
		self.ext = ext
		self.comma = comma
		
		#  State variable
		self.state = {'status': 'IDLE', 'sigma': INFINITY}
		
		for np in range(1000):
			fn = "%s%d%s"%(self.fileName, np, self.ext)
			if os.path.exists(fn):
				os.remove(fn)
	###
	def extTransition(self):
		"""
		"""
		for port in self.IPorts:
			np = port.myID
			msg = self.peek(port)
			if msg:
				### filename
				fn = "%s%d%s"%(self.fileName, np, self.ext)
	
				with open(fn,'a') as f: f.write("%s\n"%(str(msg)))
				del msg

		self.state["sigma"] = 0
		self.state["status"] = 'ACTIF'
		
	###
  	def intTransition(self):
		self.state["status"] = 'IDLE'
		self.state["sigma"] = INFINITY
		
	###
	def timeAdvance(self):return self.state['sigma']
	
	###
	def __str__(self):return "MessagesCollector"
