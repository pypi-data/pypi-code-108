"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame import item
from libopensesame.oslogging import oslogger
from libqtopensesame.items.qtautoplugin import qtautoplugin
from libopensesame.py3compat import *
import os
import sys

from pyEVT import EvtExchanger

class EVTxx(item.item):

	"""
		This class (the class with the same name as the module)
		handles the basic functionality of the item. It does
		not deal with GUI stuff.
	"""


	description = u"Allows setting or pulsing values of pins on the "  \
					"output port of various EventExchanger devices"

	def reset(self):
		self.var._value = 0
		self.var._duration = 500
		self.var._productName = u'DUMMY'
		self.var._outputMode = u'Pulse Output Lines'

	def prepare(self):
		item.item.prepare(self)
		self.EE = EvtExchanger()
		Device = self.EE.Select(self.var._productName)
		
		try:
			if Device is None:
				raise
		except:
			self.var._productName = u'DUMMY'
			oslogger.info("Cannot find eventexchanger: code to debugwindow")

						
	def run(self):
		self.set_item_onset()
		#self.EE.Select(self.PATH)
		if 	self.var._productName == u'DUMMY':
			oslogger.info('dummy code: {} for {} ms'.format(self.var._value, self.var._duration) )
		else:
			if self.var._outputMode == u'Set Output Lines':
				self.EE.SetLines(self.var._value)
			elif self.var._outputMode == u'Pulse Output Lines':
				# make sure that the code starts at, and returns to zero.
				self.EE.SetLines(0)
				self.EE.PulseLines(self.var._value, self.var._duration)
		
		return True

class qtEVTxx(EVTxx, qtautoplugin):
	def __init__(self, name, experiment, string = None):

		#Pass the word on to the parents
		EVTxx.__init__(self, name, experiment, string)
		qtautoplugin.__init__(self, __file__)

	def init_edit_widget(self):
	# Pass the word on to the parent
		qtautoplugin.init_edit_widget(self)

		EE = EvtExchanger()
		listofdevices = EE.Attached()
		for i in listofdevices:
			if "SHOCKER" not in i:
				self.ProductName_widget.addItem(i)
