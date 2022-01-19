from jocular.device import Device
from kivy.properties import StringProperty

class GenericCamera(Device):

	family = StringProperty('Camera')

	def on_new_object(self):
		self.last_capture = None

	def on_previous_object(self):
		self.last_capture = None

	def reset(self):
		self.last_capture = None

	def capture(self, **kwargs):
		return None

	def stop_capture(self):
		pass

	def get_image(self):
		if hasattr(self, 'last_capture'):
			return self.last_capture
		return None

	def get_capture_props(self):
		''' Overridden if cam has props that might be useful to caller
			e.g. to write into the FITs header
		'''
		return None
