#!/usr/bin/env python

from __future__ import print_function

# Prepare environment
import sys
pyxml=None
index = 0
for p in sys.path:
    if -1 != p.find('pyxml'):
         pyxml = p
    index += 1

if None != pyxml:
    sys.path.remove(pyxml)

import xml.etree.ElementTree as ET

import os
cert_dir = os.getenv('HOME') + '/.psquared/client/certs'

import requests
session=requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32)
session.mount('http://', adapter)

CERT = cert_dir + '/psquare_client.crt' #Client certificate
KEY = cert_dir + '/psquare_client.key' #Client private key
CACERT = cert_dir + '/psquare_cacert.crt' #CA certificates

if os.path.exists(CERT) and os.path.exists(CERT):
    session.cert = (CERT, KEY)
if os.path.exists(CACERT):
    session.verify = CACERT

HEADERS = {'Content-Type': 'application/xml',
           'Accept': 'application/xml'}
DEBUG = False
RESUBMISSION_LIMIT = 8

def eprint(*args, **kwargs):
    """Prints to standard error"""
    print(*args, file=sys.stderr, **kwargs)


# Simple pretty print for *IX
def pretty_print(uri, s, response = True):
    if DEBUG:
        if None != uri:
            if response:
                eprint('URI : Response : ' + uri)
            else:
                eprint('URI : Request :  ' + uri)
        os.system("echo '" + str(s) + "' | xmllint -format - 1>&2")
        eprint('--------')


class FatalError(Exception):
    def __init__(self, message, errorCode, response):
        self.code = errorCode
        self.message = message
        self.response = response


def checkStatus(uri, r, expected):
    if 400 == r.status_code:
        raise FatalError('Application at "' + uri  + '" requires SSL certificate', r.status_code, r.text)
    elif 401 == r.status_code:
        raise FatalError('Not authorized to execute commands for Application at "' + uri, r.status_code, r.text)
    elif 404 == r.status_code:
        raise FatalError('Application at "' + uri  + '" not found', r.status_code, r.text)
    elif expected != r.status_code:
        raise FatalError('Unexpected status (' + str(r.status_code) + ') returned from "' + uri  + '"', r.status_code, r.text)
    return


class PSquaredFailure(Exception):
    """
    Thrown when a RESTful does not complete as expected.
    """
    def __init__(self, message, errorCode):
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)
        self.code = errorCode
        self.message = message # JM 08/25/2020 


def get_attachment(message):
    """
    Returns the 'attachment' document that includes the supplied message, if any.
    """
    attachment = ET.Element('attachment')
    if None != message:
        msg = ET.Element('message')
        msg.text = message
        attachment.append(msg)
    return attachment


def execute_transition(uri, message):
    """
    Requests the PSquared instance create a new realized state.
    """
    # Prepare attachment document
    attachment = get_attachment(message)
    pretty_print(uri, ET.tostring(attachment), False)
    r = session.post(uri, data=ET.tostring(attachment), headers=HEADERS)
    if 404 == r.status_code:
        raise PSquaredFailure('Exit request "' + uri  + '" not found', r.status_code)
    elif 409 == r.status_code:
        raise PSquaredFailure('Another process has changed the processing of this request, so this attempt will halt', r.status_code)
    elif 201 != r.status_code:
        raise PSquaredFailure('Unexpected status (' + str(r.status_code) + ') returned from "' + uri  + '"', r.status_code)
    pretty_print(uri, r.text)
    return ET.fromstring(r.text)


def parse_submitted_response(state, resubmission_count):
    e=state.findall('exits/exit')
    if 0 == len(e):
        e=state.find('exited')
        if None == e:
            raise PSquaredFailure('Incomplete response returned from "' + uri  + '"', 1)
        if not 0 > resubmission_count:
            if 'executing' == e.find('name').text:
                if resubmission_count == RESUBMISSION_LIMIT:
                    raise PSquaredFailure('re-submission limit has been reached, so this attempt will halt', 409)
                return automatic_resubmission(e.find('uri').text, resubmission_count + 1)
            raise PSquaredFailure('State that follows submission does not allow automatic re-submission, so this attempt will halt', 409)
        raise PSquaredFailure('Another process has started processing this request, so this attempt will halt', 409)
    executingUri = None
    for exit in e:
        if 'executing' == exit.find('name').text:
            return exit.find('uri').text
    raise PSquaredFailure('Unexpected response returned from "' + uri  + '"', 1)


def automatic_resubmission(uri, resubmission_count):
    """
    Resubmits this request as its previous engine failed top complete.
    """
    try:
        r = session.get(uri)
    except ConnectionError as e:
        raise PSquaredFailure('Could not connect to server', -1)
    checkStatus(uri, r, 200)
    pretty_print(uri, r.text)
    state = ET.fromstring(r.text)
    e=state.findall('exits/exit')
    if 0 == len(e):
        e=state.find('exited')
        if None == e:
            raise PSquaredFailure('Incomplete response returned from "' + uri  + '"', 1)
        if 'reschedule' == e.find('name').text:
            return get_execution_uri(e.find('uri').text, resubmission_count)
        raise PSquaredFailure('Another process has processed this request, so this attempt will halt', 409)
    for exit in e:
       if 'reschedule' == exit.find('name').text:
           rescheduleUri = exit.find('uri').text
           break

    state = execute_transition(rescheduleUri,
                               'Rescheduling as previous execution died')
    e=state.findall('exits/exit')
    if 0 == len(e):
        raise PSquaredFailure('Failed to correctly reschedule submission')
    return parse_submitted_response(state, resubmission_count)


def get_execution_uri(uri, resubmission_count):
    """
    Returns the URI that will signal to PSqaured that processing has begun.
    """
    try:
        r = session.get(uri)
    except ConnectionError as e:
        raise PSquaredFailure('Could not connect to server', -1)
    checkStatus(uri, r, 200)
    pretty_print(uri, r.text)
    state = ET.fromstring(r.text)
    return parse_submitted_response(state,
                                    resubmission_count)
    

def processing_beginning(uri,
                         message):
    """
    Informs the PSquared instance that processing is beginning for this
    item/version pairing.
    """
    state = execute_transition(uri,
                               message)
    e=state.findall('exits/exit')
    for exit in e:
        if 'processed' == exit.find('name').text:
            processedUri = exit.find('uri').text
            break
    
    for exit in e:
        if 'failed' == exit.find('name').text:
            failedUri = exit.find('uri').text
            break
    
    return processedUri, failedUri


def process(cmd,
            params,
            cmd_out,
            cmd_err):
    """
    Processes the supplied command, return any message created by the command while
    it was executing.
    """
    import subprocess
    import tempfile
    args = []
    args.append(cmd)
    args.extend(params)
    fd, message_file = tempfile.mkstemp(text=True)
    cmd_env = os.environ.copy()
    cmd_env['PP_MESSAGE_FILE'] = message_file
    proc = subprocess.Popen(args,
                            env=cmd_env,
                            stdout=cmd_out,
                            stderr=cmd_err)
    result = proc.wait()
    message = os.fdopen(fd, 'r').read()
    os.remove(message_file)
    return result, message.strip()


def execute(message_for_execute,
            cmd,
            arguments,
            submission_uri,
            cmd_out,
            cmd_err,
            success_cmd,
            failure_cmd,
            resubmission):
    if resubmission:
        resubmission_count = 0
    else:
        resubmission_count = -1
    executingUri = get_execution_uri(submission_uri,
                                     resubmission_count)
    processedUri, failedUri = processing_beginning(executingUri,
                                                   message_for_execute)
    if None == arguments:
        params = []
    else:
        params = arguments
    if None == cmd:
        result, message = 0, 'No command supplied'
    else:
        try:
            result, message = process(cmd,
                                      params,
                                      cmd_out,
                                      cmd_err)
        except OSError as o:
            eprint(cmd, params)
            eprint('Failed to execute command')
            if None != o.errno:
                eprint('Error Number: ' + str(o.errno))
            if None != o.strerror:
                eprint('Explanation: ' + o.strerror)
            if None != o.filename:
                eprint('Filename: ' + o.filename)
            result, message = 255, 'Failed to execute command, check log file for details'
    if 0 == result:
        execute_transition(processedUri,
                           message)
        if None != success_cmd:
            try:
                process(success_cmd,
                        params,
                        cmd_out,
                        cmd_err)
            except OSError as o:
                raise PSquaredFailure('Failed to execute "success" command', 255)
    else:
        execute_transition(failedUri,
                           message)
        if None != failure_cmd:
            try:
                process(failure_cmd,
                        params,
                        cmd_out,
                        cmd_err)
            except OSError as o:
                raise PSquaredFailure('Failed to execute "failure" command', 255)


if __name__ == '__main__':
    import argparse
    import sys
    import socket
    import logging

    parser = argparse.ArgumentParser(description='Executes a command with the PSquared State machine.')
    parser.add_argument('-d',
                      '--debug',
                      dest='DEBUG',
                      help='print out detail information to stdout.',
                      action='store_true',
                      default=False)
    parser.add_argument('-e',
                        dest='ERROR',
                        help='The file, as opposed to stderr, into which to write errors from the command')
    parser.add_argument('--log_file',
                        dest='LOG_FILE',
                        help='The file, as opposed to stdout, into which to write log messages from the state machine')
    parser.add_argument('-o',
                        dest='OUTPUT',
                        help='The file, as opposed to stdout, into which to write output from the command')
    parser.add_argument('-s',
                      '--success_cmd',
                      dest = 'SUCCESS_CMD',
                      help = 'The command to run after a successful processing',
                      default = None)
    parser.add_argument('-f',
                      '--failure_cmd',
                      dest = 'FAILURE_CMD',
                      help = 'The command to run after a failed processing',
                      default = None)
    parser.add_argument('-r',
                      '--resubmission',
                      dest='RESUBMISSION',
                      help='allows automatic re-submission to take place.',
                      action='store_true',
                      default=False)
    parser.add_argument('submission_url',
                        help='The submission URL used to create the processing request to be handled')
    parser.add_argument('cmd',
                        help='The command to be executed')
    parser.add_argument('args',
                        nargs=argparse.REMAINDER,
                        help='An argument to the command to be executed')
    options = parser.parse_args()

    if options.DEBUG:
        log_level = logging.INFO
        DEBUG = True
    else:
        log_level = logging.WARNING
    if options.LOG_FILE:
        logging.basicConfig(filename=options.LOG_FILE,
                            level=log_level)
    else:
        logging.basicConfig(Stream=sys.stdout,
                            level=log_level)

    print('Beginning state machine execution')
    try:
        execute('Executing on ' + socket.gethostname() + ' using pp_engine.py',
                options.cmd,
                options.args,
                options.submission_url,
                options.OUTPUT,
                options.ERROR,
                options.SUCCESS_CMD,
                options.FAILURE_CMD,
                options.RESUBMISSION)
        print('Completed state machine execution')
    except FatalError as e:
        eprint(e.message)
        sys.exit(e.code)
