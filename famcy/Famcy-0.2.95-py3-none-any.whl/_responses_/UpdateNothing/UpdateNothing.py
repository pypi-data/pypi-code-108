import Famcy

class UpdateNothing(Famcy.FamcyResponse):
	def __init__(self, target=None):
		super(UpdateNothing, self).__init__(target=target)

	def response(self, sijax_response):
		sijax_response.script(self.finish_loading_script)