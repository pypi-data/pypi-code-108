#!/usr/bin/env python3
import argparse
import csv
import gzip
import io
import json
import logging
import os
import time
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import TextIO

import boto3
import botocore
from PIL import Image
from boto.s3.bucket import Bucket
from botocore.exceptions import ClientError

from getS3FolderPrefix import get_s3_folder_prefix
from s3customtransfer import S3CustomTransfer

from manifestCommons import *

csvlock: Lock = Lock()


# os.environ['AWS_SHARED_CREDENTIALS_FILE'] = "/etc/buda/volumetool/credentials"




# region shells
#  These are the entry points. See setup.py, which configures 'manifestfromS3' and 'manifestforwork:main' as console



def manifestForList(sourceFile: TextIO):
    """
    reads a file containing a list of work RIDs and iterate the manifestForWork function on each.
    The file can be of a format the developer like, it doesn't matter much (.txt, .csv or .json)
    """
    global shell_logger

    if sourceFile is None:
        raise ValueError("Usage: manifestforwork [ options ] sourceFile {fs | s3} [ command_options ]. "
                         "See manifestforwork -h")

    with sourceFile as f:
        for work_rid in f.readlines():
            work_rid = work_rid.strip()
            try:
                manifestForWork(client, dest_bucket, work_rid)
            except Exception as inst:
                shell_logger.error(f"{work_rid} failed to build manifest {type(inst)} {inst.args} {inst} ")


def manifestForVolume(client, workRID, vi, csvwriter):
    """
    this function generates the manifest for an image group of a work (example: I0886 in W22084)
    """

    global shell_logger

    s3_folder_prefix: str = get_s3_folder_prefix(workRID, vi.imageGroupID)
    if manifestExists(client, s3_folder_prefix):
        shell_logger.info(f"manifest exists: {workRID}-{vi.imageGroupID} path :{s3_folder_prefix}:")
    manifest = generateManifest(client, s3_folder_prefix, vi.image_list, csvwriter, workRID, vi.imageGroupID)
    # DEBUG uploadManifest(client, s3_folder_prefix, manifest)


def uploadManifest(bucket, s3folderPrefix, manifestObject):
    """
    inspire from:
    https://github.com/buda-base/drs-deposit/blob/2f2d9f7b58977502ae5e90c08e77e7deee4c470b/contrib/tojsondimensions.py#L68

    in short:
       - make a compressed json string (no space)
       - gzip it
       - upload on s3 with the right metadata:
          - ContentType='application/json'
          - ContentEncoding='gzip'
          - key: s3folderPrefix+"dimensions.json" (making sure there is a /)
    """

    global shell_logger
    shell_logger.debug("uploading..pass")
    return

    manifest_str = json.dumps(manifestObject)
    manifest_gzip = gzip_str(manifest_str)

    key = s3folderPrefix + 'dimensions.json'
    shell_logger.debug("writing " + key)
    try:
        bucket.put_object(Key=key, Body=manifest_gzip,
                          Metadata={'ContentType': 'application/json', 'ContentEncoding': 'gzip'},
                          Bucket=S3_DEST_BUCKET)
        shell_logger.info("wrote " + key)
    except ClientError:
        shell_logger.warn(f"Couldn't write json {key}")



def fillDataWithBlobImage(blob, data, csvwriter, s3imageKey, workRID, imageGroupID):
    """
    This function returns a dict containing the height and width of the image
    the image is the binary blob returned by s3, an image library should be used to treat it
    please do not use the file system (saving as a file and then having the library read it)

    This could be coded in a faster way, but the faster way doesn't work with group4 tiff:
    https://github.com/python-pillow/Pillow/issues/3756

    For pilmode, see
    https://pillow.readthedocs.io/en/5.1.x/handbook/concepts.html#concept-modes

    They are different from the Java ones:
    https://docs.oracle.com/javase/8/docs/api/java/awt/image/BufferedImage.html

    but they should be enough. Note that there's no 16 bit
    """
    errors = []
    size = blob.getbuffer().nbytes
    im = Image.open(blob)
    data["width"] = im.width
    data["height"] = im.height
    # we indicate sizes of the more than 1MB
    if size > 1000000:
        data["size"] = size
    if size > 400000:
        errors.append("toolarge")
    compression = ""
    final4 = s3imageKey[-4:].lower()
    if im.format == "TIFF":
        compression = im.info["compression"]
        if im.info["compression"] != "group4":
            errors.append("tiffnotgroup4")
        if im.mode != "1":
            errors.append("nonbinarytif")
            data["pilmode"] = im.mode
        if final4 != ".tif" and final4 != "tiff":
            errors.append("extformatmismatch")
    elif im.format == "JPEG":
        if final4 != ".jpg" and final4 != "jpeg":
            errors.append("extformatmismatch")
    else:
        errors.append("invalidformat")
    # in case of an uncompressed raw, im.info.compression == "raw"
    if errors:
        csvline = [s3imageKey, workRID, imageGroupID, size, im.width, im.height, im.mode, im.format, im.palette,
                   compression, "-".join(errors)]
        report_error(csvwriter, csvline)




if __name__ == '__main__':
    manifestShell()
    # manifestFromList
    # manifestFor