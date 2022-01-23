# -*- coding: UTF-8 -*-
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, abort, current_app, Blueprint, send_from_directory, g, Response, stream_with_context
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
import flask_sijax
# from flask_uwsgi_websocket import WebSocket
import redis
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore



import os
import importlib
import Famcy
import json
import time
import random
import pickle
import base64

from Famcy._util_._fmanager import *
from Famcy._util_._fauth import *
from Famcy._util_._felement import *
from Famcy._util_._fblock import *
from Famcy._util_._fpage import *
from Famcy._util_._fcard import *
from Famcy._util_._flayout import *
from Famcy._util_._fstyle import *
from Famcy._util_._fpermissions import *
from Famcy._util_._fthread import *
from Famcy._util_._flayout import *
from Famcy._util_._fstyle import *
from Famcy._util_._fsubmission import *

__codename__ = "Xinhai"
famcy_dir = os.path.dirname(Famcy.__file__)

# Create Global Var for User usage
FamcyElement = FElement
FamcyBlock = FBlock
FamcyPage = FPage
FamcyCard = FCard
FamcyPermissions = FPermissions
FamcyInputBlock = FInputBlock
FamcyUploadBlock = FUploadBlock
FamcyPromptCard = FPromptCard
FamcyResponse = FResponse
FamcyPriority = FPriority

# Login Related
FamcyUser = FUser
FamcyLogin = FLogin
FamcyLoginManager = None

# Layout Related
FamcyLayoutMode = FLayoutMode

# Style Related
FamcyStyle = FStyle
FamcyStyleLoader = FStyleLoader
FamcyColorTheme = FColorTheme
FamcyFontTheme = FFontTheme
FamcyStyleSideBar = FStyleSideBar
FamcyStyleSideBtns = FStyleSideBtns
FamcyStyleNavBar = FStyleNavBar
FamcyStyleNavBtns = FStyleNavBtns
FamcyBackgroundTask = FBackgroundTask

# class IdTable(object):
#   def __init__(self):
#       super(IdTable, self).__init__()
#       self.obj_id_dict = {}

#   def __setitem__(self, key, value):
#       self.obj_id_dict[key] = value

#   def __getitem__(self, key):
#       print("__getitem__", key in self.obj_id_dict.keys())
#       # print("self.obj_id_dict.keys(): ", self.obj_id_dict.keys())
#       return self.obj_id_dict[key]

#   def __delitem__(self, item):
#       print("__delitem__")
#       if item in self.obj_id_dict.keys():
#           del self.obj_id_dict[item]

#   def has_key(self, key):
#       return key in self.obj_id_dict

from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
	def default(self, obj):
		return base64.b64encode(pickle.dumps(obj))

def create_app(famcy_id, production=False):
	"""
	Main creation function of the famcy application. 
	Can set to different factory settings in the future. 
	"""
	# Famcy Manager that manage all global vars, imports, 
	# file systems, http
	FManager = FamcyManager(famcy_id, famcy_dir, production=production)
	globals()["FManager"] = FManager

	# globals()["SubmissionObjectTable"] = IdTable()

	# Header definitions
	FManager["CUSTOM_STATIC_PATH"] = FManager.console + "_static_"

	# Sijax, submission related
	FManager["Sijax"] = flask_sijax
	# FManager["SijaxSubmit"] = SubmitType
	FManager["SijaxStaticPath"] = FManager.main + 'static/js/sijax/'
	FManager["SijaxJsonUri"] = '/static/js/sijax/json2.js'

	# User, login related init
	FManager["FamcyUser"] = FUser
	FManager["LoginManager"] = LoginManager()
	FManager["CurrentUser"] = current_user

	# System Wide blueprints and application object
	MainBlueprint = Blueprint('MainBlueprint', __name__)
	globals()["MainBlueprint"] = MainBlueprint
	FManager["MainBlueprint"] = MainBlueprint
	FManager["CurrentApp"] = current_app

	# Webpage related configs
	FManager["ConsoleConfig"] = FManager.read(FManager.console + "/famcy.yaml")

	# ------------------------
	# --- Main app start zone
	# ------------------------
	app = Flask(__name__)
	# Now tell Flask to use the custom class
	app.json_encoder = CustomJSONEncoder
	# Some sort of security here -> TODO check on this
	app.config['SECRET_KEY'] = FManager.get_credentials("flask_secret_key", "").encode("utf-8")

	# Init Sijax
	FManager["Sijax"].Sijax().init_app(app)
	# FamcyWebSocket = WebSocket(app)
	# FamcyWebSocketLoopDelay = 2.5
	FamcyBackgroundQueue = FamcyPriorityQueue()
	globals()["FamcyBackgroundQueue"] = FamcyBackgroundQueue

	# Init http client
	FManager.init_http_client(**FManager["ConsoleConfig"])
	# Security Enhance
	FManager.register_csrf(app)

	store = RedisStore(redis.StrictRedis())
	globals()["store"] = store
	KVSessionExtension(store, app)

	# User Static Data
	@MainBlueprint.route('/asset/<path:filename>')
	def user_custom_asset(filename):
		# Usage in template {{ url_for('user_custom_asset', filename='doday_icon.png') }}
		return send_from_directory(FManager.console + "/" + FManager.USER_STATIC_FOLDER, filename)

	# Import Fblocks from default and custom folders. 
	# ------------------------------
	# Get all sources of felements definitions 
	system_styles = FManager.importclassdir(FManager.main + "/", "_elements_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_styles)

	# Get all sources of fblocks definitions 
	system_items = FManager.importclassdir(FManager.main + "/", "_items_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_items)

	# Get all sources of fresponse definitions 
	system_responses = FManager.importclassdir(FManager.main + "/", "_responses_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_responses)

	# Get all sources of fstyle definitions 
	system_styles = FManager.importclassdir(FManager.main + "/", "_style_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_styles)

	# Import module recursively for all pages in the console folder
	class_dir = FManager.importclassdir(FManager.console, "", FamcyFileImportMode.fixed, "page", recursive=True, 
			exclude=["_", "."], otherwise=None)

	# Register the main blueprint that is used in the FamcyPage
	app.register_blueprint(MainBlueprint)

	# Init Login Manager and Related Stuffs
	if FManager["ConsoleConfig"]["with_login"]:
		# Init login manager
		FManager["LoginManager"].login_view = "MainBlueprint.famcy_route_func_name_"+FManager["ConsoleConfig"]['login_url'].replace("/", "_")
		FManager["LoginManager"].init_app(app)
		FManager["FamcyUser"].setup_user_loader()
		assert Famcy.FamcyLoginManager, "User Must Register Famcy Login Manager"

	return app

# ------ above is the flask part -----------
