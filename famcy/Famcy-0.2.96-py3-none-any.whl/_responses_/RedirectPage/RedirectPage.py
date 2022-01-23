import Famcy

class RedirectPage(Famcy.FamcyResponse):
	def __init__(self, redirect_url="", target=None):
		super(RedirectPage, self).__init__(target=target)

		self.redirect_url = redirect_url

	def response(self, sijax_response):
		sijax_response.redirect(self.redirect_url)