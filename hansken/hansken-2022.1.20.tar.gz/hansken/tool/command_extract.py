# encoding=utf-8

from argparse import Action
from itertools import chain
import sys
import warnings

from logbook import Logger
from more_itertools import chunked

from hansken.query import DEFAULT_MAX_CLAUSE_COUNT, Exists, Facet, Or, Term
from hansken.remote import ProjectContext
from hansken.tool import add_command


log = Logger(__name__)


class SetItemAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # assume we'll get two values: the key and the value to be set
        # TODO: should raise type error when this unpacking fails (HANSKENPY-40)
        key, value = values
        # get the current state of the dict we're writing to or default to a new one
        stored = getattr(namespace, self.dest, None) or {}
        # set values from the command line
        stored[key] = value
        # set the current state of the dict (possibly overwriting the old one)
        setattr(namespace, self.dest, stored)


def run_extract_command(args, progress=sys.stdout.isatty()):
    """
    Runs extractions of images in the context of a project. Requires a keystore
    to work with encrypted data; keys will be fetched automatically.

    :param args: an `argparse.Namespace` object carrying command line arguments
    :param progress: whether to include progress info to stdout (defaults to
        ``sys.stdout.isatty()``)
    """
    # check that we'll have an endpoint and a project (error message emulated to look like argparse's own messages)
    if not args.endpoint:
        extract_parser.error('the following argument is required: ENDPOINT')
    if not args.project:
        extract_parser.error('the following argument is required: PROJECT')
    if not args.keystore:
        extract_parser.error('the following argument is required: KEYSTORE')

    def filter_images():
        # find current states of the images
        filtered = set()

        for image in linked:
            if image['id'] in images:
                # image is to be processed, find its current state
                image['state'] = image['states'][-1]['state']
                properties = image.items()
                # match all key:value pairs from the filter
                # TODO: enable negative filters (HANSKENPY-40)
                if all(prop in properties for prop in args.filter.items()):
                    log.debug('including image {}', image['id'])
                    filtered.add(image['id'])
                else:
                    log.debug('excluding image {}', image['id'])

        return filtered

    def images_with_user_content():
        # query to find user-generated content (notes and tags) within the images
        user_query = Exists('#note') | Exists('tags')
        # facet to get counters for images that have user-generated content
        facet = Facet('image')

        log.debug('checking for user content in {} images', len(images))

        def user_content_images(batch):
            query = user_query & Or(*[Term('image', image) for image in batch])
            # the keys with hits in the facets will be image id's that match user_query
            return context.search(query, count=0, facets=facet).facets[0].keys()

        return set(chain.from_iterable(
            # generate images that contain user-generated content in batches close to the max clause count
            user_content_images(batch) for batch in chunked(images, DEFAULT_MAX_CLAUSE_COUNT - 4)
        ))

    def what_to_extract():
        # provide information on the images that have user content
        print('the following images have user content within project {}:'.format(args.project))
        infos = [image for image in linked if image['id'] in user_content]
        for image in infos:
            print('  {id} ({description})'.format(**image))

        # ask the user what to do with that information (include / exclude these images or quit)
        try:
            include = None
            while include is None:
                # get either an empty string (default) or the first lowered char of whatever was entered
                choice = input('extract these images (y/[n]/q)? ')[:1].lower()
                if choice in 'ynq':  # NB: '' in 'ynq' is True
                    if choice == 'q':
                        raise SystemExit()
                    else:
                        # only 'yessy' should mean include (empty string = default = no)
                        include = choice == 'y'
        except (EOFError, KeyboardInterrupt):
            log.debug('user content inclusion choice cancelled by user')
            # user pressed ^D or ^C, abort command
            raise SystemExit('aborted')

        # return the chosen set of images to be extracted
        return images if include else images - user_content

    with ProjectContext(args.endpoint, args.project, args.keystore,
                        auth=args.auth, verify=args.verify) as context:
        linked = context.images()

        if args.images:
            # verify all images to be extracted are linked to project
            not_linked = set(args.images) - {image['id'] for image in linked}
            if not_linked:
                raise ValueError('images not linked to project {}: {}'.format(
                    args.project, ', '.join(not_linked)
                ))

        # create base set of images, either read from command line or defaulting to all linked images
        images = set(args.images) or {image['id'] for image in linked}

        if args.filter:
            log.info('filtering {} images using {} filters', len(images), len(args.filter))
            images = filter_images()
            log.info('{} images left after applying filters', len(images))

        if args.skip_images:
            skip_images = set(args.skip_images)
            log.info('skipping {} images', len(skip_images))
            images = images - skip_images
            log.info('{} images left after removing skipped images', len(images))

        if images and args.check_user_content:
            user_content = images_with_user_content()
            if user_content:
                log.info('{} images have user content, prompting user what to do', len(user_content))
                images = what_to_extract()
                log.info('{} images left after user content check', len(images))

        tools = None
        if args.include_tools or args.exclude_tools:
            include = set(args.include_tools or [])
            exclude = set(args.exclude_tools or [])

            if include & exclude:
                raise ValueError('cannot both include and exclude tools [{}]'.format(
                    ', '.join(sorted(include & exclude)))
                )

            # select all default tools
            tools = {name for name, tool in context.connection.tools().items() if tool.get('defaultEnabled')}
            log.info('default tool set uses {} tools', len(tools))

            # add and subtract tools to be included or excluded
            tools |= include
            tools -= exclude
            log.info('using {} tools after including [{}] and excluding [{}]',
                     len(tools),
                     ', '.join(sorted(include)),
                     ', '.join(sorted(exclude)))

        # make sure tool names becomes a list (sorted to be deterministic) or remains None to select the default
        tools = sorted(tools) if tools else None

        # start extractions
        if images:
            log.info('extracting {} images as user {}', len(images), context.connection.identity)
            try:
                if progress:
                    print('\033[2K\r[{:<40}] ({}/{})'.format(
                        '',  # no progress yet
                        0, len(images)
                    ), end='')
                else:
                    # provide some output if we won't be using a fancy progress bar
                    print('extracting {} images...'.format(len(images)))

                num_errors = 0
                for num, image in enumerate(images, start=1):
                    try:
                        # the actual action we set out to do (key left at automatic)
                        context.connection.extract(args.project, image, tools=tools, configuration=args.config)
                    except Exception as e:
                        num_errors += 1
                        log.exception('extraction of image {} within project {} failed', image, args.project, e)
                    finally:
                        if progress:
                            # print a 40-char progress bar with number indicator
                            print('\033[2K\r[{:<40}] ({}/{}){}'.format(
                                # fill progress bar as far as needed
                                '»' * int(40 * num / len(images)),
                                # numeric progress info
                                num, len(images),
                                # append number of errors if > 0
                                ' ({} errors)'.format(num_errors) if num_errors > 0 else ''
                            ), end='')

                # set return code to 1 on any number of errors
                return min(1, num_errors)
            finally:
                if progress:
                    # append a newline after our progress bar
                    print()
        else:
            raise SystemExit('no images to extract')


def run_extract(*args, **kwargs):
    warnings.warn('{0}.run_extract has been renamed to {0}.run_extract_command'.format(__name__),
                  DeprecationWarning)
    return run_extract_command(*args, **kwargs)


extract_parser = add_command('extract', run_extract_command, optional_project=False,
                             help='start extraction of images linked to a project')
extract_parser.add_argument('project', metavar='PROJECT',
                            help='the project to extract images for')
extract_parser.add_argument('images', metavar='IMAGE', nargs='*',
                            help='the images to be extracted (defaults to all images linked to PROJECT)')

extract_parser.add_argument('-s', '--state', metavar='STATE', dest='filter',
                            # 'parse' the passed value for state into the expected two-tuple
                            type=lambda value: ('state', value), action=SetItemAction,
                            help='consider only images whose current state is STATE')
extract_parser.add_argument('--property', metavar='PROPERTY:VALUE', dest='filter',
                            # parse the value passed value by splitting on :
                            # TODO: should raise TypeError on 'syntax error' (HANSKENPY-40) (or should use nargs=2)
                            type=lambda value: value.split(':', 1), action=SetItemAction,
                            help='consider only images whose value for PROPERTY is VALUE')
extract_parser.add_argument('-c', '--check-user-content', dest='check_user_content', action='store_true', default=True,
                            help='check if any selected images have user content and prompt for action to take '
                                 '(this is the default)')
extract_parser.add_argument('-C', '--no-check-user-content', dest='check_user_content', action='store_false',
                            help="don't check for user content")
extract_parser.add_argument('--skip-images', metavar='IMAGE', nargs='+',
                            help='images to be skipped, even if they would be included by other filters')
extract_parser.add_argument('--config', metavar='KEY:VALUE', dest='config',
                            # TODO: should raise TypeError on 'syntax error' (HANSKENPY-40) (or should use nargs=2)
                            type=lambda value: value.split(':', 1), action=SetItemAction,
                            help='override extraction configuration key CONFIG with VALUE for this single extraction')
extract_parser.add_argument('--include-tools', metavar='TOOL', nargs='+',
                            help='include named TOOL with the tools to be used to extract IMAGE(S)')
extract_parser.add_argument('--exclude-tools', nargs='+',
                            help='exclude named TOOL from the tools to be used to extract IMAGE(S)')
