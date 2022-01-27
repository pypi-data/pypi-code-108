import Famcy

class RedirectPageTab(Famcy.FamcyResponse):
	def __init__(self, redirect_tab="", target=None):
		super(RedirectPageTab, self).__init__(target=target)

		self.redirect_tab = redirect_tab

	def response(self, sijax_response):
		sijax_response.redirect(url_for("main.generate_tab_page", tab=self.redirect_tab))