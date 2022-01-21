# encoding=utf-8

from itertools import chain
import warnings

from logbook import Logger

from hansken.remote import ProjectContext
from hansken.tool import add_command


log = Logger(__name__)


try:
    from fuse import FUSE, Operations
    # REG = regular file, LNK = symbolic link
    from stat import S_IFREG, S_IFLNK

    def run_mount_command(args):
        if not args.endpoint:
            mount_parser.error('the following argument is required: ENDPOINT')
        if not args.keystore:
            mount_parser.error('the following argument is required: KEYSTORE')

        with ProjectContext(args.endpoint, args.project,
                            keystore_url=args.keystore, auth=args.auth, verify=args.verify) as context:
            images = [image['id'] for image in context.images()]

            options = {
                # align the fs' name with common unix-style filesystem names
                'fsname': 'hanskenfs',
                # default the maximum read to 512KiB (runtime might force this lower)
                'max_read': 512 << 10,
            }

            # parse mount options from the -o arg as a comma-separated list of options
            # NB: FUSE will turn this back into a -o style line, but offers no way of passing this verbatim
            for option in (args.options.split(',') if args.options else []):
                option = option.split('=', 1)
                if len(option) == 2:
                    options[option[0]] = option[1]
                else:
                    # treat singular keys as flags
                    options[option[0]] = True

            operations = HanskenFS(context, *images)
            # let fuse mount the actual filesystem
            FUSE(operations, args.mount_point, foreground=args.foreground, **options)

    class HanskenFS(Operations):
        """
        A subset of filesystem operations that enable a number of images
        within a project to be accessed as read-only local files. All metadata
        calls are cached locally, read calls are passed to remote. Depending
        on mount options, the local system may cache blocks read from this
        filesystem.
        """

        def __init__(self, context, *images):
            log.debug('gathering info to mount {} images in project {}', len(images), context.project_id)
            # gather the root traces of all the images, used for filesystem metadata and reading data
            self.roots = {'/{}'.format(root.image_id): root for root in context.roots()
                          if root.image_id in images}

            log.debug('got {} roots', len(self.roots), len(images))
            # store relevant image metadata to create 'symlinks' to the image data
            self.links = {'/{}'.format(image['description']): image['id'] for image in context.images()
                          if image['id'] in images and image.get('description')}

            log.debug('got {} descriptions to be used as symlinks', len(self.links))
            # cache the keys to be used for file access (treat 404s as 'no key needed')
            self.keys = {'/{}'.format(image): context.connection.key(image, raise_on_not_found=False)
                         for image in images}

            log.debug('got {}/{} keys', len(self.keys) - list(self.keys.values()).count(None), len(self.keys))

        def _stat(self, path):
            """
            A local minimized implementation of stat/fstat, providing only
            values for ``st_size`` and ``st_mtime`` (actually birth time, but
            the ``stat`` struct seems to not include this).

            :param path: the path to stat (starting with ``/``)
            :return: the size and mtime of *path*, as (`int`, `float`)
            """
            root = self.roots.get(path)
            size = root.get('extracted.data.raw.size') or 0
            mtime = root.get('processed.origin.createdOn') or root.get('processed.tool.meta.publishedOn')
            mtime = mtime.timestamp() if mtime else 0.0

            return size, mtime

        def getattr(self, path, fh=None):
            log.debug('hanskenfs: getattr({}, fh={})', path, fh)

            if path in self.roots:
                # getattr() for a 'file', return it as a regular file with access rights u+r,g+r,o+r
                size, mtime = self._stat(path)
                return dict(  # noqa: C408
                    st_mode=S_IFREG | 0o444,
                    st_size=size,
                    st_mtime=mtime
                )

            if path in self.links:
                # getattr for a 'link', return it as a link with access rights u+rx,g+rx,o+rx
                size, mtime = self._stat('/{}'.format(self.links.get(path)))
                return dict(  # noqa: C408
                    st_mode=S_IFLNK | 0o555,
                    st_size=size,
                    st_mtime=mtime,
                    st_nlinks=1
                )

            # not something we 'understand', let fusepy handle this one
            return super(HanskenFS, self).getattr(path, fh=fh)

        def readdir(self, path, fh=None):
            log.debug('hanskenfs: readdir({}, {})', path, fh)
            # strip the leading slashes from all the paths we're tracking
            return ['.', '..'] + [f.lstrip('/') for f in chain(self.roots.keys(), self.links.keys())]

        def readlink(self, path):
            log.debug('hanskenfs: readlink({})', path)
            return self.links.get(path)

        def read(self, path, size, offset, fh=None):
            log.debug('hanskenfs: read({}, {}, {}, {})', path, size, offset, fh)
            if path in self.roots:
                # return all bytes in the buffer, closing the underlying connection for reuse
                with self.roots.get(path).open(offset=offset, size=size, key=self.keys.get(path)) as buffer:
                    return buffer.read()

            # let fuse generate a useful error
            super(HanskenFS, self).read(path, size, offset, fh)

    fusepy_available = True
except (ImportError, OSError) as e:
    # allow someone reading the debug log to see why hansken mount is unavailable
    log.debug('mount command not available', e)
    fusepy_available = False

    # define a run_mount that will indicate error to user
    def run_mount_command(*args, **kwargs):
        mount_parser.error("command requires FUSE's python bindings, install hansken.py with the 'mount' extra or "
                           "install package 'fusepy' manually")


def run_mount(*args, **kwargs):
    warnings.warn('{0}.run_mount has been renamed to {0}.run_mount_command'.format(__name__),
                  DeprecationWarning)
    run_mount_command(*args, **kwargs)


help_text = 'mount images linked to a project as files inside an empty directory'
if not fusepy_available:
    # extend help text in case we'll expect errors
    help_text += ' (requires fusepy to be installed)'

mount_parser = add_command('mount',
                           run_mount_command,  # either the real deal or an error-wrapper
                           optional_project=False,
                           help=help_text)
mount_parser.add_argument('project', metavar='PROJECT',
                          help='the project to mount images from')
mount_parser.add_argument('mount_point', metavar='MOUNT_POINT',
                          help='an empty directory to use as the mount point')
mount_parser.add_argument('-f', '--foreground', action='store_true', default=False,
                          help='keep the process in the foreground (the default is to background the process)')
mount_parser.add_argument('-o', '--options', metavar='OPTIONS', default='',
                          help='FUSE mount options (see fuse documentation), specified like the mount command')
