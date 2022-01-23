from Famcy._util_._fwidget import FamcyWidget
from Famcy._util_._flayout import *
from Famcy._util_._fsubmission import *
from Famcy._util_._fpermissions import *
from Famcy._util_._fthread import *
from flask import g, Response, request, session, redirect, url_for
from flask_login import login_required
import Famcy
import time
import abc
import pickle

class FPage(FamcyWidget):
	"""
	This page represents each of the page 
	on Famcy. It handles rendering, layout, 
	submission, etc... providing an overview
	of everything that happens in the page. 

	Routing of the page is defined by the folder
	/ subfolders file structure. 

	Abstraction:
		AF(route, style) = The page that is at url route and 
		apply css / js style of style
	
	Rep:
		* layout: FamcyLayout. Represent the layout
		of Famcy cards of the page. 
		* permission: FPermissions. Represent
		the allowed access of the user to this page. 

	Interface:
		* render(): render the page
		* register(): register the page to the Famcy env
		* preload(): action before the rendering
		* postload(): actions after the rendering
	"""
	route = "/"
	style = None
	permission = None
	background_thread_flag = False
	background_freq = 0.5

	# def __init__(self, route, style, permission_level=0, 
	#       layout_mode=FLayoutMode.recommend, 
	#       background_thread=False, background_freq=0.5):
	def __init__(self, layout_mode=FLayoutMode.recommend):

		super(FPage, self).__init__()
		# self.route = route
		# self.style = style
		self.layout = FamcyLayout(self, layout_mode)
		# self.permission = FPermissions(permission_level)
		# self.background_thread_flag = background_thread
		# self.background_freq = background_freq

		self.init_page()

		if FPage.background_thread_flag:
			self.sijax_response = None
			
			# Check loop correctness
			assert getattr(self, "background_thread_inner", None), "Must implement background_thread_inner"
			self.bthread = FamcyThread(target=self.background_thread_loop, daemon=True)
			self.bthread.start()

		self._check_rep()

	def init_page(self):
		self.body = Famcy.ELEMENT()

	def _check_rep(self):
		"""
		Check rep invariant:
			- Famcy layout in bound
			- Permission is not empty, able to 
				access in some way. 
		"""
		pass

	@classmethod
	def setClassAttr(cls, key, value):
		if key in cls.__dict__.keys():
			cls.__dict__[key] = value

	@classmethod
	def register(cls, route, style, permission_level=0, background_thread=False, background_freq=0.5, init_cls=None):
		cls.route = route
		cls.style = style
		cls.permission = FPermissions(permission_level)
		cls.background_thread_flag = background_thread
		cls.background_freq = background_freq

		route_func = lambda: cls.render(init_cls=init_cls)
		route_func.__name__ = "famcy_route_func_name"+route.replace("/", "_")

		if cls.permission.required_login():
			# Register the page render to the main blueprint
			Famcy.FManager["Sijax"].route(Famcy.MainBlueprint, cls.route)(login_required(route_func))
		else:
			Famcy.FManager["Sijax"].route(Famcy.MainBlueprint, cls.route)(route_func)

		if cls.background_thread_flag:
			bg_func = lambda: cls.background_generator_loop()
			bg_func.__name__ = "bgloop_famcy_route_func_name"+route.replace("/", "_")

			if cls.permission.required_login():
				# Register the page render to the main blueprint
				Famcy.FManager["MainBlueprint"].route(cls.route+"/bgloop")(login_required(bg_func))
			else:
				Famcy.FManager["MainBlueprint"].route(cls.route+"/bgloop")(bg_func)
		
	@classmethod
	def render(cls, init_cls=None, *args, **kwargs):
		if g.sijax.is_sijax_request:
			sijaxHandler = FSubmissionSijaxHandler
			sijaxHandler.current_page = session.get('current_page')
			print("session.get('current_page').id: ", sijaxHandler.current_page.id)

			# code for upload form
			upload_list = session.get('current_page').find_class(session.get('current_page'), "upload_form")
			for _item in upload_list:
				_ = g.sijax.register_upload_callback(_item.id, sijaxHandler.upload_form_handler)

			g.sijax.register_object(sijaxHandler)
			return g.sijax.process_request()

		# init page
		if request.method == 'GET':
			if init_cls:
				current_page = init_cls
			else:
				current_page = cls()
			if not isinstance(cls.style, Famcy.VideoStreamStyle):
				session["current_page"] = current_page

		form_init_js = ''	# no use
		end_script = ''
		if not current_page.permission.verify(Famcy.FManager["CurrentUser"]):
			# content_data = "<h1>You are not authorized to view this page!</h1>"
			session["login_permission"] = "You are not authorized to view this page!"
			return redirect(url_for("MainBlueprint.famcy_route_func_name_"+Famcy.FManager["ConsoleConfig"]['login_url'].replace("/", "_")))
		else:
			# Render all content
			current_page.body = super(FPage, current_page).render()
			content_data = current_page.body.render_inner()
			end_script = current_page.body.render_script()
			for temp, _ in current_page.layout.staticContent:
				end_script += temp.body.render_script()

			# Apply style at the end
			return current_page.style.render(current_page.header_script, content_data, background_flag=current_page.background_thread_flag, route=current_page.route, time=int(1/current_page.background_freq)*1000, form_init_js=form_init_js, end_script=end_script)

	@staticmethod
	def background_generator_loop():
		def generate():
			try:
				baction = Famcy.FamcyBackgroundQueue.pop()
				yield json.dumps({"indicator": True, "message": baction.tojson()})

			except Exception as e:
				yield json.dumps({"indicator": False, "message": str(e)})

		return Response(generate(), mimetype='text/plain')

	def background_thread_loop(self):
		"""
		This is the background thread 
		loop for fpage
		"""
		while True:
			time.sleep(int(1/self.background_freq))
			self.background_thread_inner()

	def background_thread_inner(self):
		"""
		This is the background thread
		inner content for fpage. 
		"""
		pass

	# Functions that can be overwritten
	# ---------------------------------
	def render_inner(self):
		"""
		This is the function to 
		render the layout. 
		"""
		header_script, self.body = self.layout.render()

		if header_script not in self.header_script:
			self.header_script += header_script
		
		return self.body

	def preload(self):
		"""
		This is the preload function
		that should be executed before 
		the inner render function. 
		"""
		pass

	def postload(self):
		"""
		After the page is rendered, 
		apply async post load function. 
		"""
		pass

