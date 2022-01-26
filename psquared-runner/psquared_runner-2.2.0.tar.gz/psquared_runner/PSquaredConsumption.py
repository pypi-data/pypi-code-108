#!/usr/bin/env python

# Prepare environment
import sys
from pika.frame import Body
pyxml=None
index = 0
for p in sys.path:
    if -1 != p.find('pyxml'):
         pyxml = p
    index += 1

if None != pyxml:
    sys.path.remove(pyxml)

import errno
def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise e

FILENAME_LENGTH_LIMIT = 255

import hashlib
import json
import os
import socket
import subprocess
import xml.etree.ElementTree as ET

import pp_engine

from rabbitmq_consume import StopWorkerException, StopListeningException

class PSquaredConsumption(object):

    def __init__(self,
                 properties,
                 body,
                 redelivered):
        self._body = body
        self._properties = properties
        # If redelivery is set the following to `redelivered` less set to `False`
        self._redelivered = False # redelivered

    def executionMessage(self):
        return 'Executing on ' + socket.gethostname()

    def consume(self):
        try:
            document = ET.fromstring(self._body)
            action = document.get('action')
            if 'stop_listening' == action:
                raise StopListeningException()
            if 'stop_worker' == action:
                raise StopWorkerException()
            if 'ignore' == action:
                print ('Ignoring execution request')
            else:
                element = document.find('submission_uri')
                if None != element:
                    submission_uri = element.text
                    cmd = document.find('command').text
                    args = document.findall('argument')
                    if 0 == len(args):
                        arguments = None
                    else:
                        arguments = []
                        for arg in args:
                            arguments.append(arg.text)
                    element = document.find('success_cmd')
                    if None == element or '' == element.text:
                        success_cmd = None
                    else:
                        success_cmd = element.text
                    element = document.find('failure_cmd')
                    if None == element or '' == element.text:
                        failure_cmd = None
                    else:
                        failure_cmd = element.text
                    attribute = document.get('stdout')
                    if None == attribute or '' == attribute:
                        cmd_out = None
                    else:
                        if attribute.startswith('/'):
                            filepath = attribute
                        else:
                            filepath = os.path.expanduser('~/' + attribute)
                        outDir = os.path.dirname(filepath)
                        if None != outDir and '' != outDir:
                            mkdirs(outDir)

                        # Temporary support for file name limit of FILENAME_LENGTH_LIMIT
                        outBase = os.path.basename(filepath)
                        if FILENAME_LENGTH_LIMIT < len(outBase):
                            outBase=str(hashlib.sha256(outBase).hexdigest())
                            if None != outDir and '' != outDir:
                                filepath=os.path.join(outDir, outBase)
                            else:
                                filepath=outBase
                        # End temporary support

                        cmd_out = open(filepath, 'w')
                    attribute = document.get('stderr')
                    if None == attribute or '' == attribute:
                        cmd_err = None
                    else:
                        if attribute.startswith('/'):
                            filepath = attribute
                        else:
                            filepath = os.path.expanduser('~/' + attribute)
                        errDir = os.path.dirname(filepath)
                        if None != errDir and '' != errDir:
                            mkdirs(errDir)

                        # Temporary support for file name limit of FILENAME_LENGTH_LIMIT
                        errBase = os.path.basename(filepath)
                        if FILENAME_LENGTH_LIMIT < len(errBase):
                            errBase=str(hashlib.sha256(errBase).hexdigest())
                            if None != errDir and '' != errDir:
                                filepath=os.path.join(errDir, errBase)
                            else:
                                filepath=errBase
                        # End temporary support

                        cmd_err = open(filepath, 'w')
                    print ('Beginning state machine completion')
                    pp_engine.execute(self.executionMessage(),
                                      cmd,
                                      arguments,
                                      submission_uri,
                                      cmd_out,
                                      cmd_err,
                                      success_cmd,
                                      failure_cmd,
                                      self._redelivered)
                    print ('Completed state machine')
        except StopListeningException as e:
            raise e
        except StopWorkerException as e:
            raise e
        except pp_engine.PSquaredFailure as e:
            print ('Failed to complete state machine')
            print ('Failed in PSquared:\n' + e.message, file=sys.stderr)
            #print >> sys.stderr, 'Failed in PSquared:\n' + e.message
            print ('END CONSUMPTION')
        except Exception as e:
            print ('Failed to complete state machine')
            print (e, file=sys.stderr)
            #print (e.message, file=sys.stderr)
            #print >> sys.stderr, e.message
            print ('ABORT CONSUMPTION')
