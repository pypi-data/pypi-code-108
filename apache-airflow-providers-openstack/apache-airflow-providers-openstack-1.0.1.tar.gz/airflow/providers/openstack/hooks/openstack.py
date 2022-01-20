#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from io import BytesIO
from typing import Any, List, Optional

import boto3
import openstack
import os

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from openstack import proxy
from openstack.cloud import exc
from munch import Munch
from datetime import datetime
from airflow.hooks.base import BaseHook


class OpenstackHook(BaseHook):
    """
    Interact with Openstack.

    :param os_conn_id: The :ref:`openstack connection id <howto/connection:openstack>`
        reference.
    :type os_conn_id: str
    """

    conn_name_attr = 'os_conn_id'
    default_conn_name = 'os_default'
    conn_type = 'openstack'
    hook_name = 'Openstack'

    def __init__(self, os_conn_id: str = default_conn_name) -> None:
        super().__init__()
        self.os_conn_id = os_conn_id
        self.conn: Optional[openstack.connection.Connection] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.conn is not None:
            self.close_conn()

    def get_conn(self) -> openstack.connection.Connection:
        """Returns a OS connection object"""
        if self.conn is None:
            params = self.get_connection(self.os_conn_id)
            connect_dict = dict(
                region_name=params.extra_dejson.get("OS_REGION_NAME"),
                auth=dict(
                    auth_url=params.host,
                    username=params.login,
                    password=params.password,
                    project_id=params.extra_dejson.get("OS_PROJECT_ID"),
                    user_domain_id=params.extra_dejson.get("OS_PROJECT_DOMAIN_ID"),
                )
            )
            self.conn = openstack.connection.Connection(**connect_dict)
            self.conn.authorize()

        return self.conn

    def close_conn(self):
        """
        Closes the connection. An error will occur if the
        connection wasn't ever opened.
        """
        conn = self.conn
        conn.close()
        self.conn = None

    def list_volumes(self) -> List[any]:
        """
        Returns a list of files on the remote system.

        :param path: full path to the remote directory to list
        :type path: str
        """
        conn = self.get_conn()
        return conn.list_volumes()

    def list_snapshots(self, volumeid: str) -> List[any]:
        conn = self.get_conn()
        return conn.list_volume_snapshots(search_opts={'volume_id': volumeid})

    def get_volume_by_name(self, name: str) -> Munch:
        conn = self.get_conn()
        return next(x for x in conn.list_volumes() if x.name == name)

    def get_volume_by_id(self, volid: str) -> Munch:
        conn = self.get_conn()
        return conn.get_volume_by_id(volid)

    def get_snapshot_by_id(self, snapid: str) -> Munch:
        conn = self.get_conn()
        return conn.get_volume_snapshot_by_id(snapid)

    def get_image_by_id(self, imgid: str) -> Munch:
        conn = self.get_conn()
        return conn.get_image_by_id(imgid)

    def create_snapshot_from_volume_id(self, volid: str):
        conn = self.get_conn()
        volume = self.get_volume_by_id(volid)
        return conn.create_volume_snapshot(volume.id, True, False,
                                           name="snap_{}_{}".format(volume.name, datetime.now().strftime("%Y%m%d")))

    # noinspection PyProtectedMember
    def create_volume_from_snapshot_id(self, snapid: str) -> Munch:
        conn = self.get_conn()
        snap = self.get_snapshot_by_id(snapid)
        kwargs = dict(
            size=snap.size,
            name=snap.name,
            snapshot_id=snap.id
        )
        payload = dict(volume=kwargs)
        resp = conn.block_storage.post(
            '/volumes',
            json=dict(payload))
        data = proxy._json_response(
            resp,
            error_message='Error in creating volume')
        volume = conn._get_and_munchify('volume', data)
        conn.list_volumes.invalidate(conn)

        if volume['status'] == 'error':
            raise exc.OpenStackCloudException("Error in creating volume")

        return conn._normalize_volume(volume)

    def create_image_from_volume_id(self, volid: str) -> Munch:
        conn = self.get_conn()
        volume = self.get_volume_by_id(volid)
        return conn.create_image(volume.name, volume=volume)

    def download_image_id_to_path(self, imgid: str, path: str):
        conn = self.get_conn()
        img = conn.get_image_by_id(imgid)
        filename = "{}_{}.img".format(img.name, img.id)
        file_path = os.path.join(path, filename)
        r = conn.image.download_image(imgid, True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        return file_path

    def stream_image_to_s3(self, imgid: str,  aws_conn_id: str, bucket: str, part_size_mb: int):
        conn = self.get_conn()
        img = conn.get_image_by_id(imgid)
        filename = "{}_{}.img".format(img.name, img.id)

        s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        s3: boto3.resource = s3_hook.get_resource_type("s3")
        s3Client: boto3.client = s3_hook.get_client_type("s3")

        mpu = s3Client.create_multipart_upload(
            Bucket=bucket,
            Key=filename
        )

        stream = BytesIO()
        parts = []
        partcount = [0]

        def uploadPart():
            partcount[0] += 1
            print("uploading part %i" % partcount[0])
            stream.seek(0)
            upload_part = s3.MultipartUploadPart(
                bucket, filename, mpu['UploadId'], partcount[0]
            )
            upload_part_response = upload_part.upload(
                Body=stream,
            )
            parts.append({
                'PartNumber': partcount[0],
                'ETag': upload_part_response['ETag']
            })
            stream.seek(0)
            stream.truncate()

        response = conn.image.download_image(imgid, True)
        for chunk in response.iter_content():  # until EOF
            if not chunk:  # EOF?
                break
            stream.write(chunk)
            if stream.tell() > part_size_mb << 20:
                uploadPart()
        uploadPart()
        s3Client.complete_multipart_upload(Bucket=bucket, Key=filename,
                                           MultipartUpload={'Parts': parts},
                                           UploadId=mpu['UploadId'])

    def delete_image(self, imgid: str):
        conn = self.get_conn()
        conn.delete_image(imgid)

    def delete_volume(self, volumeid: str):
        conn = self.get_conn()
        conn.delete_volume(volumeid)

    def delete_snapshot(self, snapid: str):
        conn = self.get_conn()
        conn.delete_volume_snapshot(snapid)

