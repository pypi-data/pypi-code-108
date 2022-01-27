import requests
import json


class MahiruServer:
	def __init__(self, address='127.0.0.1', port=46357):
		self.address = address
		self.port = port


class MahiruException(Exception):
	pass


def finish(uuid: str, server: MahiruServer=MahiruServer()):
	res = requests.get(f'http://{server.address}:{server.port}/finish/{uuid}').json()
	if res['status'] != 'success':
		raise MahiruException(res['message'])


def start(taskId: str, args, server: MahiruServer=MahiruServer()):
	res = requests.post(f'http://{server.address}:{server.port}/start', data={
		'id': taskId,
		'arguments': json.dumps(args)
	}).json()
	if res['status'] != 'success':
		raise MahiruException(res['message'])
