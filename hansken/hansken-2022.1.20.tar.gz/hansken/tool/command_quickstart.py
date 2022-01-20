# encoding=utf-8

from datetime import date
from shlex import quote
import warnings

from logbook import Logger
import requests
from requests.exceptions import SSLError

from hansken import __version__
from hansken.auth import get_idps, is_keycloak_idp, kerberos_available, probe_openam_idp, SAML_SOAP_NS
from hansken.tool import add_command


log = Logger(__name__)


def prompt(name):
    """
    Prompts the user for a value for *name*. Keyboard interrupt / end of file
    is treated as a user abort.

    :param name: pretty, user-readable name for the requested value
    :return: a value for *name*, supplied by the user
    :raise SystemExit: when prompt is aborted by the user
    """
    try:
        value = None
        while not value:
            value = input('> enter {}: '.format(name)).strip()

        return value
    except (EOFError, KeyboardInterrupt):
        log.info('value prompt for {} aborted by user', name)
        raise SystemExit('aborted')


def select(name, options):
    """
    Lets the user select a value from provided options.

    :param name: pretty, user-readable name for the requested value
    :param options: `dict` of alternatives containing name and value to choose
        from
    :return: a value for *name*, chosen by the user from *choices*
    :raise SystemExit: when prompt is aborted by the user
    """
    try:
        # turn options into a structure where we can retrieve a choice based on a number
        options = sorted(options.items())
        print('select a {} from the following options'.format(name))  # nosec
        # present options as 1-based list
        for num, (key, description) in enumerate(options, start=1):
            print('  {}: {} ({})'.format(num, description, key))

        # keep asking for a value until user supplies a number between 1 and the number of options
        value = None
        while not value:
            value = input('> select {}: '.format(name)).strip()
            if not value.isdigit() or int(value) < 1 or int(value) > len(options):
                print('please choose a number between 1 and {}'.format(len(options)))
                value = None

        # turn 1-based choice into 0-based index
        value = int(value) - 1
        # return the 'key' portion of the choice
        return options[value][0]
    except (EOFError, KeyboardInterrupt):
        log.info('value choice for {} aborted by user', name)
        raise SystemExit('aborted')


def confirm(name, value, fallback=None, options=None):
    """
    Ask the user to confirm *value* to be used for *name*. No input assumes
    confirmation, keyboard interrupt / end of file is treated as a user abort.

    :param name: pretty, user-readable name for the value to be confirmed
    :param value: the value to be confirmed
    :param fallback: value to be used when user chooses 'no' (`.prompt` will
        be used if *fallback* is `None`)
    :param options: `dict` of alternatives to choose from, or `None` (used by
        `.select`)
    :return: a value for *name*, either confirmed or supplied by the user
    :raise SystemExit: when confirmation is aborted by the user
    """
    choice = None
    while not choice or choice not in 'ynq':
        try:
            # use first letter of user input as choice, default to 'y'
            choice = input('> does this look correct ([y]/n/q)? ').strip()[:1].lower() or 'y'
        except (EOFError, KeyboardInterrupt):
            # interpret ^C / ^D as user abort
            choice = 'q'

    if choice == 'q':
        log.info('value confirmation for {} aborted by user', name)
        raise SystemExit('aborted')
    elif choice == 'n':
        if fallback is None:
            # only prompt when no fallback for 'n' was provided
            log.debug('value {} for {} deemed incorrect by user, prompting for value', value, name)
            return select(name, options) if options else prompt(name)
        else:
            log.debug('value {} for {} deemed incorrect by user, falling back to {}', value, name, fallback)
            return fallback

    return value


def run_quickstart_command(args):
    print('this is hansken.py, version', __version__)
    print('hansken quickstart will help you to configure a few things by asking you to provide or confirm values '
          'hansken.py needs to communicate with Hansken and authenticate you')
    print('default answers to questions will be marked with square brackets, use ^C or ^D to quit at any time')

    print()
    print('first order of business: the endpoint of the Hansken REST API')
    if args.endpoint:
        print('the following endpoint was either already in your environment or supplied on the command line:')
        print('  {}'.format(args.endpoint))
        args.endpoint = confirm('hansken REST API endpoint', args.endpoint)
    else:
        print('no pre-configured endpoint was found, please supply the Hansken REST API endpoint '
              '(this typically ends with "/gatekeeper")')
        args.endpoint = prompt('Hansken REST API endpoint')

    log.info('endpoint to be used: {}', args.endpoint)

    if args.endpoint.startswith('https'):
        try:
            requests.get(args.endpoint, verify=True)
            # no error from requests, verify can be left/set at True
            args.verify = True
        except SSLError:
            print('it seems the REST API endpoint at {} uses an invalid certificate'.format(args.endpoint))
            args.verify = confirm('certificate verification', value=False, fallback=True)

    print()
    idps = get_idps(args.endpoint, verify=args.verify)
    if idps:
        print("next up: information we'll need to authenticate ourselves, also known as the identity prover, or IDP")
        if args.idp and args.idp in idps:
            # pre-configured value is available
            print('the following IDP was either already in your environment or supplied on the command line:')
            print('  {}'.format(args.idp))
            args.idp = confirm('identity provider', args.idp, options={
                key: value.get('description') for key, value in idps.items()
            })
        elif args.idp:
            # pre-configured value is not available
            print('the pre-configured value {} is not or no longer available at {}'.format(args.idp, args.endpoint))
            args.idp = None

        if idps and not args.idp:
            print('no usable pre-configured identity provider was found, '
                  'please pick one the available identity providers')
            args.idp = select('identity provider', options={
                key: value.get('description') for key, value in idps.items()
            })

        log.info('idp to be used: {}', args.idp)

        if args.idp:
            # we'll be using an IDP, check to see if we'll be needing kerberos (…)
            idp_url = idps[args.idp]['signOnServices'][SAML_SOAP_NS]
            if not is_keycloak_idp(idp_url):
                idp_realm, sso_url = probe_openam_idp(idp_url, verify=args.verify)
                if sso_url and not kerberos_available:
                    # (…) and error+exit if we do and the required dependency for it is not installed
                    print('the selected identity provider uses Kerberos authentication, '
                          'which is not currently available')
                    print('make sure to install the hansken.py kerberos extra '
                          '(pip install hansken.whl[kerberos])')
                    quickstart_parser.error('missing runtime dependency for kerberos authentication')
    else:
        print('the selected endpoint does not seem to know any identity providers, no authentication will be used')

    print()
    if args.keystore:
        print('the following keystore endpoint was either already in your environment or supplied on the command line:')
        print('  {}'.format(args.keystore))
        args.keystore = confirm('Hansken keystore endpoint', args.keystore)
    else:
        print('no pre-configured keystore endpoint was found, please supply the Hansken keystore endpoint '
              '(this typically ends with "/keystore")')
        args.keystore = prompt('Hansken keystore endpoint')

    log.info('keystore endpoint to be used: {}', args.keystore)

    print()
    if args.preference:
        print('the following preference service endpoint was either already in your environment or supplied on the '
              'command line:')
        print('  {}'.format(args.preference))
        args.preference = confirm('Hansken preference service endpoint', args.preference)
    else:
        print('no pre-configured preference service endpoint was found, please supply the Hansken preference service '
              'endpoint (this typically ends with "/preference-service")')
        args.preference = prompt('Hansken preference service endpoint')

    log.info('preference service endpoint to be used: {}', args.preference)

    argfile = [
        '# argument file generated by "hansken quickstart" on {}, version {}'.format(date.today(), __version__),
        '# the endpoint for the Hansken REST API',
        '--endpoint {}'.format(quote(args.endpoint)),
    ]
    if args.idp:
        argfile.extend([
            "# the 'name' of the identity provider to use",
            '--idp {}'.format(quote(args.idp))
        ])
    argfile.extend([
        '# the endpoint for the Hansken keystore REST API',
        '--keystore {}'.format(quote(args.keystore))
    ])
    argfile.extend([
        '# the endpoint for the Hansken preference service REST API',
        '--preference {}'.format(quote(args.preference))
    ])
    if not args.verify:
        argfile.extend([
            '# disable certificate verification',
            '# (one or more of the configured endpoints use invalid certificates)',
            '--no-verify'
        ])
    argfile = '\n'.join(argfile)

    print('quickstart completed! results below:')
    print()
    print(argfile)

    print()
    print('save the lines above to a file, this file can then be used to add arguments to invocations of hansken.py on '
          'the command line, e.g.:')
    print()
    print('  hansken shell @argfile')

    print()
    print('note that there are more global options than listed above (like logging configurations), see documentation')

    # TODO: prompt to write contents of argfile to file (HANSKENPY-87)
    return 0


def run_quickstart(*args, **kwargs):
    warnings.warn('{0}.run_quickstart has been renamed to {0}.run_quickstart_command'.format(__name__),
                  DeprecationWarning)
    run_quickstart_command(*args, **kwargs)


quickstart_parser = add_command('quickstart',
                                run_quickstart_command,
                                optional_project=False,
                                help='interactively determine configuration values for use with hansken.py')
# explicitly disable auth, avoid starting with username/password for quickstart
quickstart_parser.set_defaults(auth=False)
