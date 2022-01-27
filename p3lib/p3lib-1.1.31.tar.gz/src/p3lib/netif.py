#!/usr/bin/env python3.8

import  platform
from    subprocess import call, check_output
import  socket
import  struct

class NetIF(object):
    """@Responsible for determining details about the network interfaces on a PC."""
    
    LINUX_OS_NAME      = "Linux"
    SUPPORTED_OS_NAMES = [ LINUX_OS_NAME ]
    
    ID_STR1            = "inet addr:"
    ID_STR2            = "addr:"
    ID_STR3            = "mask:"
    ID_STR4            = "inet "

    IP_NETMASK_SEP     = "/"
    
    @staticmethod
    def IsAddressInNetwork(ip, net):
        """@brief Determine if an IP address is in a IP network.
           @param ip The IP address of the interface in the format 192.168.1.20
           @param net The network in the format 192.168.1.0/24"""
        ipaddr = socket.inet_aton(ip)
        netaddr, netmask = net.split(NetIF.IP_NETMASK_SEP)
        netaddr = socket.inet_aton(netaddr)

        ipint = struct.unpack("!I", ipaddr)[0]
        netint = struct.unpack("!I", netaddr)[0]
        maskint = (0xFFFFFFFF << (32 - int(netmask))) & 0xFFFFFFFF

        return ipint & maskint == netint

                
    @staticmethod            
    def IPStr2int(addr):  
        """@brief Convert an IP address string to an integer.
           @param addr The IP address string.
           @return The integer represented by the IP address."""                                                             
        return struct.unpack("!I", socket.inet_aton(addr))[0]                       
    
    @staticmethod      
    def Int2IPStr(addr):                                                               
        """@brief Convert an integer to an IP address string.
           @param addr The Integer value of the IP address.
           @return The string value (dotted quad) of the IP address."""
        return socket.inet_ntoa(struct.pack("!I", addr))  

    @staticmethod
    def NetmaskToBitCount(netmask):
        """@brief Convert a dotted quad netmask to a bit count netmask format.
           @param netmask: The dotted quad netmask (E.G 255.255.255.0)
           @return: The netmask as a count of the set bits (E.G 24).
        """
        return sum([bin(int(x)).count('1') for x in netmask.split('.')])

    @staticmethod
    def BitCountToNetMask(bitCount):
        """@brief Convert a bit count to a netmask string
           @param bitCount The number of bits in the netmask.
           @return The netmask string E.G 255.255.255.0"""
        if bitCount > 32:
            raise Exception("{} greater than 32".format(bitCount))
        num=1
        for _ in range(0,bitCount):
            num=num>>1
            num=num|0x80000000
        return NetIF.Int2IPStr(num)
        
    def __init__(self):
        
        self._osName = platform.system()

        self._checkSupportedOS()
        
        self._ifDict = None
        
    def getLocalNetworkAddress(self):
        """@brief Get the IP address of the local interface that has the default route.
                  The IP address will be the source IP address for packets are sent over the default route from this machine.
                  This works on Windows, Linux, Android""" 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.connect(('<broadcast>', 0))
        netIPAddr = sock.getsockname()[0]
        sock.close()
        return netIPAddr

    def getIFDict(self, readNow=False, includeNoIPIF = False):
        """@param readNow If True the read the current network interface 
                          state now regardless of wether we have read it previously.
                          If False and we have read the state of the network 
                          interfaces previously then return the previous state.
           @param includeNoIPIF If True then interfaces with no IPaddress are included in the results.
           @return A dict of the IP network interfaces on this platform.
                       key   = name of interface
                       value = A list of <IP ADDRESS>/<NET MASK BIT COUNT>"""
        if self._ifDict and not readNow:
            return self._ifDict
                   
        if self._osName.find(NetIF.LINUX_OS_NAME) >= 0 :
            self._ifDict = self.getLinuxIFDict(includeNoIPIF=includeNoIPIF)
                   
        return self._ifDict
    
    def getLinuxIFDict(self, includeNoIPIF = False):
        """@brief Get a dic that contains the local interface details.
           @param includeNoIPIF If True then interfaces with no IPaddress are included in the results.
           @return A dict of the IP network interfaces on this platform.
                       key   = name of interface
                       value = A list of <IP ADDRESS>/<NET MASK BIT COUNT>"""
        netIFDict = {}
        ifName = None
        
        cmdOutput = check_output(['/sbin/ip','a'] ).decode()
        netIFDict = self._getLinuxIFDict(cmdOutput, includeNoIPIF=includeNoIPIF)
        return netIFDict

    def _getLinuxIFDict(self, cmdOutput, includeNoIPIF=False):
        """@brief Get a dic that contains the local interface details.
           @param cmdOutput The ip a command output.
           @param includeNoIPIF If True then interfaces with no IPaddress are included in the results.
           @return A dict of the IP network interfaces on this platform.
                       key   = name of interface
                       value = A list of <IP ADDRESS>/<NET MASK BIT COUNT>"""
        netIFDict = {}
        lines = cmdOutput.lower().split('\n')
        interfaceID = 1
        ifName = None
        ifAddressList = []
        for line in lines:
            elems = line.split(":")
            try:
                #If first element is the IF ID
                #Note that the IF ID may not be sequential
                int(elems[0])
                #Extract the if name
                if len(elems) > 1:
                    ifName = elems[1].strip()
                    ifName = ifName.replace(":", "")
                    ifAddressList = []
                    if includeNoIPIF:
                        netIFDict[ifName] = ifAddressList
            except:
                line = line.strip()
                if line.startswith("inet "):
                    elems = line.split()
                    if len(elems) > 1:
                        ipAddress = elems[1]
                        ifAddressList.append(ipAddress)
                        netIFDict[ifName] = ifAddressList

        return netIFDict

    def getIFName(self, ipAddress):
        """@brief Get the name of the interface which the ip address can be reached directly (not via an IP gateway)
           @param ipAddress The IP address that should be out on an interface.
           @return The dict entry for the interface.
                   key == Interface name
                   value = Interface address.
           @return The name of the local network interface or None if not found."""
        ifDict = self.getIFDict()
        ifNames = list(ifDict.keys())
        ifNames.sort()
        for ifName in ifNames:
            ipDetailsList = ifDict[ifName]
            for ipDetails in ipDetailsList:
                elems = ipDetails.split(NetIF.IP_NETMASK_SEP)
                if len(elems) == 2:
                    ipAddr     = elems[0]
                    netMaskBits= int(elems[1])
                    netMask = NetIF.BitCountToNetMask(netMaskBits)
                    ipAddrInt  = NetIF.IPStr2int(ipAddr)
                    netMaskInt = NetIF.IPStr2int(netMask)
                    network = ipAddrInt&netMaskInt
                    networkStr = socket.inet_ntoa(struct.pack("!I", network))
                    netMaskInt=24
                    if NetIF.IsAddressInNetwork(ipAddress, "%s/%s" % ( networkStr, netMaskInt) ):
                        return ifName

        return None
    
    def _getIFDetails(self, ifName):
        """@brief Get the details of the network interface on this machine given the interface name.
           @param ifName The name of the interface.
           @return A tuple containing the tuples that contain
                  0: IP address
                  1: Netmask"""
        self.getIFDict()
        if ifName in self._ifDict:
            ifDetailsList = self._ifDict[ifName]
            for ifDetails in ifDetailsList:
                if ifDetails:
                    elems = ifDetails.split(NetIF.IP_NETMASK_SEP)
                    if len(elems) == 2:
                        return elems
        return None
    
    def getIFIPAddress(self, ifName):
        """@brief Get the IP address of the network interface on this machine given the interface name.
           @param ifName The name of the interface.
           @return The IP address oft heinterface of None if unknown."""
        ifDetails = self._getIFDetails(ifName)
        if ifDetails and len(ifDetails) == 2:
            return ifDetails[0]
            
        return None
    
    def getIFNetmask(self, ifName):
        """@brief Get the netmask of the network interface on this machine given the interface name.
           @param ifName The name of the interface.
           @return The IP address of the interface of None if unknown."""
        ifDetails = self._getIFDetails(ifName)
        if ifDetails and len(ifDetails) == 2:
            netMaskBitCount = int(ifDetails[1])
            return NetIF.BitCountToNetMask(netMaskBitCount)
            
        return None
    
    def _checkSupportedOS(self):
        """@brief Check that the OS is supported."""
        for supportedOSName in NetIF.SUPPORTED_OS_NAMES:
            if self._osName.find(supportedOSName) != -1:
                return
            
        raise Exception("%s: %s is an unsupported platform", type(self).__name__, self._osName)