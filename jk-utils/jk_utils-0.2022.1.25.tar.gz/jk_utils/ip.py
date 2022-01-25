


import os
import re
import sys

_has_netifaces = False
try:
	import netifaces
	_has_netifaces = True
except:
	pass






#
# Retrieve all interface name, IP address, MAC address triplets from all active network adapters (excluding loopback and docker)
#
def getIPsEx():
	if _has_netifaces:
		ret = []

		for ifaceName in netifaces.interfaces():
			if ifaceName.startswith("docker"):
				continue
			if ifaceName.startswith("lo"):
				continue

			addrs = netifaces.ifaddresses(ifaceName)
			try:
				ifMac = addrs[netifaces.AF_LINK][0]["addr"]
				ipAddr = addrs[netifaces.AF_INET][0]["addr"]
				if ipAddr.startswith("127."):
					continue
				ret.append([ifaceName, ipAddr, ifMac])
			except IndexError as e:
				pass
			except KeyError as e:
				pass

		return ret

	else:
		raise Exception("Python module netiface module not available!")
#




#
# Retrieve all IP addresses from all active network adapters (excluding loopback and docker)
#
def getIPs():
	return [ x[1] for x in getIPsEx() ]
#






class LocalIPAddressDetector(object):

	def __init__(self, localIPAddressFilters:list):
		self.__localIPAddressRegExes = []
		for s in localIPAddressFilters:
			pos = s.index("*")
			if pos < 0:
				sRegex = "^" + s + "$"
			elif pos == 0:
				sRegex = "^.+" + s + "$"
			elif pos == len(s) - 1:
				sRegex = "^" + s + ".+$"
			else:
				raise Exception("Invalid network card pattern: " + repr(s))
			self.__localIPAddressRegExes.append(re.compile(sRegex))
	#

	def __call__(self):
		return self.getIPAddresses()
	#

	#
	# Retrieve all local IP addresses this machine might be contaced in a local network.
	#
	def getIPAddresses(self):
		if _has_netifaces:
			ret = []

			ipAddrTuples = []
			for ifaceName in netifaces.interfaces():
				addrs = netifaces.ifaddresses(ifaceName)
				try:
					#if_mac = addrs[netifaces.AF_LINK][0]["addr"]
					ipAddr = addrs[netifaces.AF_INET][0]["addr"]
					if ipAddr.startswith("127."):
						continue
					ipAddrTuples.append([ifaceName, ipAddr, False])
				except IndexError as e:
					pass
				except KeyError as e:
					pass

			for ipAddrRegEx in self.__localIPAddressRegExes:
				for r in ipAddrTuples:
					if r[2]:
						continue
					if ipAddrRegEx.match(r[0]):
						r[2] = True
						ret.append(r[1])

			return ret

		else:
			raise Exception("Python module netiface module not available!")
	#

#



