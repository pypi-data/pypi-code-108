import Famcy
import os
import enum
from flask import render_template
# from dashboard_utils import *

class FStyleMode(enum.IntEnum):
	default = 0
	login = 1
	videoStream = 2

class FStyle:
	def __init__(self, styleName=FStyleMode.default, with_login=None):
		self.styleDict = {FStyleMode.default: Famcy.ClassicStyle, FStyleMode.login: Famcy.LoginStyle, FStyleMode.videoStream: Famcy.VideoStreamStyle}
		self._FamcyStyle = self.styleDict[styleName]
		self.withLogin = with_login if with_login else Famcy.FManager["ConsoleConfig"]["with_login"]

		# default url
		self.main_url = Famcy.FManager["ConsoleConfig"]["main_url"]

		self._check_rep()

	def _check_rep(self):
		"""
		Rep Invariant
		"""
		pass

	def setLogin(self, with_login):
		self.withLogin = with_login

	def setDashboardHTMLHeader(self):
		"""
		Return the html header for the dashboard
		"""
		return """<meta charset="utf-8"/>
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<meta name="theme-color" content="#000000" />
		<meta
		  name="description"
		  content="%s"
		/>
		<title>%s</title>

		<link href="%s/static/css/index.css" rel="stylesheet" media="screen">
		<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
		<script src="%s/static/js/cookie_utils.js"></script>%s""" % (self.desc, self.title, self.main_url, self.main_url, self.uploadFileHeader())

	def uploadFileHeader(self):
		return"""
		<!--upload-->
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/css/bootstrap.min.css" crossorigin="anonymous">
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.min.css" crossorigin="anonymous">
		
		<!--event calendar-->
		<link href='%s/static/css/fullcalendar.css' rel='stylesheet' />
		<link href='%s/static/css/fullcalendar.print.css' rel='stylesheet' media='print' />
		<script src='%s/static/js/jquery-1.10.2.js' type="text/javascript"></script>
		<script src='%s/static/js/jquery-ui.custom.min.js' type="text/javascript"></script>
		<script src='%s/static/js/fullcalendar_zh.js' type="text/javascript"></script>

		<!--side bar-->
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/boxicons@2.0.8/css/boxicons.min.css"></link>

		<!--input password-->
		<script type="text/javascript" src="%s/static/js/password_strength_lightweight.js"></script>
		<link rel="stylesheet" type="text/css" href="%s/static/css/password_strength.css">

		<!--input form-->
		<script src='%s/static/js/before_input_submit.js' type="text/javascript"></script>

		<!--input list-->
		<script src="%s/static/js/input_list.js"></script>

		<!--generate loader-->
		<script src="%s/static/js/generate_loader.js"></script>

		<!--fblock extra function-->
		<script src="%s/static/js/fblock_extra_func.js"></script>
		<script src="%s/asset/js/fblock_cus_func.js"></script>

		<!--background loop-->
		<script src="%s/static/js/background_loop.js"></script>

		""" % tuple([self.main_url for _ in range(13)])

	def setDashboardJavaScript(self):
		return"""
		<!--table-->
		<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"></script>
		<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
		<script src="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.js"></script>
		"""
	
	def render(self, extra_script, content, page_id="", background_flag=False):
		return self._FamcyStyle.render(extra_script, content, page_id=page_id, background_flag=False)

class FStyleNavBar(FStyle):
	def __init__(self):
		super(FStyleNavBar, self).__init__()
		self.userName = "admin"
		self.userImg = os.path.join("", "static", "image/login.png")

	def setNavBarInfo(self, user_name=None, user_img_path=None):
		if user_name:
			self.userName = user_name
		if user_img_path:
			self.userImg = user_img_path

	def setDashboardNavBar(self):
		if self.withLogin:
			login_class = ""
		else:
			login_class = "display_none"

		return"""<div class="nav_bar">
			<div class="header_toggle">
				<i class='bx bx-menu' id="header-toggle"></i>
			</div>
			<button class="member_section %s" onclick="window.location.href='/dashboard/profile'">
				<img src="%s" id="user_icon">
				<h3 id="user_name">%s</h3>
			</button>
		</div>
		<script src='%s/static/js/side_bar.js' type="text/javascript"></script>""" % (login_class, self.userImg, self.userName, self.main_url)


	def render(self):
		return self.setDashboardNavBar()

class FStyleSideBar(FStyle):
	def __init__(self):
		super(FStyleSideBar, self).__init__()
		self.side_bar_title_href = Famcy.FManager["ConsoleConfig"]["main_page"]
		self.side_bar_title = Famcy.FManager["ConsoleConfig"]["side_bar_title"]
		self.side_bar_hierarchy = Famcy.FManager["ConsoleConfig"]["side_bar_hierachy"]
		self.title_style = Famcy.FManager["ConsoleConfig"]["title_style"] if "title_style" in Famcy.FManager["ConsoleConfig"].keys() else {}
		self.side_bar_style = Famcy.FManager["ConsoleConfig"]["side_bar_style"] if "side_bar_style" in Famcy.FManager["ConsoleConfig"].keys() else {}

	def setSideBarInfo(self, side_bar_title=None, side_bar_hierarchy=None, title_style=None, side_bar_style=None):
		if side_bar_title:
			self.side_bar_title = side_bar_title
		if side_bar_hierarchy:
			self.side_bar_hierarchy = side_bar_hierarchy
		if title_style:
			self.title_style = title_style
		if side_bar_style:
			self.side_bar_style = side_bar_style

	def setDashboardSideBar(self):
		"""
		icon library (version 2.0.8) => https://boxicons.com/
		list with key -> path
		side_bar_hierarchy = [
			{"main_title1": "maintitle1/a"},
			{"main_title2": [
				{"sub_title21": "maintitle2/a"}, 
				{"sub_title22": "maintitle2/b"}
			]}
		]
		title_style = "bx-grid-alt"
		side_bar_style = {"main_title1": "bxl-docker", "main_title2": "bxl-python"}
		"""
		if self.withLogin:
			login_class = ""
		else:
			login_class = "display_none"

		defalut_icon = "bx-grid-alt"
		list_of_icon = list(self.side_bar_style.keys())

		return_html = ''
		btn_html = ''
		for top_level in self.side_bar_hierarchy:
			icon = defalut_icon
			main_title = list(top_level.keys())[0]

			if main_title in list_of_icon:
				icon = self.side_bar_style[main_title]

			if not isinstance(top_level[main_title], list):
				btn_html += '<div><a href="' + top_level[main_title] + '" class="nav_link toggle_class display_flex"><i class="bx ' + icon + ' nav_icon"></i><span class="nav_name">' + main_title + '</span></a></div>'

			else:
				sub_btn_html = ''
				for sub_level in top_level[main_title]:
					sub_title = list(sub_level.keys())[0]
					sub_icon = defalut_icon
					if sub_title in list_of_icon:
						sub_icon = self.side_bar_style[sub_title]
					sub_btn_html += '<a href="' + sub_level[sub_title] + '" class="nav_link toggle_class display_flex"><i class="bx ' + sub_icon + ' nav_icon"></i><span class="nav_name">' + sub_title + '</span></a>'
				btn_html += '<div><div onclick="btnClickedFunc(this)" class="nav_link toggle_class display_flex"><i class="bx ' + icon + ' nav_icon"></i><span class="nav_name">' + main_title + '</span></div><div class="sub_title">' + sub_btn_html + '</div></div>'


		return"""<div id="side-bar">
		<div class="l-navbar" id="nav-bar">
			<div class="nav">
				<div>
					<a href="%s" class="nav_logo toggle_class display_flex">
						<i class='bx %s nav_logo-icon'></i>
						<span class="nav_logo-name nav_name">%s</span>
					</a>
					<div class="nav_list">%s</div>
				</div>
				<a href="logout" class="nav_link toggle_class display_flex %s">
					<i class='bx bx-log-out nav_icon'></i>
					<span class="nav_name">登出</span>
				</a>
			</div>
		</div>
		</div>""" % (self.side_bar_title_href, self.title_style, self.side_bar_title, btn_html, login_class)

	def render(self):
		return self.setDashboardSideBar()


class FStyleSideBtns(FStyle):
	def __init__(self):
		super(FStyleSideBtns, self).__init__()
		self.side_bar_title_href = Famcy.FManager["ConsoleConfig"]["main_page"]
		self.side_bar_title = Famcy.FManager["ConsoleConfig"]["side_bar_title"]
		self.side_bar_hierarchy = Famcy.FManager["ConsoleConfig"]["side_bar_hierachy"]
		self.title_style = Famcy.FManager["ConsoleConfig"]["title_style"] if "title_style" in Famcy.FManager["ConsoleConfig"].keys() else {}
		self.side_bar_style = Famcy.FManager["ConsoleConfig"]["side_bar_style"] if "side_bar_style" in Famcy.FManager["ConsoleConfig"].keys() else {}

	def setSideBtnsInfo(self, side_bar_title=None, side_bar_hierarchy=None, title_style=None, side_bar_style=None):
		if side_bar_title:
			self.side_bar_title = side_bar_title
		if side_bar_hierarchy:
			self.side_bar_hierarchy = side_bar_hierarchy
		if title_style:
			self.title_style = title_style
		if side_bar_style:
			self.side_bar_style = side_bar_style

	def setDashboardSideBtns(self):
		"""
		icon library (version 2.0.8) => https://boxicons.com/
		list with key -> path
		side_bar_hierarchy = [
			{"main_title1": "maintitle1/a"},
			{"main_title2": [
				{"sub_title21": "maintitle2/a"}, 
				{"sub_title22": "maintitle2/b"}
			]}
		]
		title_style = "bx-grid-alt"
		side_bar_style = {"main_title1": "bxl-docker", "main_title2": "bxl-python"}
		"""
		if self.withLogin:
			login_class = ""
		else:
			login_class = "display_none"

		defalut_icon = "bx-grid-alt"
		list_of_icon = list(self.side_bar_style.keys())

		return_html = ''
		btn_html = ''
		for top_level in self.side_bar_hierarchy:
			icon = defalut_icon
			main_title = list(top_level.keys())[0]

			if main_title in list_of_icon:
				icon = self.side_bar_style[main_title]

			if not isinstance(top_level[main_title], list):
				btn_html += '<div><a href="' + top_level[main_title] + '" class="nav_link toggle_class display_flex"><i class="bx ' + icon + ' nav_icon"></i><span class="nav_name">' + main_title + '</span></a></div>'

			else:
				sub_btn_html = ''
				for sub_level in top_level[main_title]:
					sub_title = list(sub_level.keys())[0]
					sub_icon = defalut_icon
					if sub_title in list_of_icon:
						sub_icon = self.side_bar_style[sub_title]
					sub_btn_html += '<a href="' + sub_level[sub_title] + '" class="nav_link toggle_class display_flex"><i class="bx ' + sub_icon + ' nav_icon"></i><span class="nav_name">' + sub_title + '</span></a>'
				btn_html += '<div><div onclick="btnClickedFunc(this)" class="nav_link toggle_class display_flex"><i class="bx ' + icon + ' nav_icon"></i><span class="nav_name">' + main_title + '</span></div><div class="sub_title">' + sub_btn_html + '</div></div>'


		return"""<div id="side-bar">
		<div class="l-navbar" id="nav-bar">
			<div class="nav">
				<div>
					<a class="header_toggle nav_logo toggle_class display_flex">
						<i class='bx bx-menu nav_logo-icon' id="header-toggle"></i>
					</a>
					<a href="%s" class="nav_logo toggle_class display_flex">
						<i class='bx %s nav_logo-icon'></i>
						<span class="nav_logo-name nav_name">%s</span>
					</a>
					<div class="nav_list">%s</div>
				</div>
				<a href="logout" class="nav_link toggle_class display_flex %s">
					<i class='bx bx-log-out nav_icon'></i>
					<span class="nav_name">登出</span>
				</a>
			</div>
		</div>
		</div><script src='%s/static/js/side_bar.js' type="text/javascript"></script>""" % (self.side_bar_title_href, self.title_style, self.side_bar_title, btn_html, login_class, self.main_url)

	def render(self):
		return self.setDashboardSideBtns()


class FStyleNavBtns(FStyle):
	def __init__(self):
		super(FStyleNavBtns, self).__init__()
		self.body = None
		self.side_bar_title_href = Famcy.FManager["ConsoleConfig"]["main_page"]
		self.side_bar_title = Famcy.FManager["ConsoleConfig"]["side_bar_title"]
		self.side_bar_hierarchy = Famcy.FManager["ConsoleConfig"]["side_bar_hierachy"]

	def setNavBtnsInfo(self, side_bar_title=None, side_bar_hierarchy=None):
		if side_bar_title:
			self.side_bar_title = side_bar_title
		if side_bar_hierarchy:
			self.side_bar_hierarchy = side_bar_hierarchy

	def setDashboardNavBtns(self):
		"""
		icon library (version 2.0.8) => https://boxicons.com/
		list with key -> path
		side_bar_hierarchy = [
			{"main_title1": "maintitle1/a"},
			{"main_title2": [
				{"sub_title21": "maintitle2/a"}, 
				{"sub_title22": "maintitle2/b"}
			]}
		]
		title_style = "bx-grid-alt"
		side_bar_style = {"main_title1": "bxl-docker", "main_title2": "bxl-python"}
		"""
		self.body = Famcy.div()
		self.body["className"] = "portfolio_nav"

		for top_level in self.side_bar_hierarchy:
			main_title = list(top_level.keys())[0]

			if not isinstance(top_level[main_title], list):
				btn = Famcy.a()
				btn["href"] = top_level[main_title]
				btn.innerHTML = main_title
				self.body.addElement(btn)
				
			else:
				pass
				# sub_btn_html = ''
				# for sub_level in top_level[main_title]:
				# 	sub_title = list(sub_level.keys())[0]
				# 	sub_icon = defalut_icon
				# 	if sub_title in list_of_icon:
				# 		sub_icon = self.side_bar_style[sub_title]
				# 	sub_btn_html += '<a href="' + sub_level[sub_title] + '" class="nav_link toggle_class display_flex"><i class="bx ' + sub_icon + ' nav_icon"></i><span class="nav_name">' + sub_title + '</span></a>'
				# btn_html += '<div><div onclick="btnClickedFunc(this)" class="nav_link toggle_class display_flex"><i class="bx ' + icon + ' nav_icon"></i><span class="nav_name">' + main_title + '</span></div><div class="sub_title">' + sub_btn_html + '</div></div>'


		return self.body.render_inner()

	def render(self):
		return self.setDashboardNavBtns()



class FColorTheme(FStyle):
	def __init__(self):
		super(FColorTheme, self).__init__()
		self.main_color = "#3968F7"
		self.sub_color = "#94D4ED"
		self.dark_color = "#2d2d2d"
		self.white_color = "#ffffff"
		self.light_grey_color = "#f1f1f1"
		self.semi_grey_color = "#cccccc"

	def setColor(self, main_color=None, sub_color=None, dark_color=None, white_color=None, light_grey_color=None, semi_grey_color=None):
		if main_color:
			self.main_color = main_color
		if sub_color:
			self.sub_color = sub_color
		if dark_color:
			self.dark_color = dark_color
		if white_color:
			self.white_color = white_color
		if light_grey_color:
			self.light_grey_color = light_grey_color
		if semi_grey_color:
			self.semi_grey_color = semi_grey_color

	def setColorTheme(self):
		innerScript = ""
		innerScript += "document.documentElement.style.setProperty('--main-color', '" + self.main_color + "');"
		innerScript += "document.documentElement.style.setProperty('--sub-color', '" + self.sub_color + "');"
		innerScript += "document.documentElement.style.setProperty('--white-color', '" + self.white_color + "');"
		innerScript += "document.documentElement.style.setProperty('--dark-color', '" + self.dark_color + "');"
		innerScript += "document.documentElement.style.setProperty('--light-grey-color', '" + self.light_grey_color + "');"
		innerScript += "document.documentElement.style.setProperty('--semi-grey-color', '" + self.semi_grey_color + "');"
		return"""
		<script>
		%s
		</script>
		""" % (innerScript)

	def render(self):
		return self.setColorTheme()

class FFontTheme(FStyle):
	def __init__(self):
		super(FFontTheme, self).__init__()
		self.font_family = ""
		self.import_font = ""

	def setFontFamily(self, font_family=None, import_font=None):
		if font_family:
			self.font_family = font_family
		if import_font:
			self.import_font = import_font

	def setFontTheme(self):
		innerScript = ""
		innerScript += self.import_font
		innerScript += "<style>*{font-family: " + self.font_family + " !important;}</style>"
		return innerScript

	def render(self):
		return self.setFontTheme()

class FStyleLoader(FStyle):
	def __init__(self):
		super(FStyleLoader, self).__init__()
		self.loaderType = "Spinner"

	def setLoaderType(self, loader_type=None):
		if loader_type:
			self.loaderType = loader_type				# ("Bean_Eater" / "Blocks" / "Double_Ring" / "Ellipsis" / "Gear" / "Infinity" / "Pulse" / "Spinner")

	def setLoader(self):
		self.loaderType = self.loaderType if self.loaderType else "Spinner"
		return '<div id="loading_holder" style="display: none;"><div id="loader"></div></div><script>generate_loader("' + self.loaderType + '")</script>'

	def render(self):
		return self.setLoader()

		
		