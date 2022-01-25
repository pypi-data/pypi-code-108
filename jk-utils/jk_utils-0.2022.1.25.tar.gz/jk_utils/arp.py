



import os
import sys
import socket
import time
import json
import codecs
import re

_has_netifaces = False
try:
	import netifaces
	_has_netifaces = True
except:
	pass

import jk_simpleexec

from .dtutils import *
from .Cache import Cache






class ArpRecord(object):

	def __init__(self, ipAddress, flag, macAddr, interface):
		self.ipAddress = ipAddress
		#self.flag = flag
		self.macAddress = macAddr
		self.interface = interface
	#

	def dump(self, out_stream = sys.stdout, prefix = ""):
		out_stream.write(prefix + self.__repr__() + "\n")
	#

	def __repr__(self):
		return "ARP(" + self.ipAddress + ", " + self.macAddress + ", " + self.interface + ")"
	#

	def __str__(self):
		return "ARP(" + self.ipAddress + ", " + self.macAddress + ", " + self.interface + ")"
	#

#



class cachedarp(object):

	__cache = Cache(60)

	@staticmethod
	def arpResolveByIP(ipAddress):
		r = cachedarp.__cache.get(ipAddress)
		if r != None:
			return r[1]
		mac = arp.arpResolveByIP(ipAddress)
		cachedarp.__cache.put(ipAddress, (True, mac))
		return mac
	#

#




class arp(object):

	__reReply1 = re.compile("^ARPING [0-9\.]+ from [0-9\.]+ ([0-9a-zA-Z\.]+)$")
	__reReply2 = re.compile("^Unicast reply from [0-9\.]+ \[([0-9a-fA-F:]+)\] ")


	#
	# Get the MAC address for the specified IP address.
	# Please note that data is taken from the operating system cache if possible.
	# If no record exists in the cache an ARP query is performed. During this query the remote host has a single second to reply,
	# so this method will take at most one second to execute.
	#
	# @param		str ipAddress		The IP address to get the MAC address for
	# @return		ArpRecord			Either returns a valid <c>ArpRecord</c> object or <c>None</c>.
	#
	@staticmethod
	def arpResolveByIP(ipAddress):
		assert isinstance(ipAddress, str)

		for arpEntry in arp.systemArpEntries():
			if arpEntry.ipAddress == ipAddress:
				return arpEntry
		for arpEntry in arp.arpEntriesOfLocalInterfaces():
			if arpEntry.ipAddress == ipAddress:
				return arpEntry
		arpEntry = arp.arpQuery(ipAddress)
		return arpEntry
	#



	#
	# Get the IP address for the specified MAC address.
	# Please note that data is taken from the operating system cache only. If no data is stored in that cache this method will return <c>None</c>.
	#
	# @param		str macAddress		The MAC address to get the IP address for
	# @return		ArpRecord			If no data is in the cache <c>None</c> is returned. Otherwise a valid <c>ArpRecord</c> object is returned.
	#
	@staticmethod
	def arpResolveByMAC(macAddress):
		assert isinstance(macAddress, str)

		for arpEntry in arp.systemArpEntries():
			if arpEntry.macAddress == macAddress:
				return arpEntry
		return None
	#



	#
	# Perform an single ARP query.
	# Please note that invoking this method will cause network traffic. A remote host is queried. As this host has a single second to reply
	# this method will take at most one second to execute.
	# Please also note that remote hosts that are not connected well might exceed the timeout and therefor will not be listed by this method.
	#
	# @param		str ipAddress		The IP address to get the MAC address for
	# @return		ArpRecord			Returns an <c>ArpRecord</c> object or <c>None</c>.
	#
	@staticmethod
	def arpQuery(ipAddress):
		assert isinstance(ipAddress, str)

		result = jk_simpleexec.invokeCmd("/usr/bin/arping", [ "-w", "0.5", "-fb", "-c", "1", ipAddress ])
		if len(result.stdErrLines) > 0:
			raise Exception("arping failed: " + result.commandPath + " " + str(result.commandArguments))
		lines = result.stdOutLines
		result1 = arp.__reReply1.match(lines[0])
		if result1:
			result2 = arp.__reReply2.match(lines[1])
			if result2:
				return ArpRecord(ipAddress, -1, result2.group(1), result1.group(1))
			return None
		else:
			raise Exception("arping failed: Unexpected output: " + lines[0])
	#



	#
	# Queries the operating system ARP cache to list all known ARP records.
	# Please note that if an ARP record is missing this does not mean that this host is not active.
	# This only means the operating system just had no recent contact with this system.
	# Please also note that local IP and MAC addresses are not listed in this cache. User <c>arpEntriesOfLocalInterfaces()</c>
	# to list pseudo ARP entries for these network interfaces.
	#
	# @return		ArpRecord[]			Returns (a possibly empty list) of ARP records.
	#
	@staticmethod
	def systemArpEntries():
		with codecs.open("/proc/net/arp", "r") as f:
			lines = f.readlines()
			lines = lines[1:]
		ret = []
		for line in lines:
			ipAddress, hexHWType, hexFlag, macAddr, mask, interfaceDevice = re.split(" +", line[:-1])
			flag = int(hexFlag, 0)
			if flag in [2, 4, 6, 8]:
				ret.append(ArpRecord(ipAddress, flag, macAddr, interfaceDevice))
		return ret
	#



	#
	# Returns a list of MACs that are used locally by this host.
	# Please note that this method addresses only the local interfaces as they these MAC addresses are not maintained by the
	# operating system ARP cache.
	#
	# @return		ArpRecord[]			Returns a (possibly empty) list of <c>ArpRecord</c> objects.
	#
	@staticmethod
	def arpEntriesOfLocalInterfaces():
		if _has_netifaces:
			ret = []

			for i in netifaces.interfaces():
				addrs = netifaces.ifaddresses(i)
				try:
					if_mac = addrs[netifaces.AF_LINK][0]['addr']
					if_ip = addrs[netifaces.AF_INET][0]['addr']
				except IndexError as e:
					if_mac = if_ip = None
				except KeyError as e: #ignore ifaces that dont have MAC or IP
					if_mac = if_ip = None
				ret.append(ArpRecord(if_ip, -1, if_mac, None))

			return ret

		else:
			raise Exception("Python module netiface module not available!")
	#

#

















