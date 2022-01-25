#!/usr/bin/python3

"""

NAME     - metagen
SYNOPSIS - Adds metadata.xml to current directory
AUTHOR   - Rob Cakebread <cakebread@gmail.com>
AUTHOR   - Jesus Rivero <neurogeek@gentoo.org>
USE      - metagen --help
EXAMPLES - man metagen

"""

import re
import os
import sys
import tempfile
from argparse import ArgumentParser
from subprocess import getstatusoutput
from textwrap import dedent

from portage import config
from portage.exception import FileNotFound
from portage.output import red, blue, yellow

from metagen.version import __version__
from metagen import metagenerator

PORTDIR = config(local_config=False)["PORTDIR"]

# GLEP 67
_MAINTAINER_TYPE_PERSON = 'person'
_MAINTAINER_TYPE_PROJECT = 'project'
_MAINTAINER_TYPE_UNKNOWN = 'unknown'
_VALID_MAINTAINER_TYPES = (_MAINTAINER_TYPE_PERSON, _MAINTAINER_TYPE_PROJECT, _MAINTAINER_TYPE_UNKNOWN)

def parse_echangelog_variable(name, email):
    """Extract developer name and email from ECHANGELOG_USER variable"""
    try:
        e = os.environ["ECHANGELOG_USER"]
    except KeyError:
        print(red("!!! Environmental variable ECHANGELOG_USER not set."))
        print(red("!!! Set ECHANGELOG_USER or use -e and -n"))
        sys.exit(1) 
    try:
        my_email = e[e.find("<") +1:e.find(">")]
    except:
        print(red("!!! ECHANGELOG_USER not set properly"))
        sys.exit(1) 
    try:
        my_name = e[0:e.find("<")-1]
    except:
        print(red("!!! ECHANGELOG_USER not set properly"))
        sys.exit(1) 
    if email:
        email = "%s,%s" % (my_email, email)
    else:
        email = my_email
    if name:
        name = "%s,%s" % (my_name, name)
    else:
        name = my_name
    return name, email

def generate_xml(options):
    """Returns metadata.xml text"""

    metadata = metagenerator.MyMetadata()

    if options.echangelog:
        (options.name, options.email) = \
            parse_echangelog_variable(options.name, options.email)

    if options.email:
        names, descs = [], []
        if options.name:
            names = options.name.split(",")
        if options.desc:
            descs = options.desc.split(",")
        maintainer_types = options.maintainer_type.split(",")
        metadata.set_maintainer(options.email.split(","),
                                names,
                                descs,
                                maintainer_types,
                                )

    if options.long:
        metadata.set_longdescription(options.long)

    return "%s" % metadata

def validate_xml(my_xml):
    """Test for valid XML"""
    #TODO validate against DTD
    #This just makes sure its valid XML of some sort.
    #Probably not necessary since repoman validates against DTD?
    re_escape_quotes = re.compile('"')
    s = re_escape_quotes.sub('\\"', my_xml)
    cmd = "echo \"%s\" | xmllint --valid - 2>&1 > /dev/null" % s
    return getstatusoutput(cmd)[0]


def _check_maintainer_type_list(text):
    for candidate in text.split(','):
        if candidate not in _VALID_MAINTAINER_TYPES:
            raise ValueError('"%s" not a valid maintainer type' % candidate)
    return text

_check_maintainer_type_list.__name__ = 'maintainer type'


def main():
    parser = ArgumentParser(prog='metagen')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    maintainer = parser.add_argument_group(title='maintainer arguments')
    maintainer.add_argument("--email", "-e", action="store",
                         help="Maintainer's email address")
    maintainer.add_argument("--name", "-n", action="store",
                         help="Maintainer's name")
    maintainer.add_argument("--echangelog", "-m", action="store_true",
                         default=False,
                         help="Use name and email address from ECHANGELOG_USER "+
                         "environmental variable. "+
                         "This is a shortcut for -e <email> -n <name>")
    maintainer.add_argument("--desc", "-d", action="store",
                         help="Description of maintainership")
    maintainer.add_argument("--type", "-t", dest='maintainer_type', metavar='TYPE',
                         type=_check_maintainer_type_list,
                         help="Maintainer type as of GLEP 67; valid values are: %s" \
                             % ', '.join('"%s"' % e for e in _VALID_MAINTAINER_TYPES))

    package = parser.add_argument_group(title='package arguments', description=None)
    package.add_argument("--long", "-l", action="store",
                         help="Long description of package.")

    operation = parser.add_argument_group(title='operation arguments', description=None)
    operation.add_argument("--output", "-o", action="store",
                         help="Specify location of output file.")
    operation.add_argument("--force", "-f", action="store_true", default=False,
                         help="Force overwrite of existing metadata.")
    operation.add_argument("--verbose", "-v", action="store_true", default=True,
                         help="Verbose. Output of file to stdout. (default)")
    operation.add_argument("--quiet", "-q", action="store_false", dest="verbose",
                         help="Squelch output of file to stdout.")
    operation.add_argument("-Q", action="store_true", dest="no_write",
                         default=False,
                         help="Do not write file to disk.")

    options = parser.parse_args()

    if options.desc or options.name:
        if not options.email and not options.echangelog:
            print(red("!!! No maintainer's email address specified."))
            print(red("!!! Options -d and -n are only valid with -e or -m"))
            sys.exit(1)
 
    if not options.email and not options.echangelog:
        print(red("!!! You must specify --echangelog|-m " +
                  "or maintainer's email address (-e)\n"))
        sys.exit(1)

    if (options.email or options.echangelog) and not options.maintainer_type:
        print(red("!!! No maintainer type specified. Please pass one of the following, in addition:"))
        for candidate in _VALID_MAINTAINER_TYPES:
            print(red("!!!   --type %s" % candidate))
        sys.exit(1)

    txt = generate_xml(options)

    error_status = validate_xml(txt)
    if error_status < 0:
        print(red("!!! Error - Invalid XML"))
        print(red("!!! Please report this bug with the options you used and the output:"))
        print(error_status)
        print(txt)
        sys.exit(1)

    if options.verbose:
        print("\n%s" % txt)

    out_file = "./metadata.xml"
    if options.output:
        out_file = options.output
    if not options.no_write and os.path.exists(out_file):
        if not options.force:
            print(red("!!! File %s exists." % out_file))
            print(red("!!! Use -f to force overwrite."))
            sys.exit(1)
    if not options.no_write:
        open("%s" % out_file, "w").writelines(txt)
        print(blue("%s written") % out_file)


if __name__ == '__main__':
    main()
