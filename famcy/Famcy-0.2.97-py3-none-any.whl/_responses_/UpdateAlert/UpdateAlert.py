import Famcy

class UpdateAlert(Famcy.FamcyResponse):
	def __init__(self, alert_type="alert-primary", alert_message="", alert_position="prepend", extra_script=None, target=None):
		super(UpdateAlert, self).__init__(target=target)

		self.alert_type = alert_type		# ("alert-primary" / "alert-secondary" / "alert-success" / "alert-danger" / "alert-warning" / "alert-info" / "alert-light" / "alert-dark")
		self.alert_message = alert_message
		self.alert_position = alert_position
		self.extra_script = extra_script

	def generate_alert(self):
		inner_text = '''
		<div class="alert %s" id="alert_msg_%s" role="alert">
			%s
		</div>
		''' % (self.alert_type, self.target.id, self.alert_message)

		extra_script = '''
		$("#alert_msg_%s").fadeTo(2000, 500).slideUp(500, function(){
			$("#alert_msg_%s").slideUp(500);
			$("#alert_msg_%s").remove();
		});
		''' % (self.target.id, self.target.id, self.target.id)

		return inner_text, extra_script

	def response(self, sijax_response):
		if self.target:
			inner_text, extra_script = self.generate_alert()

			if self.alert_position == "append":
				sijax_response.html_append('#'+self.target.id, inner_text)
			else:
				sijax_response.html_prepend('#'+self.target.id, inner_text)

			sijax_response.script(extra_script)
			sijax_response.script(self.extra_script)
			sijax_response.script(self.finish_loading_script)