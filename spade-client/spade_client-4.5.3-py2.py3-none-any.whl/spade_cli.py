#
# Module: spade-cli
#
# Description: SPADE command line interface
#

from __future__ import print_function

import sys
def _eprint(*args, **kwargs):
    """Prints to standard error"""
    print(*args, file=sys.stderr, **kwargs)

import os
from spade_client import Spade, Display, ApplicationFunction, BundlesFunction, TicketsFunction, TimingFunction, FatalError

import argparse
import datetime
import re

class validateXMLDateTime(argparse.Action):
    """Checks that a string is is ISO8601 compliant"""

    def __call__(self, parser, namespace, values, option_string=None):
        prog = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]{1,3})?(Z|((\+|-)[0-9]{2}(:)?([0-9]{2})))?)?$')
        if None == prog.match(values):
            raise argparse.ArgumentError(self, 'invalid XML DataTime value: ' + values)
        setattr(namespace, self.dest, values)


def create_server_parser():
    parser = argparse.ArgumentParser(description='Command Line interface to SPADE.', add_help=False)
    parser.add_argument('-d',
                        '--debug',
                        dest='DEBUG',
                        help='print out RESTful documents.',
                        action='store_true',
                        default=False)
    parser.add_argument('-v',
                        '--version',
                        dest='VERSION',
                        help='print out the version information of the application.',
                        action='store_true',
                        default=False)
    parser.add_argument('--cert',
                        dest = 'CERTIFICATE',
                        help = 'path to the client\'s x509 certificate, if different from the default,'
                        + ' ${HOME}/.spade/client/cert/spade_client.pem',
                        default = None)
    parser.add_argument('--key',
                        dest = 'KEY',
                        help = 'path to the client\'s private x509 key, if different from the default,'
                        + ' ${HOME}/.psquared/client/private/psquare_client.key',
                        default = None)
    parser.add_argument('--cacert',
                        dest = 'CA_CERTIFICATE',
                        help = 'path to the file containing one or more CA x509 certificates, if different from the default,'
                        + ' ${HOME}/.spade/client/cert/cacert.pem',
                        default = None)
    parser.add_argument('-k',
                        '--insecure',
                        dest = 'INSECURE',
                        help = 'Allow insecure server connections when using SSL',
                        action='store_true',
                        default = None)
    return parser


def extend_names_and_descriptions(application, xpath, resource_names, resource_descriptions):
        named_resources = application.findall(xpath)
        for named_resource in named_resources:
            name = named_resource.find('name').text
            try:
                named_resource.attrib["deprecated"]
            except KeyError:
                resource_names.append(name) 

                descriptionElement = named_resource.find('description')
                if None == descriptionElement:
                    description = ''
                else:
                    description = ' : ' + descriptionElement.text
                resource_descriptions.append('  ' + name + description)
        return resource_names, resource_descriptions


from copy import deepcopy

def get_named_resource_data(application, report_xpath, command_xpath):
    """
    Creates the Displays the name and description of all named resources in the specified xpath

    :param ElementTree application: the application document whose resources should be displayed.
    :param arresource_descriptionsray xpath: the XPath elements used to extract the resources.
    """
    xpaths = [report_xpath, command_xpath]
    resource_names = []
    resource_descriptions = []
    resource_names, resource_descriptions = extend_names_and_descriptions(application,
                                                                          report_xpath,
                                                                          resource_names,
                                                                          resource_descriptions)
    resource_names, resource_descriptions = extend_names_and_descriptions(application,
                                                                          command_xpath,
                                                                          resource_names,
                                                                          resource_descriptions)

    if 0 == len(resource_descriptions):
        return None, None
    else:
        epilog = """permitted bundle operations:
"""
        for resource in resource_descriptions:
            epilog = epilog + resource + """
"""
    return resource_names, epilog


def create_resource_subparser(subparsers, application, topic, func, parents):
        reports_xpath = 'reports/[name="' + topic + '"]/action'
        commands_xpath = 'commands/[name="' + topic + '"]/action'
        resource_choices, resource_epilog = get_named_resource_data(application,
                                                                    reports_xpath,
                								                    commands_xpath)
        if parents:
            parents_to_use = parents
        else:
            parents_to_use = []
        parser = subparsers.add_parser(topic,
                                       help='Executes operation on a set of specified ' + topic,
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       epilog=resource_epilog,
                                       parents=parents_to_use)
        parser.add_argument(topic + '_operation',
                            help='The operation to execute (see below)',
                            choices=resource_choices)
        parser.set_defaults(func=func)
        parser.set_defaults(reports_xpath=reports_xpath)
        parser.set_defaults(commands_xpath=commands_xpath)


def application_operation(spade, options, application):
    application_function = ApplicationFunction(spade.session, options.DEBUG);
    if "summary" == options.application_operation:
        Display.status(application)
        return
    if spade.execute_named_resource(application,
                                    options.reports_xpath,
                                    options.application_operation,
                                    application_function.report):
        return
    spade.execute_named_resource(application,
                                 options.commands_xpath,
                                 options.application_operation,
                                 application_function.command)


def create_bundles_options():
    parser = argparse.ArgumentParser(description='Commands that operate on a list of bundles',
                                                  add_help=False)
    parser.add_argument('-b',
                        '--bundle',
                        dest='BUNDLE',
                        help='applies the commands to the specified bundle, if applicable. May be specified multiple times for some commands.',
                        action='append')
    parser.add_argument('--file_bundles',
                        dest='FILE_BUNDLES',
                        help='specified the file from which to read a set of bundles to which the commands will be applied.',
                        type=argparse.FileType('r'))
    return parser


def bundle_operation(spade, options, application):
    if (None != options.BUNDLE and 0 != len(options.BUNDLE)) or None != options.FILE_BUNDLES:
        if None == options.FILE_BUNDLES:
            bundles_function = BundlesFunction(options.BUNDLE, spade.session, options.DEBUG)
        else:
            bundles = [x.strip('\n') for x in options.FILE_BUNDLES.readlines()]
            if None != options.BUNDLE and 0 != len(options.BUNDLE):
                bundles.extend(options.BUNDLE)
            bundles_function = BundlesFunction(bundles, spade.session, options.DEBUG)
    else:
        bundles_function = BundlesFunction(None, spade.session, options.DEBUG);

    if spade.execute_named_resource(application,
                                    options.reports_xpath,
                                    options.bundles_operation,
                                    bundles_function.report):
        return
    spade.execute_named_resource(application,
                                 options.commands_xpath,
                                 options.bundles_operation,
                                 bundles_function.command)


def create_tickets_options():
    parser = argparse.ArgumentParser(description='Commands that operate on a list of bundles',
                                                  add_help=False)
    parser.add_argument('-t',
                        '--ticket',
                        dest='TICKET',
                        help='applies the commands to the specified ticket, if applicable. May be specified multiple times for some commands.',
                        action='append')
    parser.add_argument('--file_tickets',
                        dest='FILE_TICKETS',
                        help='specified the file from which to read a set of tickets to which the commands will be applied.',
                        type=argparse.FileType('r'))
    return parser


def ticket_operation(spade, options, application):
    if (None != options.TICKET and 0 != len(options.TICKET)) or None != options.FILE_TICKETS:
        if None == options.FILE_TICKETS:
            tickets_function = TicketsFunction(options.TICKET, spade.session, options.DEBUG)
        else:
            tickets = [x.strip('\n') for x in options.FILE_TICKETS.readlines()]
            if None != options.TICKET and 0 != len(options.TICKET):
                tickets.extend(options.TICKET)
            tickets_function = TicketsFunction(tickets, spade.session, options.DEBUG)
    else:
        tickets_function = TicketsFunction(None, spade.session, options.DEBUG);

    if spade.execute_named_resource(application,
                                    options.reports_xpath,
                                    options.tickets_operation,
                                    tickets_function.report):
        return
    spade.execute_named_resource(application,
                                 options.commands_xpath,
                                 options.tickets_operation,
                                 tickets_function.command)


def create_timing_options():
    parser = argparse.ArgumentParser(description='Commands that return a set of timings',
                                                  add_help=False)
    after = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1, minutes=0)
    parser.add_argument('--after',
                        dest = 'AFTER',
                        help = 'the time on or after which entries should be include in the returned list.',
                        default = after.isoformat(timespec='milliseconds'),
                        action = validateXMLDateTime)
    parser.add_argument('--before',
                        dest = 'BEFORE',
                        help = 'the time before which items should be include in the returned list.')
    parser.add_argument('--limit',
                        dest = 'LIMIT',
                        type = int,
                        help = 'the limit on the number of items in the returned list.')
    parser.add_argument('--neighbor',
                        dest = 'NEIGHBOR',
                        help = 'only include timing to the specified neighbor in the returned list.')
    parser.add_argument('--registration',
                        dest = 'REGISTRATION',
                        help = 'only include timing to the specified registrations in the returned list, more than one can be specified.',
                        action="append")
    return parser


def timing_operation(spade, options, application):
    timing_function = TimingFunction(options.AFTER,
                                     options.BEFORE,
                                     options.LIMIT,
                                     options.NEIGHBOR,
                                     options.REGISTRATION,
                                     spade.session,
                                     options.DEBUG);
    spade.execute_named_resource(application,
                                 options.reports_xpath,
                                 options.timing_operation,
                                 timing_function.report)


def main():
    server_parser = create_server_parser()

    options, ignore = server_parser.parse_known_args()

    url = os.getenv('SPADE_APPLICATION', 'http://localhost:8080/spade/local/report/')
    if None == options.INSECURE:
        verify = None
    else:
        verify = not options.INSECURE
    spade = Spade(url,
                  xml=options.DEBUG,
                  cert = options.CERTIFICATE,
                  key = options.KEY,
                  cacert = options.CA_CERTIFICATE,
                  verify = verify )

    if options.DEBUG:
        spade.debug_separator()

    try:
        application = spade.get_application()
        parser = argparse.ArgumentParser(parents=[server_parser])
        subparsers = parser.add_subparsers(help='sub-command help')
        
        create_resource_subparser(subparsers,  application, 'application', application_operation, None)

        create_resource_subparser(subparsers,  application, 'bundles', bundle_operation, [create_bundles_options()])

        create_resource_subparser(subparsers,  application, 'tickets', ticket_operation, [create_tickets_options()])

        # Need to apply limits to this topic       
        create_resource_subparser(subparsers,  application, 'timing', timing_operation, [create_timing_options()])
        
        options = parser.parse_args()
        if "func" in options:
            options.func(spade, options, application)
            return
        options.application_operation = "summary"
        application_operation(spade, options, application)

    except FatalError as e:
        _eprint(e.message)
        sys.exit(e.code)


if __name__ == '__main__':
    main()
