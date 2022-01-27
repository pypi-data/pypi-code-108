# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.libs.sp_serial"""

import logging
import socket

from time import sleep

import serial
from xmodem import XMODEM


LOG = logging.getLogger("sp_serial.%s" % __name__)

class SPSerial(object): # pylint: disable=useless-object-inheritance
    def __init__(self,
                 port               = None,
                 baudrate           = 9600,
                 bytesize           = 8,
                 parity             = 'N',
                 stopbits           = 1,
                 timeout            = None,
                 xonxoff            = False,
                 rtscts             = False,
                 writeTimeout       = None,
                 dsrdtr             = False,
                 eol                = '\r'):

        if port.find(":") == -1:
            LOG.debug("Using serial port %r", port)
            self.mode = 'Serial'
            self.serial = serial.Serial(
                port         = port,
                baudrate     = baudrate,
                bytesize     = bytesize,
                parity       = parity,
                stopbits     = stopbits,
                timeout      = timeout,
                xonxoff      = xonxoff,
                rtscts       = rtscts,
                writeTimeout = writeTimeout,
                dsrdtr       = dsrdtr)
        else:
            LOG.debug("Using tcp port %r", port)
            self.mode = 'TCP'
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host, tcpport = port.split(':')
            self.socket.connect((socket.gethostbyname(host), int(tcpport)))
            self.socket.settimeout(1) #1s
            self.serial = self.socket.makefile()

        self.eol            = eol
        self.progressbar    = None
        self.progresslen    = 0
        self.timeout        = None

    def read(self, size):
        if self.mode == 'Serial':
            return self.serial.read(size)
        return self.socket.recv(size)

    def readline(self):
        if self.mode == 'Serial':
            return self.serial.readline()
        line = c = ""
        try:
            while c != "\n":
                c = self.socket.recv(1)
                line += c
        except socket.timeout:
            pass
        return line


    def write(self, data):
        r = self.serial.write(data)
        self.serial.flush()
        return r

    def writeline(self, data):
        LOG.debug("TX: %r", data)
        return self.write(data + self.eol)

    def sendBreak(self, duration = 1):
        if self.mode == 'Serial':
            return self.serial.sendBreak(duration)
        return self.write("\xFF\xF3") # Break IAC as defined in Telnet RFC

    def setTmpTimeout(self, timeout):
        if self.mode == 'Serial':
            self.timeout = self.serial.timeout
            if timeout is not None:
                self.serial.timeout = timeout
        else:
            self.timeout = self.socket.gettimeout()
            if timeout is not None:
                self.socket.settimeout(timeout)

    def restoreTimeout(self):
        if self.mode == 'Serial':
            if self.timeout is not None:
                self.serial.timeout = self.timeout
        else:
            if self.timeout is not None:
                self.socket.settimeout(self.timeout)

    def readlinesuntil(self, data = None, timeout = None):
        self.setTmpTimeout(timeout)

        def serial_port_reader():
            while True:
                x   = self.readline()
                if x == '':
                    continue
                LOG.debug("RX: %r", x)

                x   = x.strip()

                if x.find(data) > -1:
                    break
                yield x

        r = ''.join(serial_port_reader())

        self.restoreTimeout()

        return r

    def readuntil(self, data = None, timeout = None):
        if not data:
            size    = 1
        else:
            size    = len(data)

        self.setTmpTimeout(timeout)

        def serial_port_reader():
            while True:
                tmp = self.read(size)
                LOG.debug("RX: %r", tmp)
                if not tmp or (data and data == tmp):
                    break
                yield tmp

        r = ''.join(serial_port_reader())

        self.restoreTimeout()

        return r

    def getc(self, size, timeout=1): # pylint: disable=unused-argument
        r = self.read(size)
        LOG.debug("RXc: %d", r)
        return r

    def putc(self, data, timeout=1): # pylint: disable=unused-argument
        LOG.debug("TXc: %d", data)
        r = self.write(data)
        sleep(0.001)

        if self.progressbar:
            self.progresslen += len(data)
            if self.progresslen <= self.progressbar.maxval:
                self.progressbar.update(self.progresslen)

        return r

    def xmodem(self, progressbar=None, mode = 'xmodem', pad = '\x1a'):
        self.progressbar = progressbar
        self.progresslen = 0

        return XMODEM(getc = self.getc, putc = self.putc, mode = mode, pad = pad)
