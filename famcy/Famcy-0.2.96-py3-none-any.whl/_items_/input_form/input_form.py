import Famcy
import json

class input_form(Famcy.FamcyCard):
	"""
	This is a category of card
	that group all submittable
	blocks together. 
	"""
	def __init__(self, layout_mode=Famcy.FamcyLayoutMode.recommend):
		super(input_form, self).__init__(layout_mode=layout_mode)
		self.configs["method"] = "post"
		self.init_block()

	def init_block(self):
		self.body = Famcy.form()
		self.body["id"] = self.id
		self.body["method"] = self.configs["method"]
		self.body["action"] = self.action
		self.body["onsubmit"] = "return false;"

		script = Famcy.script()
		script["src"] = "/static/js/input_form_submit.js"
		self.body.addStaticScript(script)

	def render_inner(self):
			
		header_script, self.body = self.layout.render()
		if header_script not in self.header_script:
			self.header_script += header_script

		inner_script = ""
		for widget, _, _, _, _ in self.layout.content:
			if widget.clickable:
				widget.body["onclick"] = "input_form_main_btn_submit(this, %s, '%s', '%s', '%s');" % (json.dumps(widget.loader), self.id, str(self.submission_obj_key), str(widget.submission_obj_key))

		return self.body
		