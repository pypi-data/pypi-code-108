import Famcy

class UpdatePrompt(Famcy.FamcyResponse):
	"""
	This is the response to update the entire page (Tab)
	Make sure self.target is a fpage
	"""
	def __init__(self, extra_script=None, target=None, upload_flag=False):
		super(UpdatePrompt, self).__init__(target=target)
		self.extra_script = extra_script
		self.upload_flag = upload_flag

	def response(self, sijax_response):
		if self.target:
			# update body html
			_ = self.target.render_inner()
			
			pure_html = self.run_all_script_tag(self.target.body.render_inner(), sijax_response) if self.upload_flag else self.target.body.render_inner()
			sijax_response.html_append('#root', '<div id="prompt_holder">' + pure_html + '</div>')
			sijax_response.script(self.extra_script)
			sijax_response.script(self.finish_loading_script)