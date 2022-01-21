# encoding=utf-8

import warnings

import iso8601
from tabulate import tabulate, tabulate_formats

from hansken import __version__
from hansken.query import Term
from hansken.remote import Connection, ProjectContext
from hansken.tool import add_command
from hansken.util import format_byte_size


def run_versions_command(args):
    """
    Prints versions of both ``hansken.py`` and the remote it connects to.
    Optionally also retrieves the remote versions at extraction time for all
    images extracted for a project.

    :param args: an `argparse.Namespace` object with parsed arguments
    :return: 0
    """
    if not args.endpoint:
        versions_parser.error('the following argument is required: ENDPOINT')

    with Connection(args.endpoint, keystore_url=args.keystore, auth=args.auth, verify=args.verify) as connection:
        # get the build version, turn the build date into a proper date
        remote_versions = connection.version()
        build_date = iso8601.parse_date(remote_versions.get('timestamp')).date()

        print('hansken.py:    {}'.format(__version__))
        print('REST endpoint: {} (built on {})'.format(remote_versions.get('build'), build_date))

        if args.project:
            # leave a newline between this section and the next
            print()

            with ProjectContext(connection, args.project) as context:
                # create an info dict per image
                images = context.images()
                images = {image['id']: image for image in images}
                # gather some additional information from the root traces
                roots = context.roots()
                for root in roots:
                    version = root.tool_versions
                    # extraction service inserts its own version in the root trace
                    # named changed a few times, in reverse chronological order:
                    names = ('extraction-framework', 'hansken-extraction-service', 'extraction-service')
                    version = next(
                        # find the first non-falsy value, (…)
                        iter(filter(None, (version.get(name) for name in names))),
                        # (…) default to (unknown)
                        '(unknown)'
                    )

                    date = root.get('processed.tool.meta.extractionStartedOn')
                    date = iso8601.parse_date(date).date() if date else '(unknown)'

                    image = images.get(root.image_id)
                    # include additional info available from the root trace
                    image.update(
                        version=version,
                        date=date,
                        size=format_byte_size(root.data.raw.size)
                    )

                    if args.traces:
                        # only perform the search when needed, expensive compared to the rest
                        image.update(traces=len(context.search(Term('image', image.get('id')), count=0)))

                # predefine the headers to use
                headers = ['id', 'description', 'version', 'date']
                if args.size:
                    headers.append('size')
                if args.traces:
                    headers.append('traces')

                # reduce the data set to the bare essentials
                images = [
                    [value.get(header) for header in headers]
                    for value in sorted(images.values(), key=lambda value: value.get('id'))
                ]
                # and print the data set as a table
                print(tabulate(images, headers=headers, tablefmt=args.format))

    return 0


def run_versions(*args, **kwargs):
    warnings.warn('{0}.run_versions has been renamed to {0}.run_versions_command'.format(__name__),
                  DeprecationWarning)
    run_versions_command(*args, **kwargs)


# define command versions
versions_parser = add_command('versions',
                              run_versions_command,
                              optional_project=False,
                              help='print client, server and extraction versions')
versions_parser.add_argument('project', metavar='PROJECT', nargs='?',
                             help='print versions at extraction time for images in PROJECT')
versions_parser.add_argument('-s', '--size', dest='size', action='store_true', default=False,
                             help='display the raw data size of images')
versions_parser.add_argument('-S', '--no-size', dest='size', action='store_false',
                             help="don't display the raw data size of images (this is the default)")
versions_parser.add_argument('-t', '--traces', dest='traces', action='store_true', default=False,
                             help='display the number of traces per image')
versions_parser.add_argument('-T', '--no-traces', dest='traces', action='store_false',
                             help="don't display the number of traces per image (this is the default)")
versions_parser.add_argument('-f', '--format', metavar='FORMAT', choices=tabulate_formats, default='simple',
                             help='specify tabulation format, one of {} (see documentation of python module tabulate)'
                                  ''.format(', '.join(tabulate_formats)))
