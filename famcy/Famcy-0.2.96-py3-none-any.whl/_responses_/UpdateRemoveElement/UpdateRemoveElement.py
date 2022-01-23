import Famcy

class UpdateRemoveElement(Famcy.FamcyResponse):
	"""
	This is the response to update the entire page (Tab)
	Make sure self.target is a fpage
	"""
	def __init__(self, prompt_flag=False, extra_script=None, target=None):
		super(UpdateRemoveElement, self).__init__(target=target)
		self.extra_script = extra_script
		self.prompt_flag = prompt_flag

	def response(self, sijax_response):
		if self.target:
			target_id = "prompt_holder" if self.prompt_flag else self.target.id
			sijax_response.remove('#' + target_id)
			sijax_response.script(self.extra_script)
			sijax_response.script(self.finish_loading_script)