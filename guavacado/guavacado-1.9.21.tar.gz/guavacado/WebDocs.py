#! /usr/bin/env python
'''provides a documentation page for the web server, showing all functions available and their URLs'''

import json

from .WebInterface import WebInterface
from .misc import generate_redirect_page

class WebDocs(object):
	'''provides a documentation page for the web server, showing all functions available and their URLs'''
	def __init__(self, host, dispatcher_level=None):
		self.host = host
		self.web_interface = WebInterface(host=self.host, dispatcher_level=dispatcher_level)
		self.resource_list = []
	
	def connect_funcs(self):
		'''connects the documentation functions to the default web interface'''
		# self.web_interface.connect('/',self.ROOT_REDIRECT,'GET')
		self.web_interface.connect('/docs/',self.GET_DOCS,'GET')
		self.web_interface.connect('/docs/json/',self.GET_DOCS_JSON,'GET')

	def log_connection(self,resource,action,method,websock_actions=None):
		'''adds the given information to the REST API documentation list'''
		def get_action_dict(fn):
			if fn is None:
				return {
					'docstring':None,
					'function_name':None,
				}
			return {
				'docstring':fn.__doc__,
				'function_name':fn.__name__,
			}
		log_entry = {
			'websocket':None,
			'resource':resource,
			'method':method,
		}
		log_entry.update(get_action_dict(action))
		if websock_actions is not None:
			log_entry['websocket'] = {
				'connected': get_action_dict(websock_actions['connected']),
				'received': get_action_dict(websock_actions['received']),
				'closed': get_action_dict(websock_actions['closed']),
			}
		self.resource_list.append(log_entry)

	def ROOT_REDIRECT(self):
		'''redirects to /static/ directory'''
		return generate_redirect_page("/static/")

	def GET_DOCS(self):
		'''return the documentation page in HTML format'''
		def empty_str_if_none(val):
			if val is None:
				return ''
			return val
		def multilevel_dict_or_empty(d, subpath):
			if d is None:
				return ''
			if len(subpath)==0:
				return empty_str_if_none(d)
			if subpath[0] in d:
				return multilevel_dict_or_empty(d[subpath[0]], subpath[1:])
		has_websock = len([r for r in self.resource_list if r['websocket'] is not None]) > 0
		resources = ""
		for resource in self.resource_list:
			if resource["docstring"] is None:
				resource["docstring"] = "&lt;No docs provided!&gt;"
			resource_html = """
						<tr>
							<td>{resource_link}</td>
							<td>{method}</td>
							<td>{function_name}</td>
							<td>{docstring}</td>
							{websock_vals}
						</tr>
			""".format(
				resource_link = {False:'<a href="{resource}">{resource}</a>'.format(
					resource = resource["resource"],
				),True:'''
					<a onclick="(()=>{opencurlyboi}
						var resource = '{resource}';
						{more_javascript}
					{closecurlyboi})();">ws[s]://...{resource}</a>
				'''.format(
					resource = resource["resource"],
					opencurlyboi='{',
					closecurlyboi='}',
					more_javascript='''
						var url = window.location.origin.replace('https://','wss://').replace('http://','ws://') + resource;
						console.log(url);
						var socket = new WebSocket(url);

						socket.addEventListener('open', (e) => {
							console.log(url + ' connected!');
							console.log(e);
						});

						socket.addEventListener('message', (e) => {
							console.log(url + ' received!');
							console.log(e);
							console.log(e.data);
							var reader = new FileReader();
							reader.onload = function() {
								console.log(reader.result);
							}
							reader.readAsText(e.data);
						});

						socket.addEventListener('close', (e) => {
							console.log(url + ' closed!');
							console.log(e);
						});

						socket.addEventListener('error', (e) => {
							console.log(url + ' error!');
							console.error(e);
						});
						
						console.log(socket);
					''',
				)}[resource['websocket'] is not None],
				method = resource["method"],
				function_name = empty_str_if_none(resource["function_name"]),
				docstring = empty_str_if_none(resource["docstring"]).replace("\n","<br />"),
				websock_vals = {True:'''
							<td>{has_sock}</td>
							<td>{connected}</td>
							<td>{connected_docstring}</td>
							<td>{received}</td>
							<td>{received_docstring}</td>
							<td>{closed}</td>
							<td>{closed_docstring}</td>
				'''.format(
					has_sock = {True:'✅',False:''}[resource['websocket'] is not None],
					connected = multilevel_dict_or_empty(resource, ['websocket', 'connected', 'function_name']),
					connected_docstring = multilevel_dict_or_empty(resource, ['websocket', 'connected', 'docstring']),
					received = multilevel_dict_or_empty(resource, ['websocket', 'received', 'function_name']),
					received_docstring = multilevel_dict_or_empty(resource, ['websocket', 'received', 'docstring']),
					closed = multilevel_dict_or_empty(resource, ['websocket', 'closed', 'function_name']),
					closed_docstring = multilevel_dict_or_empty(resource, ['websocket', 'closed', 'docstring']),
				),False:''}[has_websock],
			)
			resources = resources+resource_html
		return """
			<!DOCTYPE html>
			<html>
				<head>
					<meta charset="UTF-8">
					<title>Guavacado Web Documentation</title>
				</head>
				<body>
					<table border="1">
						<tr>
							<th>Resource</th>
							<th>Method</th>
							<th>Function Name</th>
							<th>Docstring</th>
							{websock_headers}
						</tr>
						{resources}
					</table>
				</body>
			</html>
		""".format(
			websock_headers={True:'''
							<th>Websocket</th>
							<th>Websocket Connected</th>
							<th>Docstring</th>
							<th>Websocket Received</th>
							<th>Docstring</th>
							<th>Websocket Closed</th>
							<th>Docstring</th>
			''',False:''}[has_websock],
			resources=resources,
		)

	def GET_DOCS_JSON(self):
		'''return the documentation page in JSON format'''
		return json.dumps(self.resource_list)
