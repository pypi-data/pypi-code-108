#! /usr/bin/python3

import argparse
import logging

import globalnoc.wsc


def kv(value):
    if not '=' in value:
        raise argparse.ArgumentTypeError("%s is a key=value" % value)
    return value


parser = argparse.ArgumentParser()
URLgroup = parser.add_mutually_exclusive_group(required=True)
URLgroup.add_argument("-U", "--url", help="URL to request")
URLgroup.add_argument("-S", "--service", help="URN of Service to request")

authgroup = parser.add_argument_group()
authgroup.add_argument(
    "-u", "--username", help="Username for basic auth or ECP")
authgroup.add_argument(
    "-P", "--password", help="Password for basic auth or ECP")
authgroup.add_argument(
    "-r", "--realm", help="Realm. For ECP requests, this should be the IdP's ECP endpoint. e.g. https://idp.somebody.edu/idp/profile/SAML2/SOAP/ECP")

parser.add_argument("-m", "--method", default='help',
                    help="GlobalNOC WS 'method' parameter. Default: 'help'")
parser.add_argument("-a", "--args", action='append', default=[], type=kv,
                    help='Arguments to send to remote service in key=value form. May be specified more than once.')
parser.add_argument('-t', '--timeout', type=int, help='Timeout in seconds')
#parser.add_argument('-k', '--keepalive', action='store_true', help="Enable keepalives")
parser.add_argument('-o', '--raw', action='store_true',
                    help='Pass raw output rather than decode JSON')
parser.add_argument(
    '-l', '--cookies', help='Path to cookies file to read on load, and write before exit')

cachegroup = parser.add_mutually_exclusive_group()
cachegroup.add_argument('-c', '--servicecache',
                        help="Path to name service cache file")
# cachegroup.add_argument('-n', '--nameservice', help="URL for name service directory")

parser.add_argument('-X', '--noresult', action='store_true',
                    help="Do not print the results of the webservice call")
parser.add_argument('-D', '--debug', action='store_true',
                    help="Print debug logs")

args = parser.parse_args()

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.DEBUG if args.debug else logging.WARN)

w = globalnoc.wsc.WSC()

if args.username:
    if not args.password:
        import getpass
        args.password = getpass.getpass()
    w.username = args.username
    w.password = args.password
    if args.realm:
        w.realm = args.realm

if args.url:
    w.url = args.url
else:
    if args.servicecache:
        w.ns = args.servicecache
    w.urn = args.service

if args.timeout:
    w.timeout = args.timeout

w.raw = args.raw

if args.cookies:
    try:
        w._load(args.cookies)
    except:
        if not args.noresult:
            print("Problem loading cookies. Continuing without any.")

res = w.__getattr__(args.method)(**dict([a.split('=', 1) for a in args.args]))

if not args.noresult:
    if args.raw:
        print(res)
    else:
        import pprint
        pprint.pprint(res)

if args.cookies:
    try:
        w._save(args.cookies)
    except:
        if not args.noresult:
            print("Problem saving cookies.")
