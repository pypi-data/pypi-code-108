# encoding=utf-8

import warnings

from logbook import Logger
from requests import codes, HTTPError

from hansken.remote import Connection
from hansken.tool import add_command
from hansken.util import omit_empty


log = Logger(__name__)


def run_grant_command(args):
    if not args.endpoint:
        grant_parser.error('the following argument is required: ENDPOINT')
    if not args.keystore:
        grant_parser.error('the following argument is required: KEYSTORE')

    grant(args.endpoint, args.keystore,
          # we'll need either project or image, argparse's mutex group will make sure exactly one is provided
          project=args.project, image=args.image, identities=args.identities,
          auth=args.auth, verify=args.verify)


def run_grant(*args, **kwargs):
    warnings.warn('{0}.run_grant has been renamed to {0}.run_grant_command'.format(__name__),
                  DeprecationWarning)
    run_grant_command(*args, **kwargs)


def grant(base_url, keystore_url, project=None, image=None, identities=None, auth=None,
          verify=True):
    with Connection(base_url, keystore_url, auth=auth, verify=verify) as connection:
        # take either the specified image or all images in the specified project
        images = [image] if image else [linked['id'] for linked in connection.project_images(project)]
        log.debug('retrieving keys for {} images', len(images))

        keys = omit_empty({image: connection.key(image, raise_on_not_found=False) for image in images})
        log.info('{} has {} keys for {} images', connection.identity, len(keys), len(images))

        domain = connection.identity
        domain = domain[domain.index('@') + 1:]
        log.debug("determined active identity's domain to be {}", domain)

        # TODO: show progress info for total set of keys to be stored (HANSKENPY-45)
        stored_total = 0
        for identity in identities:
            if '@' not in identity:
                log.debug('expanding identity {identity} to {identity}@{domain}', identity=identity, domain=domain)
                identity = '{}@{}'.format(identity, domain)

            stored_identity = 0
            for image, key in keys.items():
                log.debug('store key for image {} for identity {}', image, identity)
                try:
                    connection.store_key(image, key, identity=identity)
                    stored_identity += 1
                except HTTPError as e:
                    # store_key will raise a 400 bad request http error if this identity already has a key for the image
                    # this is no problem here
                    if e.response is None or e.response.status_code != codes.bad_request:
                        # any other error is treated as a real error
                        raise

            log.info('stored {}/{} keys for identity {}', stored_identity, len(keys), identity)
            stored_total += stored_identity

        log.info('stored {} keys for {} identities', stored_total, len(identities))


# define command grant
grant_parser = add_command('grant',
                           run_grant_command,
                           optional_project=False,
                           help='grant keys for specific or project images to target identity or identities')
grant_parser.add_argument('identities', metavar='IDENTITY', nargs='+',
                          help='grant keys to IDENTITY')

# input takes either a single image or a single project, make argparse enforce this
images_group = grant_parser.add_mutually_exclusive_group(required=True)
images_group.add_argument('-p', '--project', metavar='PROJECT',
                          help='grant keys for all images in PROJECT')
images_group.add_argument('-i', '--image', metavar='IMAGE',
                          help='grant keys for a specific IMAGE')
