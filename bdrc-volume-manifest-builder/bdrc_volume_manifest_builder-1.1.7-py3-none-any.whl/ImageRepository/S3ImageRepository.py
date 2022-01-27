import hashlib
import io
import sys
from typing import Tuple

import boto3
import botocore
from boto.s3.bucket import Bucket

# from manifestCommons import *
import v_m_b.manifestCommons as Common
from v_m_b.ImageRepository.ImageRepositoryBase import ImageRepositoryBase
from v_m_b.VolumeInfo.VolInfo import VolInfo
from v_m_b.image.generateManifest import fillDataWithBlobImage
from v_m_b.s3customtransfer import S3CustomTransfer


class S3ImageRepository(ImageRepositoryBase):

    def upload_manifest(self, *args):
        pass

    def get_bom(self):
        """

        :return: text of volume bill of materials
        """
        pass

    def __init__(self, bom: str, client: boto3.client, dest_bucket: Bucket):
        """
        Initialize
        :param bom:name of Bill of Materials
        """
        super(S3ImageRepository, self).__init__(bom)
        self._client = client
        self._bucket = dest_bucket
        self._boto_paginator = self._client.get_paginator('list_objects_v2')

    def manifest_exists(self, work_Rid: str, image_group_id: str):
        """
        make sure s3folderPrefix+"/dimensions.json" doesn't exist in S3
        """
        key = self.getPathfromLocators(work_Rid, image_group_id) + 'dimensions.json'
        try:
            self._client.head_object(Bucket=Common.S3_DEST_BUCKET, Key=key)
            return True
        except botocore.exceptions.ClientError as exc:
            if exc.response['Error']['Code'] == '404':
                return False
            else:
                raise

    def fillData(self, transfer, s3imageKey, imgdata):
        """
        Launch async transfer with callback
        """
        buffer = io.BytesIO()
        try:
            transfer.download_file(self._bucket.name, s3imageKey, buffer,
                                   callback=DoneCallback(buffer, imgdata))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.repo_log.error(f"S3 object {s3imageKey} not found.")
            else:
                ee = sys.exc_info()
                self.repo_log.error(f"S3 Exception ei[0]:{ee[0]} ei[1]:{ee[1]}")
                raise
        finally:
            # self.repo_log.debug(imgdata)
            pass

    def generateManifest(self, work_Rid: str, vol_info: VolInfo) -> []:
        res = []
        transfer = S3CustomTransfer(self._client)
        parent: str = self.getPathfromLocators(work_Rid, vol_info.imageGroupID)
        #
        # jkmod: moved expand_image_list into VolumeInfoBUDA class
        for imageFileName in vol_info.image_list:
            image_key: str = parent + imageFileName
            imgdata = {"filename": imageFileName}
            res.append(imgdata)
            self.fillData(transfer, image_key, imgdata)

        transfer.wait()
        return res

    def getImageNames(self, work_Rid: str, image_group: str, bom_name: str) -> []:
        """
        S3 implementation of get Image Names

        """
        image_list = []

        full_image_group_path: str = self.getPathfromLocators(work_Rid, image_group)
        bom_path: str = full_image_group_path + bom_name
        # noinspection PyBroadException
        try:
            bom: [] = self.read_bom_from_s3(bom_path)

            if len(bom) > 0:
                self.repo_log.debug(
                    f"fetched BOM from BUDA BOM: {len(bom)} entries path:{bom_path}:")
                return bom

            # no BOM. Enumerate the files
            page_iterator = self._boto_paginator.paginate(Bucket=self._bucket.name, Prefix=full_image_group_path)

            # #10 filter out image files
            # filtered_iterator = page_iterator.search("Contents[?contains('Key','json') == `False`]")
            # filtered_iterator = page_iterator.search("Contents.Key[?contains(@,'json') == `False`][]")
            # filtered_iterator = page_iterator.search("[?contains(Contents.Key,'json') == `false`][]")

            # Strip out the path components of all non json files in the prefix
            for page in page_iterator:
                if "Contents" in page:
                    image_list.extend([dat["Key"].replace(full_image_group_path, "") for dat in page["Contents"] if
                                       '.json' not in dat["Key"]])

            self.repo_log.debug(
                f"fetched BOM from S3 list_objects: {len(image_list)} entries. path:{full_image_group_path}")
        except Exception as eek:
            self.repo_log.warning(f"Could not populate BOM for {bom_path}")
        finally:
            pass
        return image_list

    def read_bom_from_s3(self, bom_path: str) -> list:
        """
        Reads a json file and returns the values with the "filename" key as a list of strings
        :param bom_path:  full s3 path to BOM
        :return:
        """
        import boto3
        import json

        s3 = boto3.client('s3')
        json_body: {} = {}

        from botocore.exceptions import ClientError
        try:
            obj = s3.get_object(Bucket=self._bucket.name, Key=bom_path)
            #
            # Python 3 read() returns bytes which need decode
            json_body = json.loads(obj['Body'].read().decode('utf - 8'))

            self.repo_log.info("read bom from s3 object size %d json body size %d path %s",
                               len(obj), len(json_body), bom_path)
        except ClientError as ex:
            errstr: str = f"ClientError Exception {ex.response['Error']['Code']} Message " \
                          " f{ex.response['Error']['Message']} on object {ex.response['Error']['Key']} " \
                          "for our BOMPath  {bom_path}  from bucket {self._bucket.name}"

            if ex.response['Error']['Code'] == 'NoSuchKey':
                self.repo_log.warning(errstr)
            else:
                self.repo_log.error(errstr)
                raise

        return [x[Common.VMT_BUDABOM_JSON_KEY] for x in json_body]

    def uploadManifest(self, work_rid: str, image_group: str, bom_name: str, manifest_zip: bytes):
        """
         - upload on s3 with the right metadata:
          - ContentType='application/json'
          - ContentEncoding='gzip'
          - key: s3folderPrefix+"dimensions.json" (making sure there is a /)
        :param work_rid:
        :param image_group:
        :param bom_name:
        :param manifest_zip:
        :return:
        """
        key = self.getPathfromLocators(work_rid, image_group) + bom_name
        self.repo_log.debug("writing " + key)
        from botocore.exceptions import ClientError
        try:
            self._client.put_object(Key=key, Body=manifest_zip,
                                    Metadata={'ContentType': 'application/json', 'ContentEncoding': 'gzip'},
                                    Bucket=self._bucket.name)
            self.repo_log.info("wrote " + key)
        except ClientError:
            self.repo_log.warn(f"Couldn't write json {key}")

    def getPathfromLocators(self, work_Rid: str, image_group_folder_name: str) -> str:
        """
        :param work_Rid: Work resource id
        :param image_group_folder_name: image group - gets transformed
        :returns:  the s3 prefix (~folder) in which the volume will be present.

        inpire from https://github.com/buda-base/buda-iiif-presentation/blob/master/src/main/java/
        io/bdrc/iiif/presentation/ImageInfoListService.java#L73
        Example:
           - work_Rid=W22084, image_group_id=I0886
           - result = "Works/60/W22084/images/W22084-0886/
        where:
           - 60 is the first two characters of the md5 of the string W22084
           - 0886 is:
              * the image group ID without the initial "I" if the image group ID is in the form I\\d\\d\\d\\d
              * these are some older cases
              * or else the full image group ID (incuding the "I")

        """
        md5 = hashlib.md5(str.encode(work_Rid))
        two = md5.hexdigest()[:2]

        # Moved to VolInfossuffix = self.getImageGroup(image_group_folder_name)
        return f'Works/{two}/{work_Rid}/images/{work_Rid}-{image_group_folder_name}/'

    def resolveWork(self, work_rid_path: str) -> Tuple[str, str]:
        """
        S3 implementation
        :param work_rid_path:
        :return: reflects path back
        """
        return "", work_rid_path


class DoneCallback(object):
    def __init__(self, buffer, imgdata):
        self._buffer = buffer
        self._imgdata = imgdata

    def __call__(self):
        fillDataWithBlobImage(self._buffer, self._imgdata)
