# encoding=utf-8

from argparse import SUPPRESS
from datetime import datetime, timezone
from getpass import getpass
from os import path, urandom
from subprocess import PIPE, Popen, STDOUT  # nosec
import sys
from uuid import uuid4
import warnings

from logbook import Logger
from requests import HTTPError

from hansken.remote import Connection
from hansken.tool import add_command
from hansken.tool._webhdfs import WebHDFSServer
from hansken.util import b64decode, b64encode, format_byte_size, Namespace, parse_byte_size


log = Logger(__name__)


upload_info = Namespace(marker='\f',  # marker used by the image tool to indicate line of machine-readable output
                        names={
                            # name of the local file being processed
                            'inputName': ('in_name', str),
                            # image size of the input file(set)
                            'inputSize': ('in_size', int),
                            # amount of bytes read
                            'currentOffset': ('num_read', int),
                            # image id of output image
                            'outputName': ('out_name', str),
                            # amount of bytes written
                            'outputSize': ('out_size', int),
                            # final status of conversion (split into (result, status), where result can either be 'OK'
                            # or 'FAIL', status is a string-representation of the conversion status)
                            'status': ('status', lambda value: value.split(':', 1)),
                            # number of bytes converted before hitting error status
                            'bytesConverted': ('bytes_converted', int),
                        })


class local_proxy:  # noqa: N801
    def __repr__(self):
        return '<authenticated proxy>'


# overwrite authenticated_proxy with an instance of itself
local_proxy = local_proxy()


def run_upload_command(args, progress=sys.stdout.isatty()):
    """
    Prepares arguments from the command line before being passed to upload.

    :param args: an argparse.Namespace object
    :param progress: whether to print progress information during upload
                     (defaults to the result of sys.stdout.isatty())
    :return: return code (zero for success, non-zero for error)
    """
    # check that we'll have an endpoint and a project (error message emulated to look like argparse's own messages)
    if not args.endpoint:
        upload_parser.error('the following argument is required: ENDPOINT')
    if not args.project and (args.link or args.extract):
        upload_parser.error('the following argument is required (linking or extraction requested): PROJECT')
    if not args.link and args.extract:
        upload_parser.error('starting extraction impossible without linking image to project')
    if not args.key:
        upload_parser.error('the following argument is required: KEY')
    if args.store_key and not args.keystore:
        upload_parser.error('no keystore endpoint available to store key')

    def print_values():
        try:
            print('---')
            while True:
                name, value = yield  # catch 2-tuple sent to print
                print('{name:<20} {value}'.format(name=name + ':', value=value))
                sys.stdout.flush()
        finally:
            print('...')
            sys.stdout.flush()

    return_code = 0
    for image in args.images:
        key = args.key
        if callable(key):
            # generate / prompt a new key for every image being processed
            key = key()

        input_size = None
        report = print_values()
        next(report)  # initialize the report generator, pause at the yield
        report.send(('file', image))
        report.send(('started', datetime.now(tz=timezone.utc).isoformat()))
        try:
            # upload is a generator, should come up with our image id while it does its thing
            for name, value in upload(args.endpoint,
                                      # use provided image_id or generate random image id
                                      args.image_id or str(uuid4()),
                                      image,
                                      b64decode(key.strip(), validate=True),
                                      # default to local_proxy (hdfs_url is a hidden option)
                                      args.hdfs_url or local_proxy,
                                      bufsize=args.bufsize,
                                      max_retries=args.retry if args.retry >= 0 else None,
                                      retry_wait=args.wait,
                                      auth=args.auth,
                                      # only supply a project when linking
                                      project=args.project if args.link else args.link,
                                      extract=args.extract,
                                      keystore_url=args.keystore,
                                      store_key=args.store_key,
                                      verify=args.verify,
                                      image_tool_path=args.image_tool_path):

                if name == 'in_size':
                    report.send(('input size', format_byte_size(value)))
                    input_size = value

                if name == 'out_name':
                    report.send(('id', value))
                    report.send(('key', key))

                if progress and input_size and name == 'num_read':
                    # display progress only when input size is known
                    # clear line (\033[2K), move caret to start of line (\r), print progress line
                    print('\033[2K\r[{:<40}] ({})'.format(
                        '»' * int(40 * value / input_size),
                        format_byte_size(value)
                    ), end='')

                if name == 'out_size':
                    if progress and input_size:
                        # clear the line we've been using for progress info (hides the bar when completed)
                        print('\033[2K\r', end='')

                    report.send(('output size', format_byte_size(value)))
                    if input_size and value:
                        # if we know the input size and the output size is not 0, show the compression ratio
                        report.send(('compression ratio', round(input_size / value, 3)))

                if name == 'status':
                    report.send(('status', '{} ({})'.format(*value)))

                if name == 'bytes_converted':
                    report.send(('bytes converted', format_byte_size(value)))

            report.send(('completed', datetime.now(tz=timezone.utc).isoformat()))
        except AssertionError as e:
            return_code = 1
            print(str(e), file=sys.stderr)
            sys.stderr.flush()
        finally:
            report.close()

    return return_code


def run_upload(*args, **kwargs):
    warnings.warn('{0}.run_upload has been renamed to {0}.run_upload_command'.format(__name__),
                  DeprecationWarning)
    run_upload_command(*args, **kwargs)


def upload(connection_or_endpoint, image_id, image_file, key,
           destination=local_proxy, bufsize=8 << 20, max_retries=8, retry_wait=10.0,
           auth=None, project=False, extract=False, keystore_url=None, store_key=False,
           verify=True, image_tool_path='hansken-image-tool', streaming=False,
           **image_meta):
    """
    Calls hansken-image-tool to convert a local image file to an NFI image and
    uploads it to webhdfs (destination should include directory on target
    HDFS). Links the uploaded image to a project and starts extraction if
    requested. User and description for the created image metadata are based
    on the supplied user and image file name.

    :param connection_or_endpoint: either an instance of `.Connection` or an
        endpoint to which a new `.Connection` instance will be connected
    :param image_id: image id of the image to be uploaded
    :param image_file: local file name of the image to be uploaded
    :param key: crypto key to use for encrypting the image (binary)
    :param destination: destination for the converted image (webhdfs url),
        defaults to a local proxy, passing the data to the authenticated
        connection to the Hansken remote
    :param bufsize: buffer size to use when reading image data (only applicable
        when using a local proxy as the destination)
    :param max_retries: maximum number of times to retry uploading a chunk of
        data (only applicable when using a local proxy as the destination)
    :param retry_wait: number of seconds to wait before retrying a failed chunk
        of data (only applicable when using a local proxy as the destination)
    :param auth: a `.HanskenAuthBase` object
    :param project: project to link the uploaded image to (or False)
    :param extract: whether to extract the new image (requires project to be
        set)
    :param store_key: whether to store the provided key in the key store
    :param image_tool_path: (Path to) hansken image tool in the system being used.
        For uploading from Windows this should be set to the (batch) script, e.g. 'hansken-image-tool.bat' or
        'C:\\path\\to\\tool\\hansken-image-tool.bat' (See: https://bugs.python.org/issue8224)
        Defaults to 'hansken-image-tool' which works for unix systems
    :param streaming When set to true, use the streaming upload. When set to False, use the stable chunk upload
    :param image_meta: freeform meta data for the uploaded image, description
        defaults to file base name (e.g. MyImage.E01)
    :return: a generator yielding (name, value) tuples provided by the image
        converter (see upload_info)
    """
    # implementation requires the communication marker to be whitespace
    if not upload_info.marker.isspace():
        raise ValueError('image tool communication marker ({}) needs to be whitespace'.format(upload_info.marker))

    def run_image_tool(destination, uploaded_image):
        """
        Runs hansken-image-tool, uploading an image to an HTTP endpoint.

        :param destination: an HTTP-destination to pass along to the
            ``hansken-image-tool`` command as the image destination
        :param uploaded_image: a image metadata dict to be updated in-place
            should any image metadata need to be updated
        :return: a generator yielding (name, value) tuples provided by the
            image converted (see upload_info)
        """
        command_line = [image_tool_path,
                        '--id', image_id,
                        '--format', 'NFI',
                        '--compression', 'LZ4',
                        '--cipher', 'AES',
                        '--mode', 'CTR',
                        '--key', b64encode(key),
                        '--digest', 'SHA2_256',
                        '--machine',  # hidden option request machine-readable output
                        image_file,
                        destination]

        # start image conversion, redirect stderr to stdout (text mode)
        process = Popen(command_line, universal_newlines=True, stdout=PIPE, stderr=STDOUT)  # nosec
        console_lines = []
        # process.communicate blocks, instead read from process' standard out until EOF
        for line in iter(process.stdout.readline, ''):
            # separate regular log lines from bits of info we want
            if line.startswith(upload_info.marker):
                name, value = line.strip().split(':', 1)
                if name in upload_info.names:
                    # passed info is something we need to share, find the internal name and value type
                    name, vtype = upload_info.names[name]
                    value = vtype(value)
                    yield name, value
                    if name == 'status':
                        # caught conversion status, push that to image metadata
                        uploaded_image['uploadStatus'] = value[1]
            else:
                line = line.strip()
                log.debug('log output from image tool: {}', line)
                console_lines.append(line)

        message = 'conversion process (image id {image_id}) terminated with return code {return_code}, ' \
                  'output follows\n---\n{output}'
        if process.wait() != 0:
            raise ValueError(message.format(image_id=image_id if image_id is not None else 'unknown',
                                            return_code=process.returncode,
                                            output='\n'.join(console_lines)))

    def do_upload(connection):
        # create the image metadata of the image to be uploaded (override description if required)
        description = image_meta.pop('description', None) or path.basename(image_file)
        connection.create_image(id=image_id, description=description, **image_meta)

        # retrieve the freshly created image metadata should we need to update it
        created_image = connection.image(image_id)
        # remove the image's id, updates won't be accepted with the id in the update 'body'
        created_image.pop('id')
        # copy the created metadata so we can detect edits made during upload
        uploaded_image = dict(created_image)

        try:
            if project:
                # if requested, link image to project
                connection.link_image(project, image_id)
        except HTTPError as e:
            # not authorized to link the image (or some other problem); remove the metadata
            connection.delete_image(image_id)
            raise ValueError(f'failed to link image {image_id} to project {project}') from e

        try:
            if destination is local_proxy:
                # spin up a local WebHDFS-like server, passing data along to connection.upload_image, while passing any
                # named values generated from the image tool to the caller

                # define a wrapper around connection.upload_image to force the callback to be authenticated
                # an upload_image call potentially needs a data source that can't be reused, so make sure that any
                # potential forced re-auth happens on a repeatable call
                def force_auth_upload_callback(*args, **kwargs):
                    # call the identity_uid function to avoid the cached identity, make the remote tell us who we are
                    connection.identity_uid()
                    # now call the actual callback we intended to call before
                    return connection.upload_image(*args, **kwargs)

                with WebHDFSServer(force_auth_upload_callback,
                                   bufsize=bufsize, max_retries=max_retries, retry_wait=retry_wait,
                                   streaming=streaming) as server:
                    yield from run_image_tool('http://localhost:{}/'.format(server.server_port), uploaded_image)
            else:
                # pass any named values generated from the image tool to the caller (image tool uploads the data itself)
                yield from run_image_tool(destination, uploaded_image)
        except (KeyboardInterrupt, BrokenPipeError):
            # The user aborted the upload, or the upload has failed due to a broken pipe error
            log.warn('upload was interrupted, removing partially uploaded image {}', image_id)
            if project:
                connection.unlink_image(project, image_id)
            connection.delete_image(image_id)
            log.warn('partial upload removed')
            raise

        if uploaded_image != created_image:
            # image metadata was changed during upload, reflect changes to remote
            connection.edit_image(image_id, **uploaded_image)
        if store_key:
            connection.store_key(image_id, key)
        if project and extract:
            # if requested and there's a project available, extract traces from the uploaded image
            connection.extract(project, image_id, 'index', key)

    # call do_upload with an existing or new connection object
    if hasattr(connection_or_endpoint, 'extract'):
        # we've been handed a Connection, use it without closing it
        # NB: using isinstance here makes testing nigh impossible
        return do_upload(connection_or_endpoint)
    else:
        # using an endpoint, create local Connection that gets closed after the needed calls
        with Connection(connection_or_endpoint, auth=auth, keystore_url=keystore_url, verify=verify) as connection:
            return do_upload(connection)


def prompt_verify_key():
    """
    Prompts for a key twice, verifying the entered values are identical before
    returning it. Aborts on keyboard interrupt or EOF.

    :return: the key entered by the user
    """
    try:
        while True:
            key = getpass(prompt='Key (base64-encoded): ').strip()
            if key == getpass(prompt='Key (again): ').strip():
                return key
            else:
                print("Provided keys don't match, please try again (^C or {eof} to abort)".format(
                    eof='^Z' if 'win32' in sys.platform else '^D'
                ))
    except (KeyboardInterrupt, EOFError):  # user pressed either ^C or ^D (^Z on windows)
        raise SystemExit('Aborted')


# define command upload
upload_parser = add_command('upload',
                            run_upload_command,
                            help='upload an image to Hansken image store')
# add arguments for sub-command upload
upload_parser.add_argument('images', metavar='FILE', nargs='+', help='local file(s) to convert and upload')
upload_parser.add_argument('-o', '--output', dest='hdfs_url', metavar='ENDPOINT', default=local_proxy,
                           help=SUPPRESS)
upload_parser.add_argument('-b', '--bufsize', metavar='SIZE', type=parse_byte_size, default=8 << 20,
                           help='buffer size to be used when reading data from hansken-image-tool')
upload_parser.add_argument('-r', '--retry', metavar='N', type=int, default=8,
                           help='maximum number of times to retry uploading chunks of data '
                                '(defaults to 8, set to 0 to attempt just once, set to -1 to set no max)')
upload_parser.add_argument('-w', '--wait', metavar='SECONDS', type=float, default=10.0,
                           help='amount of time in seconds to wait between chunk upload retries')
upload_parser.add_argument('-i', '--image-id', dest='image_id', metavar='IMAGE_ID', help=SUPPRESS)
upload_parser.add_argument('-L', '--no-link', dest='link', action='store_false', default=True,
                           help='do not link uploaded image to a project (disables extraction)')
upload_parser.add_argument('-k', '--key', dest='key', metavar='KEY', default=lambda: b64encode(urandom(32)),
                           help='key to access IMAGE (base64-encoded). by default, a random key will be generated')
upload_parser.add_argument('-K', '--prompt-key', dest='key', action='store_const',
                           const=prompt_verify_key, help='prompt for a key (base64-encoded)')
upload_parser.add_argument('--streaming', action='store_true', default=False,
                           help='Stream the image data to Hansken instead of using chunked upload')
upload_parser.add_argument('-x', '--extract', action='store_true',
                           help='start extraction of traces after image upload')
upload_parser.add_argument('-s', '--store-key', dest='store_key', action='store_true', default=True,
                           help='store provided or generated key in keystore')
upload_parser.add_argument('-S', '--no-store-key', dest='store_key', action='store_false',
                           help='do not store key in keystore')
upload_parser.add_argument('--hansken-image-tool', dest='image_tool_path', default='hansken-image-tool',
                           help='(Path to) script calling the Hansken image tool. Should include script\'s'
                                'extension in Windows')
