


import os
import sys
import socket
import struct
import select
import time
import json




if sys.platform == "win32":
	# On Windows, the best timer is time.clock()
	__dDefaultTimer = time.clock
else:
	# On most other platforms the best timer is time.time()
	__dDefaultTimer = time.time

# From /usr/include/linux/icmp.h; your milage may vary.
__ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.




def __checksum(source_string):
	"""
	I'm not too confident that this is right but testing seems
	to suggest that it gives the same answers as in_cksum in ping.c
	"""
	sum = 0
	countTo = (len(source_string)/2)*2
	count = 0
	while count<countTo:
		thisVal = source_string[count + 1]*256 + source_string[count]
		sum = sum + thisVal
		sum = sum & 0xffffffff # Necessary?
		count = count + 2

	if countTo<len(source_string):
		sum = sum + source_string[len(source_string) - 1]
		sum = sum & 0xffffffff # Necessary?

	sum = (sum >> 16)  +  (sum & 0xffff)
	sum = sum + (sum >> 16)
	answer = ~sum
	answer = answer & 0xffff

	# Swap bytes. Bugger me if I know why.
	answer = answer >> 8 | (answer << 8 & 0xff00)

	return answer
#



#
# Receives a single ping.
#
# @param		socket my_socket		The socket to receive the ping from
# @param		int ID					The ID the ping packet must have (otherwise it will be rejected)
# @param		int timeout				The number of seconds to wait for a ping received
# @return		tuple<str,int>			Returns either <c>(None, None)</c> or a tuple containing:
#										* the sender IP address as string
#										* the delay in seconds
#
def __receive_one_ping(my_socket, ID, timeout):
	timeLeft = timeout
	while True:
		startedSelect = __dDefaultTimer()
		whatReady = select.select([my_socket], [], [], timeLeft)
		howLongInSelect = (__dDefaultTimer() - startedSelect)
		if whatReady[0] == []: # Timeout
			return (None, None)

		timeReceived = __dDefaultTimer()
		recPacket, addr = my_socket.recvfrom(1024)
		#print("-- received from: " + addr[0])
		icmpHeader = recPacket[20:28]
		type, code, checksum, packetID, sequence = struct.unpack(
			"bbHHh", icmpHeader
		)
		# Filters out the echo request itself.
		# This can be tested by pinging 127.0.0.1
		# You'll see your own request
		if type != 8 and packetID == ID:
			bytesInDouble = struct.calcsize("d")
			timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
			return (addr[0], timeReceived - timeSent)

		timeLeft = timeLeft - howLongInSelect
		if timeLeft <= 0:
			return (None, None)
#



#
# Receives a set of pings.
#
# @param		socket my_socket		The socket to receive the ping from
# @param		int ID					The ID the ping packet must have (otherwise it will be rejected)
# @param		int timeout				The number of seconds to wait for a ping received
# @param		int count				The number of ping packets expected. This routine will return if this number of
#										ping packets has successfully been received.
# @return		dict					Returns a dictionary containing:
#										* keys: the IP addresses as strings
#										* values: the delay of the ping packet
#
def __receive_multiple_pings(my_socket, ID, timeout, count):
	"""
	receive a number of pings ping from the socket.
	"""
	ret = {}
	timeLeft = timeout
	while True:
		startedSelect = __dDefaultTimer()
		whatReady = select.select([my_socket], [], [], timeLeft)
		howLongInSelect = (__dDefaultTimer() - startedSelect)
		if whatReady[0] == []: # Timeout
			return ret

		timeReceived = __dDefaultTimer()
		recPacket, addr = my_socket.recvfrom(1024)
		#print("-- received from: " + addr[0])
		icmpHeader = recPacket[20:28]
		type, code, checksum, packetID, sequence = struct.unpack(
			"bbHHh", icmpHeader
		)
		# Filters out the echo request itself.
		# This can be tested by pinging 127.0.0.1
		# You'll see your own request
		if type != 8 and packetID == ID:
			bytesInDouble = struct.calcsize("d")
			timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
			ret[addr[0]] = timeReceived - timeSent
			count -= 1
			if count == 0:
				return ret

		timeLeft = timeLeft - howLongInSelect
		if timeLeft <= 0:
			return ret
#



#
# Send a single ping packet.
#
# @param		socket my_socket		The socket to send the packet on.
# @param		str dest_ip_addr		A IP adddress (!) to send the ping packet to.
# @param		int ID					An identifier to send with the ping message
# @return		bool					Returns <c>True</c> on success, <c>False</c> on error.
#										Such an error occurred if sending a ping failed f.e. because
#										there is no network connection available.
#
def __send_one_ping(my_socket, dest_ip_addr, ID):
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)
	my_checksum = 0

	# Make a dummy heder with a 0 checksum.
	header = struct.pack("bbHHh", __ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
	bytesInDouble = struct.calcsize("d")
	data = bytes((192 - bytesInDouble) * "Q", 'utf-8')
	data = struct.pack("d", __dDefaultTimer()) + data

	# Calculate the checksum on the data and the dummy header.
	my_checksum = __checksum(header + data)

	# Now that we have the right checksum, we put that in. It's just easier
	# to make up a new header than to stuff it into the dummy.
	header = struct.pack(
		"bbHHh", __ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
	)
	packet = header + data
	try:
		my_socket.sendto(packet, (dest_ip_addr, 1)) # Don't know about the 1
		return True
	except OSError:
		return False
#



#
# Perform a single ping to the specified address.
# You must be root to invoke this function.
#
# @param		string destinationAddress	The destination host to send the ping packet to. This can either be a host name or an IP address.
# @param		int timeout					The timeout in seconds to wait for a response.
# @return		tuple<int,str>				Returns a tuple of two values:
#											* the sender IP address as string
#											* the delay in seconds (possibly <c>None</c> if the destination did not reply)
#
def pingSingleHost(destinationAddress, timeout):
	if os.geteuid() != 0:
		raise Exception("Pings can only be sent as root!")

	icmp = socket.getprotobyname("icmp")
	try:
		my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	except PermissionError as e:
		#e.args = (e.args if e.args else tuple()) + ((
		#	" - Note that ICMP messages can only be sent from processes"
		#	" running as root."
		#),)
		raise

	my_ID = os.getpid() & 0xFFFF

	destIPAddr = socket.gethostbyname(destinationAddress)
	__send_one_ping(my_socket, destIPAddr, my_ID)
	senderIPAddr, delay = __receive_one_ping(my_socket, my_ID, timeout)

	my_socket.close()
	return destIPAddr, delay
#


#
# Send a ping to multiple hosts at the same time.
# You must be root to invoke this function.
#
# @param		string[] destinationAddresses	An iterable of destination addresses. These can either be a host name or an IP address.
#												You should not attempt to use more than 300 IP addresses in this list as it has been found
#												to otherwise overload the internal operating system buffers for the network interface.
#												(This limit roughly applies to regular Linux systems. Please note that this limit might be
#												a bit different.)
# @param		int timeout						The timeout in seconds to wait for the responses.
# @param		bool orderByIPAddr				This routine performs address resolution. This parameter decides about the grouping of the results returned.
#												If <c>True</c> is specified here this routine returns a map containing IP addresses as
#												keys and tuples of host names and delays as values.
#												If <c>False</c> is specified here this routine returns a map containing the host names
#												as keys and tuples of IP addresses and delays as values.
# @return		dict							Returns a dictionary with tuples. Depending on the parameter <c>orderByIPAddr</c> the keys
#												are either host names or IP addresses, the values tuples of host names or IP addresses as first element
#												and the ping delays in seconds as the second element. This second element is <c>None</c> if the
#												destination host did not reply.
#
def pingMultipleHosts(destinationAddresses, timeout:int, orderByIPAddr:bool = False):
	if os.geteuid() != 0:
		raise Exception("Pings can only be sent as root!")

	icmp = socket.getprotobyname("icmp")
	try:
		my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	except PermissionError as e:
		#e.args = (e.args if e.args else tuple()) + ((
		#	" - Note that ICMP messages can only be sent from processes"
		#	" running as root."
		#),)
		raise

	my_ID = os.getpid() & 0xFFFF

	orgAddresses = []
	ipAddresses = []
	dataMap = {}
	for dest_addr in destinationAddresses:
		orgAddresses.append(dest_addr)
		ipAddress = socket.gethostbyname(dest_addr)
		ipAddresses.append(ipAddress)
		#print(dest_addr + " :: " + destIPAddr)
		dataMap[ipAddress] = (dest_addr, None)

	#n = 0
	nPingsSend = 0
	nPingsSendSucceeded = 0
	for destIPAddr in ipAddresses:
		#print(n)
		#n += 1
		#print("-- " + str(my_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)))
		nPingsSend += 1
		if __send_one_ping(my_socket, destIPAddr, my_ID):
			nPingsSendSucceeded += 1
	if nPingsSendSucceeded == 0:
		# we did not succeed in sending a single ping, probably we're not connected right now.
		receiverMap = {}
	else:
		# at least one ping could be sent.
		receiverMap = __receive_multiple_pings(my_socket, my_ID, timeout, len(orgAddresses))
		#print(receiverMap)

	for ipAddr in receiverMap.keys():
		orgAddr = dataMap[ipAddr][0] if ipAddr in dataMap else None
		dataMap[ipAddr] = (orgAddr, receiverMap[ipAddr])

	if not orderByIPAddr:
		# reorder
		dataMap2 = {}
		for ipAddr in dataMap:
			orgAddr, delay = dataMap[ipAddr]
			dataMap2[orgAddr] = (ipAddr, delay)
		dataMap = dataMap2

	my_socket.close()
	return dataMap
#






