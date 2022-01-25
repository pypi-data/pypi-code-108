

import os
import sys

_has_netifaces = False
try:
	import netifaces
	_has_netifaces = True
except:
	pass





#
# Retrieve all MAC addresses from all active network adapters (excluding local host)
#
def getMACs():
	if _has_netifaces:
		ret = []

		for i in netifaces.interfaces():
			addrs = netifaces.ifaddresses(i)
			try:
				if_mac = addrs[netifaces.AF_LINK][0]['addr']
				if_ip = addrs[netifaces.AF_INET][0]['addr']
				if if_ip == "127.0.0.1":
					continue
				ret.append(if_mac)
			except IndexError as e:
				pass
			except KeyError as e:
				pass

		return ret

	else:
		raise Exception("Python module netiface module not available!")
#



