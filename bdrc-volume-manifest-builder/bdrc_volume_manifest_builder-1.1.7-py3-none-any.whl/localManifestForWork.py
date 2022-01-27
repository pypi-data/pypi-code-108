#!/usr/bin/env python3
import sys

import aiofiles

import time
from pathlib import Path

from botocore.exceptions import ClientError

from v_m_b.manifestCommons import *


def manifestExists(image_folder: Path):
    """
    Has the manifest been built yet?
    :param image_folder: parent folder of manifest
    :type image_folder: object
    """
    return Path(image_folder,'dimensions.json').exists()


def uploadManifest(manifestObject: [], context: VMBArgs):
    """
    inspire from:
    https://github.com/buda-base/drs-deposit/blob/2f2d9f7b58977502ae5e90c08e77e7deee4c470b/contrib/tojsondimensions.py#L68

    in short:
       - make a compressed json string (no space)
       - gzip it
       - copy to destination
    """
    pass
    global shell_logger

    key: str = context.source_container
    try:
        shell_logger.info(f"wrote {key}")
    except ClientError:
        shell_logger.warn(f"Couldn't write json {key}")

# region shells

#  These are the entry points. See setup.py, which configures 'manifestfromS3' and 'manifestforwork:main' as console
#   entry points
def main():
    """
    reads the first argument of the command line and pass it as filename to the manifestForList function
    """
    manifestShell()

def manifestShell():
    """
    Prepares args for running
    :return:
    """
    args = prolog()
    manifestForList(args)

def manifestForList(args: VMBArgs):
    """
    reads a file containing a list of work RIDs and iterate the manifestForWork function on each.
    The file can be of a format the developer like, it doesn't matter much (.txt, .csv or .json)
    :param: args
    """
    global shell_logger

    if args.work_list_file is None:
        raise ValueError("Usage: manifestforwork sourceFile where sourceFile contains a list of work RIDs")

    with args.work_list_file as f:
        for work_rid in f.readlines():
            work_rid = work_rid.strip()
            try:
                manifestForWork(args, work_rid)
            except Exception as inst:
                shell_logger.error(f"{work_rid} failed to build manifest: {type(inst)} {inst.args} {inst} ")


def manifestForWork(args: VMBArgs, work_Rid: str):
    """
    this function generates the manifests for each volume of a work RID (example W22084)
    """

    global shell_logger

    vol_infos: [] = getVolumeInfos(work_Rid)
    if len(vol_infos) == 0:
        shell_logger.error(f"Could not find image groups for {work_Rid}")
        return

    for vi in vol_infos:

        _tick = time.monotonic()
        mani_fest = manifestForVolume(work_Rid, vi)
        _et = time.monotonic() - _tick
        print(f"Volume reading: {_et:05.3} ")
        shell_logger.debug(f"Volume reading: {_et:05.3} ")
        uploadManifest(mani_fest, args)


def manifestForVolume(work_Rid: str, vi: object) ->[]:
    """
    this function generates the manifest for an image group of a work (example: I0886 in W22084)
    :param vol_path: Path to images in a volume
    :type vol_path: Path
    :param vi: list of volume infos
    :type vi: object
    :returns: data for each image in one volume
    """

    # asyncio.run(generateManifest(vol_path, vi.image_list))
    generateManifest_s(complete_path,vi.image_list)


async def generateManifest(ig_container: Path, image_list: []) -> []:
    """
    this actually generates the manifest. See example in the repo. The example corresponds to W22084, image group I0886.
    :param ig_container: path of parent of image group
    :param image_list: list of image names
    :returns: list of  internal data for each file in image_list
    """
    #
    # res = []
    #
    # image_file_name: object
    # for image_file_name in image_list:
    #     image_path: Path = Path(ig_container,image_file_name)
    #     imgdata = {"filename": image_file_name}
    #     res.append(imgdata)
    #     # extracted from fillData
    #     async with aiofiles.open(image_path, "rb") as image_file:
    #         image_buffer = await image_file.read()
    #         # image_buffer = io.BytesIO(image_file.read())
    #         try:
    #             fillDataWithBlobImage(image_buffer, imgdata)
    #         except Exception as eek:
    #             exc = sys.exc_info()
    #             print(eek, exc[0])
    #     # asyncio.run(fillData(image_path, imgdata))
    return res

def generateManifest_s(ig_container: Path, image_list: []) -> []:
    """
    this actually generates the manifest. See example in the repo. The example corresponds to W22084, image group I0886.
    :param ig_container: path of parent of image group
    :param image_list: list of image names
    :returns: list of  internal data for each file in image_list
    """

    res = []

    image_file_name: object
    for image_file_name in image_list:
        image_path: Path = Path(ig_container,image_file_name)
        imgdata = {"filename": image_file_name}
        res.append(imgdata)
        # extracted from fillData
        with open(image_path, "rb") as image_file:
            image_buffer = image_file.read()
            # image_buffer = io.BytesIO(image_file.read())
            try:
                fillDataWithBlobImage(image_buffer, imgdata)
            except Exception as eek:
                exc = sys.exc_info()
                print(eek, exc[0])
        # asyncio.run(fillData(image_path, imgdata))
    return res


def fillDataWithBlobImage(blob, data):
    """
    This function populates a dict containing the height and width of the image
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

    blob2 = io.BytesIO(blob)
    size = blob2.getbuffer().nbytes
    im = Image.open(blob2)
    data["width"] = im.width
    data["height"] = im.height
    # we indicate sizes of the more than 1MB
    if size > 1000000:
        data["size"] = size


if __name__ == '__main__':
    pass
    # Or do one of these:
    # manifestFromS3()
    # manifestForList()
