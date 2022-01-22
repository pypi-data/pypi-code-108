#!/usr/bin/env python3

from netdevice import linux
import simplejson as json
import pexpect
import xmltodict
import sys

class CiscoDevice(linux.LinuxDevice):
    '''
    A base class for common Cisco device.
    '''
    version = '0.1'
    def __init__(self, device = None, **kwargs):

        linux.LinuxDevice.__init__(self, device, **kwargs)
        self.log('Not support yet.')

