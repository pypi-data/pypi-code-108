import os
import argparse

from .WebHost import WebHost
from .WebFileInterface import WebFileInterface
from .misc import wait_for_keyboardinterrupt

def main():
	"""
	serves a static folder in the local 'static' directory
	using https (self-signed certificate) on port 443, and redirecting traffic from port 80 to https
	"""
	host = WebHost(loglevel='INFO')
	host.add_addr(port=80, disp_type=('redirect', 'https://localhost/'))
	host.add_addr(port=443, TLS=(os.path.join('TLS_keys','self_signed.crt'),os.path.join('TLS_keys','self_signed.key')))
	_ = WebFileInterface(host)
	host.start_service()
	wait_for_keyboardinterrupt()
	host.stop_service()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Serves a basic static folder on a HTTP server.')
	# parser.add_argument('-a', '--ip',       dest='ip',      default=argparse.SUPPRESS, help='IP address the data should be streamed to.')
	# parser.add_argument('-p', '--portno',   dest='portno',  default=argparse.SUPPRESS, help='Port number the data should be sent to.')
	# parser.add_argument('-w', '--wls_path', dest='WLSpath', default=argparse.SUPPRESS, help='Path to WLStream - should be the full path to the executable WLStream.exe')
	# parser.add_argument('-d', '--device',   dest='device',  default=argparse.SUPPRESS, help='Name of the device to pass to WLStream, indicating which device audio should be sampled from.')
	args = parser.parse_args()
	init_settings = args.__dict__
	main(**init_settings)
