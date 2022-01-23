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
from openexp.keyboard import Keyboard

from libopensesame import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from libopensesame.oslogging import oslogger

import os
import sys
import time

from pyEVT import EvtExchanger


class RGB_Led_Control(item.item):

	"""
		This class (the class with the same name as the module)
		handles the basic functionality of the item. It does
		not deal with GUI stuff.
	"""


	description = u"Sets and/or sends RGB led data from\r\n" \
			"EventExchanger-based digital input/output device."

	def reset(self):

		# Set the default values of the plug-in items in the GUI.
		self.var._productName		 = u'DUMMY'
		self.var._correctButton		 = u'1'
		self.var._allowedButtons	 = u'1;2;3'
		self.var._responseTimeout	 = u'infinite'

		self.var._button1_Led_Color    = "#000000"
		self.var._button2_Led_Color    = "#000000"
		self.var._button3_Led_Color    = "#000000"
		self.var._button4_Led_Color    = "#000000"

		self.var._resetAfter 				  = 500;
		self.var._feedback 					  = u'yes'
		self.var._correctColor  			  = "#00FF00"
		self.var._inCorrectColor  			  = "#FF0000"
		
	def prepare(self):
		item.item.prepare(self)
		self.EE = EvtExchanger()
		Device = self.EE.Select(self.var._productName)
		
		try:
			if Device is None:
				raise
		except:
			self.var._productName = u'DUMMY'
			self.Keyboard = Keyboard(self.experiment);
			if not type(self.var._responseTimeout) == int:
				self.var._responseTimeout = None
			oslogger.info("Cannot find ResponseBox: Using Keyboard instead")


		if not type(self.var._responseTimeout) == int:
			self.var._responseTimeout = -1
		# Recode Allowed buttons to AllowedEventLines
		self.var.AllowedEventLines = 0
		try:
			AllowedList = self.var._allowedButtons.split(";")
			for x in AllowedList:
				self.var.AllowedEventLines +=  (1 << (int(x,10) -1))
		except:
			x = self.var._allowedButtons
			self.var.AllowedEventLines =  (1 << (x-1))


	def run(self):
		
		# Save the current time ...
		t0 = self.set_item_onset()

		hexprepend = "0x"
		self.colors = [hexprepend + self.var._button1_Led_Color[1:], \
							hexprepend + self.var._button2_Led_Color[1:], \
							hexprepend + self.var._button3_Led_Color[1:], \
							hexprepend + self.var._button4_Led_Color[1:]]
		
		self.CorrectColor = hexprepend + self.var._correctColor[1:]
		self.InCorrectColor = hexprepend + self.var._inCorrectColor[1:]
		CC=int(self.CorrectColor,16)
		IC=int(self.InCorrectColor,16)
		oslogger.info(self.colors)
		BLC = [0,0,0,0]
		for b in range(4):
			BLC[b] = int(self.colors[b] , 16)			
		
		if self.var._productName != u'DUMMY':
			for b in range(4):
				self.EE.SetLedColor( \
					((BLC[b] >> 16) & 0xFF), \
					((BLC[b] >> 8) & 0xFF), \
					(BLC[b] & 0xFF), \
					b+1, 1)
		
			if self.var._feedback == u'yes':
				for b in range(4):
					self.EE.SetLedColor( \
						((IC >> 16) & 0xFF), \
						((IC >> 8) & 0xFF), \
						(IC & 0xFF), \
						b+1, b+11)
		
				self.EE.SetLedColor( \
					((CC >> 16) & 0xFF), \
					((CC >> 8) & 0xFF), \
					(CC & 0xFF), \
					int(self.var._correctButton), int(self.var._correctButton)+10)
		
			# Call the 'wait for event' function in the EventExchanger C# object.

			(self.var.Response,self.var.RT) = \
				(self.EE.WaitForDigEvents(self.var.AllowedEventLines,
							self.var._responseTimeout)) 
			self.var.Response += 1

			#FEEDBACK:
			if self.var._feedback == u'yes':
				time.sleep(self.var._resetAfter/1000.0)
				for b in range(4):
					self.EE.SetLedColor(0,0,0,b+1,1)
		else:
			# demo mode: keyboard response.....
			if self.var._responseTimeout==-1:
				self.var._responseTimeout = None
			self.var.Response, self.var.RT= self.Keyboard.get_key(timeout=self.var._responseTimeout)

		#HOUSEHOLD:
		self.CorrectResponse = \
			(self.var.Response == self.var._correctButton)
		# Add all response related data to the Opensesame responses instance.
		self.experiment.responses.add(response_time=self.var.RT, \
								correct=self.CorrectResponse, \
								response=self.var.Response, \
								item=self.name)
		#Report success		
		return True

class qtRGB_Led_Control(RGB_Led_Control, qtautoplugin):
	def __init__(self, name, experiment, string = None):

		#Pass the word on to the parents
		RGB_Led_Control.__init__(self, name, experiment, string)
		qtautoplugin.__init__(self, __file__)


	def init_edit_widget(self):

	# Pass the word on to the parent
		qtautoplugin.init_edit_widget(self)


		EE = EvtExchanger()
		listofdevices = EE.Attached()
		for i in listofdevices:
			self.ProductName_widget.addItem(i)
			