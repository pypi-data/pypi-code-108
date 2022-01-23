"""
decode single (binary) frames from file or commandline
and multiple frames from a CSV file
"""

from __future__ import print_function

import argparse
import binascii
import json
import re
import sys
from datetime import datetime

from kaitaistruct import KaitaiStructError

import satnogsdecoders.decode_frame as decode_frame
from satnogsdecoders import __version__ as decoders_version


class CliParameters(object):  # pylint: disable=R0903
    """
    Commandline parameters
    """
    def __init__(self, fname=None, hframe=None, fformat=None, tmstamp=None):
        self.fname = fname
        self.hframe = hframe
        self.fformat = fformat
        self.tmstamp = tmstamp


def main():
    """
    main entry point
    """

    parser = argparse.ArgumentParser(
        description='Decode single or multiple frames using a Kaitai'
        'Struct decoder into JSON objects.')
    parser.add_argument('decoder_name',
                        type=str,
                        help='Name of the decoder (e.g. Eshail2).')
    parser.add_argument('--filename',
                        type=str,
                        help='Filename containing the frame[s].')
    parser.add_argument('--hex_frame',
                        type=str,
                        help='Hexlified frame provided as argument like '
                        '"001122AABBCCDDEEFF".')
    parser.add_argument('--format',
                        type=str,
                        help="Input file format, 'bin' or 'csv'.")
    parser.add_argument(
        '--tmstamp',
        type=str,
        help='For single hex or bin frame: timestamp of the current frame.')
    parser.add_argument('-v',
                        action='store_true',
                        help='Enables verbose output mode.')
    args = parser.parse_args()
    parms = CliParameters(args.filename, args.hex_frame, args.format,
                          args.tmstamp)
    print(decode_multiple(args.decoder_name, parms, args.v))


def create_point(fields, timestamp, decoder, version):
    """
    Create a decoded data point in JSON format

    :returns: a JSON formatted time series data point
    """
    point = {
        'time': timestamp,
        'measurement': '',
        'tags': {
            'satellite': '',
            'decoder': decoder,
            'station': '',
            'observer': '',
            'source': '',
            'version': version
        },
        'fields': fields
    }

    return point


def check_valid_format(params):
    """
    Check if frame format in file is valid
    """
    if params.fformat not in ('bin', 'csv'):
        if params.hframe is None:
            print("Wrong input file format \'{}\'! Must be 'bin' or 'csv'!".
                  format(params.fformat),
                  file=sys.stderr)
            sys.exit(2)
    return True


def parse_csv_file(dname, params, json_obj, verbose):
    """
    Parser for CSV files
    """

    if params.fformat == 'csv':
        lines = [line.rstrip('\n') for line in open(params.fname)]
        for each_line in lines:
            try:
                # substitute newlines, " and carriage-return
                each_line = re.sub('["\r\n]', '', each_line)
                bindata = binascii.unhexlify(each_line[20:])
                if verbose == 1:
                    print('Decoding frame (l={}): {}\n'.format(
                        len(bindata), each_line[20:]),
                          file=sys.stderr)
                timestamp = each_line[:19]
                json_obj.append(
                    create_point(decode_frame.decode_frame(dname, bindata),
                                 timestamp, dname, decoders_version))
            # pylint: disable=broad-except
            except (Exception, KaitaiStructError) as error:
                if verbose is True:
                    print('^~~~ Invalid frame!', file=sys.stderr)
                    print(error, file=sys.stderr)
    return json_obj


def parse_bin_file(dname, params, json_obj):
    """
    Parser for binary files
    """
    if params.fformat == 'bin':
        with open(params.fname, 'rb') as file_t:
            bindata = bytearray(file_t.read())
            if params.tmstamp is not None:
                timestamp = params.tmstamp
            else:
                timestamp = datetime.strftime(datetime.now(),
                                              '%Y-%m-%d %H:%M:%S')
                json_obj.append(
                    create_point(decode_frame.decode_frame(dname, bindata),
                                 timestamp, dname, decoders_version))
    return json_obj


def parse_hex_frame(dname, params, json_obj):
    """
    Parser for hex frames
    """
    if params.hframe is not None:
        frame = re.sub('["\r\n]', '', params.hframe)
        bindata = binascii.unhexlify(frame)
        if params.tmstamp is not None:
            timestamp = params.tmstamp
        else:
            timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        json_obj.append(
            create_point(decode_frame.decode_frame(dname, bindata), timestamp,
                         dname, decoders_version))
    return json_obj


def decode_multiple(dname, params, verbose=False):
    """
    Functional code goes here:
    """
    check_valid_format(params)
    json_obj = []
    if params.fname is not None:
        if verbose is True:
            print('Input file is: {}'.format(params.fname), file=sys.stderr)
    parse_csv_file(dname, params, json_obj, verbose)
    parse_bin_file(dname, params, json_obj)
    parse_hex_frame(dname, params, json_obj)
    return json.dumps(json_obj, indent=4, sort_keys=False)
