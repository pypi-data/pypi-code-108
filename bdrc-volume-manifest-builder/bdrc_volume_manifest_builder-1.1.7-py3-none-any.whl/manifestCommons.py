import argparse
import io
import os
import traceback
from argparse import ArgumentParser
from typing import Tuple

import boto3
from PIL import Image

from v_m_b.AOLogger import AOLogger
from v_m_b.ImageRepository import ImageRepositoryBase
from v_m_b.ImageRepository import ImageRepositoryFactory
from v_m_b.S3WorkFileManager import S3WorkFileManager

# for writing and GetVolumeInfos
S3_DEST_BUCKET: str = "archive.tbrc.org"

# jimk Toggle legacy and new sources
BUDA_IMAGE_GROUP = True

S3_MANIFEST_WORK_LIST_BUCKET: str = "manifest.bdrc.org"
LOG_FILE_ROOT: str = "/var/log/VolumeManifestTool"
todo_prefix: str = "processing/todo/"
processing_prefix: str = "processing/inprocess/"
done_prefix: str = "processing/done/"

VMT_BUDABOM: str = 'fileList.json'
VMT_BUDABOM_JSON_KEY: str = 'filename'
VMT_DIM: str = 'dimensions.json'

s3_work_manager: S3WorkFileManager = S3WorkFileManager(S3_MANIFEST_WORK_LIST_BUCKET, todo_prefix, processing_prefix,
                                                       done_prefix)
shell_logger: AOLogger

def getVolumeInfos(workRid: str, image_repo: ImageRepositoryBase) -> []:
    """
    Tries data sources for image group info. If BUDA_IMAGE_GROUP global is set, prefers
    BUDA source, tries eXist on BUDA fail.
    :param image_repo: Image repository object
    :type image_repo: ImageRepositoryBase
    :type workRid: str
    :param workRid: Work identifier
    :return: VolList[imagegroup1..imagegroupn]
    """
    from v_m_b.VolumeInfo.VolumeInfoBuda import VolumeInfoBUDA
    from v_m_b.VolumeInfo.VolumeInfoeXist import VolumeInfoeXist

    vol_infos: [] = []
    if BUDA_IMAGE_GROUP:
        vol_infos = (VolumeInfoBUDA(image_repo)).fetch(workRid)

    if len(vol_infos) == 0:
        vol_infos = (VolumeInfoeXist(image_repo)).fetch(workRid)

    # TODO:  VolumeInfoDisk

    return vol_infos


def mustExistDirectory(path: str):
    """
    Argparse type specifying a string which represents
    Supports user home specifiers and environment variables
    :param path:
    :return:
    """
    if path is None or path == "":
        return ""

    realpath: str = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isdir(realpath) or not os.path.exists(realpath):
        raise argparse.ArgumentTypeError(f"{realpath} not found")
    else:
        return realpath


def parse_args(arg_namespace: object) -> bool:
    """
    :rtype: object VMBArg with members
    :param arg_namespace. VMBArgs class which holds arg values
    :return: truth value of no semantic errors
    """

    succeeded: bool = True

    _parser = argparse.ArgumentParser(description="Prepares an inventory of image dimensions",
                                      usage="%(prog)s [common options] { REPO_CHOICE: fs [fs options] | "
                                            "s3 [s3 options] }")

    child_parsers = _parser.add_subparsers(title='Repository Parser', description="Handles repository alternatives",
                                           help="Use one of \"fs\" or \"s3\" ",
                                           dest="REPO_CHOICE", required=True)

    _parser.add_argument("-d",
                         "--debugLevel",
                         dest='log_level',
                         action='store',
                         choices=['info', 'warning', 'error', 'debug', 'critical'],
                         default='info',
                         help="choice values are from python logging module")

    _parser.add_argument("-l",
                         "--logDir",
                         dest='log_parent',
                         action='store',
                         default='/tmp',
                         help="Path to log file directory")

    # No special args for s3, they're baked in. See prolog()
    s3_parser = child_parsers.add_parser("s3")
    s3_parser.add_argument('-b',
                           '--bucket',
                           action='store',
                           required=False,
                           default=S3_DEST_BUCKET,
                           help='Bucket - source and destination')

    fs_parser: ArgumentParser = child_parsers.add_parser("fs")

    #
    # sourceFile only used in manifestForList
    fs_parser.add_argument("-c",
                           '--container',
                           action='store',
                           type=mustExistDirectory,
                           default=".",
                           help="container for all work_Rid archives. Prefixes entries in --source_rid or --workList")

    fs_parser.add_argument("-i",
                           '--image-folder-name',
                           dest='image_folder_name',
                           action='store',
                           default="images",
                           help="name of parent folder of image files")

    src_group = _parser.add_mutually_exclusive_group(required=False)

    # the work list file must exist
    src_group.add_argument('-f', '--workListFile',
                           dest='work_list_file',
                           help="File containing one RID per line.",
                           type=argparse.FileType('r'))

    # but the work rid need not exist, it is qualified by the --container arg
    # if in fs mode, or the --bucket mode if in S3
    src_group.add_argument('-w', '--work-Rid',
                           dest='work_Rid',
                           help='name or partially qualified path to one work',
                           type=str)

    _parser.add_argument('-p',
                         '--poll-interval',
                         dest='poll_interval',
                         help="Seconds between alerts for file.",
                         required=False,
                         default=60,
                         type=int)

    # noinspection PyTypeChecker
    _parser.parse_args(namespace=arg_namespace)

    # semantic checks
    if arg_namespace.REPO_CHOICE == "s3" \
            and hasattr(arg_namespace, 'work_Rid') \
            and arg_namespace.work_Rid is not None \
            and os.path.dirname(arg_namespace.work_Rid) != '':
        error_message: str = f"-w/--work_Rid argument {arg_namespace.work_Rid} must not be a path in s3 mode"
        print(error_message)
        _parser.print_usage()
        succeeded = False

    return succeeded


def buildWorkListFromS3(client: object) -> (str, []):
    """
    Reads a well-known folder for files which contain works.
    Downloads, and digests each file, moving it to a temporary processing folder.
    :param client: S3 client
    :type client: boto3.client
    :return: unnamed tuple  of source directory and file names which have to be processed.
    """
    global shell_logger

    page_iterator = client.get_paginator('list_objects_v2').paginate(Bucket=S3_MANIFEST_WORK_LIST_BUCKET,
                                                                     Prefix=todo_prefix)
    file_list = []
    # Get the object list from the first value
    for page in page_iterator:
        object_list = [x for x in page["Contents"]]
        file_list.extend([x['Key'].replace(todo_prefix, '') for x in object_list if x['Key'] != todo_prefix])

    # We've ingested the contents of the to do list, move the files into processing
    new_names = [s3_work_manager.local_name_work_file(x) for x in file_list]

    s3_work_manager.mark_underway(file_list, new_names)

    # mon
    if len(file_list) == 0:
        shell_logger.debug("no name")
    else:
        shell_logger.info(f"found names {file_list}")

    return new_names


def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    import gzip
    with gzip.GzipFile(fileobj=out, mode='w') as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


def exception_handler(exception_type, exception, tb: traceback):
    """
    All your trace are belong to us!
    your format
    :param exception_type: system provided
    :param exception:  system provided
    :param tb: system provided traceback
    :type tb: traceback
    """

    global shell_logger
    error_string: str = f"{exception_type.__name__}: {exception}\n"

    if tb is not None:

        error_string += f"\ntraceback:\n\t{ ''.join(traceback.format_tb(tb, limit=3))}"

    if shell_logger is None:
        print(error_string)
    else:
        shell_logger.exception(error_string)


class VMBArgs:
    """
    instantiates command line argument container
    """
    pass


def prolog() -> Tuple[VMBArgs, ImageRepositoryBase.ImageRepositoryBase, AOLogger]:
    """
    Program setup. Exception, logging, and repository
    :return:
    """
    # Skip noisy exceptions
    import sys
    from pathlib import Path
    global shell_logger

    args = VMBArgs()
    succeeded: bool = parse_args(args)

    # parsing has screen dumped what it needs
    if not succeeded:
        sys.exit(1)

    shell_logger = AOLogger('local_v_m_b', args.log_level, Path(args.log_parent))

    shell_logger.hush = True
    sys.excepthook = exception_handler

    image_repository: ImageRepositoryBase = None

    channel = str(args.REPO_CHOICE).lower()
    if channel == 's3':
        session = boto3.session.Session(region_name='us-east-1')
        client = session.client('s3')
        dest_bucket = session.resource('s3').Bucket(args.bucket)
        image_repository = ImageRepositoryFactory.ImageRepositoryFactory().repository(channel, VMT_BUDABOM,
                                                                                      client=client, bucket=dest_bucket)
    else:
        if channel == 'fs':
            image_repository = ImageRepositoryFactory.ImageRepositoryFactory().repository(
                channel,
                VMT_BUDABOM,
                source_container=args.container,
                image_classifier=args.image_folder_name)

    shell_logger.hush = False

    return args, image_repository, shell_logger
