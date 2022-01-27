"""
shell for manifest builder
"""
import json
import logging
import sys
import time
import traceback

# from manifestCommons import prolog, getVolumeInfos, gzip_str, VMT_BUDABOM
import v_m_b.manifestCommons as Common
from v_m_b.AOLogger import AOLogger
from v_m_b.ImageRepository.ImageRepositoryBase import ImageRepositoryBase
from v_m_b.VolumeInfo.VolInfo import VolInfo

image_repo: ImageRepositoryBase
shell_logger: AOLogger


def manifestFromS3():
    """
    Retrieves processes S3 objects in a bucket/key pair, where key is a prefix
    :return:
    """

    global image_repo, shell_logger
    args, image_repo, shell_logger = Common.prolog()

    # manifestFromS3 specific checking - no -f -w arguments
    if (hasattr(args, 'work_Rid') and args.work_Rid is not None) \
            or (hasattr(args, 'work_list_file') and args.work_list_file is not None):
        raise ValueError("manifestFromS3 must be given without --work_Rid and --work_file_name argument.")

    while True:
        try:

            import boto3
            session = boto3.session.Session(region_name='us-east-1')
            client = session.client('s3')
            work_list = Common.buildWorkListFromS3(client)

            for s3Path in work_list:
                s3_full_path = f'{Common.processing_prefix}{s3Path}'

                # jimk: need to pass a file-like object. NamedTemporaryFile returns an odd
                # beast which you cant run readlines() on
                from tempfile import NamedTemporaryFile
                file_path = NamedTemporaryFile()
                client.download_file(Common.S3_MANIFEST_WORK_LIST_BUCKET, s3_full_path, file_path.name)
                manifestForList(open(file_path.name, "r"))
                # manifestForList(file_path.name)

            # don't need to rename work_list. Only when moving from src to done
            if len(work_list) > 0:
                Common.s3_work_manager.mark_done(work_list, work_list)
        except Exception as eek:
            shell_logger.log(logging.ERROR, str(eek))
        time.sleep(abs(args.poll_interval))


def manifestShell():
    """
    Prepares args for running using command line or file system input
    :return:
    """
    global image_repo, shell_logger
    args, image_repo, shell_logger = Common.prolog()

    all_well: bool = False

    # sanity check specific to fs args: -w or -f has to be given
    if args.work_list_file is None and args.work_Rid is None:
        raise ValueError("Error: in fs mode, one of -w/--work_Rid or -f/--work_list_file must be given")
    if args.work_list_file is not None:
        all_well = manifestForList(args.work_list_file)
    else:
        all_well = doOneManifest(args.work_Rid)

    if not all_well:
        error_string = f"Some builds failed. See log file {shell_logger.log_file_name}"
        print(error_string)
        shell_logger.hush = True  # we were just leaving anyway. Errors are already logged and sent
        raise Exception(error_string)


def manifestForList(sourceFile) -> bool:
    """
    reads a file containing a list of work RIDs and iterate the manifestForWork function on each.
    The file can be of a format the developer like, it doesn't matter much (.txt, .csv or .json)
    :param sourceFile: Openable object of input text
    :type sourceFile: Typing.TextIO
    """

    global shell_logger

    if sourceFile is None:
        raise ValueError("Usage: manifestforwork [ options ] -w sourceFile {fs | s3} [ command_options ]. "
                         "See manifestforwork -h")

    all_well: bool = True
    with sourceFile as f:
        for work_rid in f.readlines():
            work_rid = work_rid.strip()
            all_well &= doOneManifest(work_rid)
    return all_well


def doOneManifest(work_Rid: str) -> bool:
    """
    this function generates the manifests for each volume of a work RID (example W22084)
    :type work_Rid: object
    """

    global image_repo, shell_logger

    is_success: bool = False

    try:
        vol_infos: [VolInfo] = Common.getVolumeInfos(work_Rid, image_repo)
        if len(vol_infos) == 0:
            shell_logger.error(f"Could not find image groups for {work_Rid}")
            return is_success

        for vi in vol_infos:
            _tick = time.monotonic()
            manifest = image_repo.generateManifest(work_Rid, vi)
            if len(manifest) > 0:
                upload(work_Rid, vi.imageGroupID, manifest)
                _et = time.monotonic() - _tick
                shell_logger.info(f"Volume {work_Rid}-{vi.imageGroupID} processing: {_et:05.3} sec ")
            else:
                _et = time.monotonic() - _tick
                shell_logger.error(f"No manifest created for {work_Rid}-{vi.imageGroupID} ")

        is_success = True
    except Exception as inst:
        eek = sys.exc_info()
        stack: str = ""
        for tb in traceback.format_tb(eek[2], 5):
            stack += tb
        shell_logger.error(f"{work_Rid} failed to build manifest {type(inst)} {inst}\n{stack} ")
        is_success = False

    return is_success


def upload(work_Rid: str, image_group_name: str, manifest_object: object):
    """
    inspire from:
    https://github.com/buda-base/drs-deposit/blob/2f2d9f7b58977502ae5e90c08e77e7deee4c470b/contrib/tojsondimensions.py#L68

    in short:
       - make a compressed json string (no space)
       - gzip it
       - send it to the repo
      :param work_Rid:˚
      :param image_group_name:
      :param manifest_object:
    """
    # for adict in manifest_object:
    #     print(f" dict: {adict} json: d{json.dumps(adict)}")
    manifest_str = json.dumps(manifest_object)
    # Even for debug, this is a little excessive
    # shell_logger.debug(manifest_str)
    manifest_gzip: bytes = Common.gzip_str(manifest_str)
    image_repo.uploadManifest(work_Rid, image_group_name, Common.VMT_DIM, manifest_gzip)


if __name__ == '__main__':
    manifestShell()
    # manifestFromS3()
