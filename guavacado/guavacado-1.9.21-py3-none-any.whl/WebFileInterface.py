#! /usr/bin/env python

import os
import fnmatch
from datetime import datetime

from .misc import generate_redirect_page, init_logger, addr_rep

from .version_number import guavacado_version
WebServerNameAndVer = "Guavacado/"+guavacado_version


class WebFileInterface(object):
	def __init__(self, host=None, host_kwargs={}, host_addr_kwargs={}, web_dispatcher_ident=None, dispatcher_level=None, staticdir="static", staticindex="index.html", include_fp=['{staticdir}/*'], exclude_fp=[]): # pylint: disable=W0102
		if web_dispatcher_ident is None:
			disp_type = 'web'
		else:
			disp_type = ('web',web_dispatcher_ident)

		# starts a WebHost on port 80 that
		if host is None:
			from guavacado import WebHost # pylint: disable=C0415
			self.host = WebHost(**host_kwargs)
			host_addr_kwargs_add = host_addr_kwargs
			if not web_dispatcher_ident is None:
				host_addr_kwargs_add.update({'disp_type': disp_type})
			self.host.add_addr(**host_addr_kwargs_add)
		else:
			self.host = host
		
		self.log_handler = init_logger(__name__)
		self.staticdir = staticdir
		self.staticindex = staticindex
		self.include_fp = include_fp
		self.exclude_fp = exclude_fp
		self.method_actions = {}
		self.host.get_specialized_dispatcher(disp_type).add_resource_handler(self.identify_request, self.handle_request, 'WebFileInterface', level=dispatcher_level)

		self.register_method_action('GET', self.identify_GET_request)
		self.register_method_action('HEAD', self.identify_HEAD_request)
	
	def register_method_action(self, method, callback):
		self.method_actions[method] = callback
	
	def identify_request(self, req_info={'url':None, 'method':None, 'headers':None, 'body':None, 'clientsocket': None, 'extra_response_headers':{}}): # pylint: disable=W0102
		if req_info['method'] in self.method_actions:
			return self.method_actions[req_info['method']](req_info['url'], req_info['headers'], req_info['body'])
		return None
	
	def identify_GET_request(self, url, _headers, _body):
		url_relative = url[1:]
		while len(url_relative)>0 and url_relative[0]=='/':
			url_relative = url_relative[1:]
		index_relative = os.path.join(url_relative,self.staticindex)
		url_relative_static = os.path.join(self.staticdir,url_relative).replace('\\','/')
		index_relative_static = os.path.join(self.staticdir,index_relative).replace('\\','/')
		check_paths = [index_relative, url_relative, index_relative_static, url_relative_static]
		for path in check_paths:
			if self.check_path_allowed(path):
				if os.path.exists(path):
					if os.path.isfile(path):
						def read_file(path=path):
							with open(path, 'rb') as fp:
								data = fp.read()
							return data
						return (read_file, ())
					else:
						return (self.get_dir_page, (path,))
		return None
	
	def identify_HEAD_request(self, url, headers, body):
		result = self.identify_GET_request(url, headers, body)
		if result is None:
			return None
		else:
			# callback, args = result
			def get_empty_result():
				return b''
			return (get_empty_result, ())
	
	def handle_request(self, callback, args):
		return callback(*args)

	def check_path_allowed(self, path):
		for ex_fp in self.exclude_fp:
			if fnmatch.fnmatch(path, ex_fp.format(staticdir=self.staticdir, staticindex=self.staticindex)):
				return False
		for inc_fp in self.include_fp:
			if fnmatch.fnmatch(path, inc_fp.format(staticdir=self.staticdir, staticindex=self.staticindex)):
				return True
		return False

	def get_address_string(self):
		return "{server} Server at {addr}".format(server=WebServerNameAndVer, addr=addr_rep(self.host.get_addr(), pretty=True))
	
	def get_dir_page(self, path):
		if path[-1]!='/':
			return generate_redirect_page('/'+path+'/')
		data = ('<html><head><title>Index of {path}</title></head><body><h1>Index of {path}</h1><table>'+\
			'<tr><th valign="top"></th><th>Name</th><th>Last modified</th><th>Size</th></tr>'+\
			'<tr><th colspan="5"><hr></th></tr>'+\
			'<tr><td valign="top"></td><td><a href="..">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td></tr>').format(
				path="/"+path
			)
		for filename in os.listdir(path):
			fullpath = os.path.join(path,filename)
			if os.path.isdir(fullpath):
				if filename[-1]!='/':
					filename = filename + '/'
			filestat = os.stat(fullpath)
			size = filestat.st_size
			size_str = str(size)
			if size>(1<<10):
				size_str = str(size/(1<<10))+"K"
			if size>(1<<20):
				size_str = str(size/(1<<20))+"M"
			if size>(1<<30):
				size_str = str(size/(1<<30))+"G"
			if size>(1<<40):
				size_str = str(size/(1<<40))+"T"
			data = data + '<tr><td valign="top"></td><td><a href="{filename}">{filename}</a></td><td align="right">{lastmodified}</td><td align="right">{size}</td></tr>'.format(
				filename=filename,
				lastmodified=datetime.fromtimestamp(filestat.st_mtime),
				size=size_str
			)
		data = data + (('<tr><th colspan="5"><hr></th></tr></table>'+\
			'<address>{address}</address>'+\
			'</body></html>').format(
				address=self.get_address_string()
			))
		return data

	def start_service(self):
		self.host.start_service()
	def stop_service(self):
		self.host.stop_service()
