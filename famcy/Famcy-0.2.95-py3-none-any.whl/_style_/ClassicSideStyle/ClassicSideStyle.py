import Famcy
from flask import render_template

class ClassicSideStyle(Famcy.FamcyStyle):
	def __init__(self):
		super(ClassicSideStyle, self).__init__()

		# set default value
		self.title = ""
		self.desc = ""
		self.font_theme = Famcy.FamcyFontTheme()
		self.loader = Famcy.FamcyStyleLoader()
		self.color_theme = Famcy.FamcyColorTheme()
		self.side_bar = Famcy.FamcyStyleSideBtns()

	def setHeadScript(self, title=None, desc=None):
		if title:
			self.title = title
		if desc:
			self.desc = desc

	def render(self, extra_script, content, background_flag=False, route="", time=5000, form_init_js=None, end_script="", **kwargs):

		html_header = self.setDashboardHTMLHeader()
		end_js = self.setDashboardJavaScript()+end_script
		color_theme = self.color_theme.render()
		font_theme = self.font_theme.render()
		load_spinner = self.loader.render()
		side_bar = self.side_bar.render()

		body_on_load = "background_loop('" + self.main_url + str(route) + "/bgloop" + "', '" + str(route) + "', " + str(time) + ");console.log('start!')" if background_flag else ""
		return render_template("no_nav_bar.html", font_theme=font_theme, form_init_js=form_init_js, load_spinner=load_spinner, color_theme=color_theme, html_header=html_header, side_bar=side_bar, content=content, extra_script=extra_script, end_js=end_js, body_on_load=body_on_load)