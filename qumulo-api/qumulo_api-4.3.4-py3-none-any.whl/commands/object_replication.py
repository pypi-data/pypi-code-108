# Copyright (c) 2020 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import argparse

from typing import Optional

import qumulo.lib.opts
import qumulo.rest.object_replication as replication_rest

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection

BUCKET_STYLE_PATH = 'BUCKET_STYLE_PATH'
BUCKET_STYLE_VIRTUAL_HOSTED = 'BUCKET_STYLE_VIRTUAL_HOSTED'
BUCKET_STYLE_CHOICES = [BUCKET_STYLE_PATH, BUCKET_STYLE_VIRTUAL_HOSTED]

DIRECTION_CHOICES = ('COPY_TO_OBJECT', 'COPY_FROM_OBJECT')


def get_secret_access_key(secret_access_key: Optional[str]) -> str:
    if secret_access_key is None:
        secret_access_key = qumulo.lib.opts.read_password(
            prompt='Enter secret access key associated with access key ID: '
        )

    return secret_access_key


class CreateObjectRelationshipCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_create_object_relationship'

    SYNOPSIS = """
    Create an object replication relationship that initiates a copy of file data to or
    from S3.
    """

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--local-directory-id', type=str_decode, help='File ID of the qumulo directory'
        )
        group.add_argument(
            '--local-directory-path', type=str_decode, help='Path of the qumulo directory'
        )

        parser.add_argument(
            '--direction',
            choices=DIRECTION_CHOICES,
            required=True,
            help='Whether data is to be copied to, or from, the object store.',
        )

        parser.add_argument(
            '--object-store-address',
            required=False,
            help="""S3-compatible server address. If omitted, Amazon S3 address
                s3.<region>.amazonaws.com will be used.""",
        )

        parser.add_argument(
            '--object-folder',
            required=True,
            help="""Folder to use in the object store bucket. A slash separator is
                automatically used to specify a folder. For example, a folder "example"
                and a file path (relative to the directory_path) "dir/file" results in
                key "example/dir/file". Use empty value "" or "/" to replicate with
                the root of the bucket.""",
        )
        parser.add_argument(
            '--use-port',
            required=False,
            type=int,
            help="""HTTPS port to use when communicating with the object store
                (default: 443)""",
        )
        parser.add_argument(
            '--ca-certificate',
            type=str_decode,
            help="""Path to a file containing the public certificate of the certificate
                authority to trust for connections to the object store, in PEM format.
                If not specified, the built-in trusted public CAs are used.""",
        )
        parser.add_argument(
            '--bucket',
            required=True,
            help='Bucket in the object store to use for this relationship',
        )
        parser.add_argument(
            '--bucket-addressing-style',
            choices=BUCKET_STYLE_CHOICES,
            help="""Addressing style for requests to the bucket. Set to
                BUCKET_STYLE_PATH for path-style addressing or
                BUCKET_STYLE_VIRTUAL_HOSTED for virtual hosted-style (the default).
                For Amazon S3, virtual hosted-style is recommended as path-style will be
                deprecated. Bucket names containing dots (".") or characters that are
                not valid in domain names may require path-style.
                The object-store-address should not include the bucket name, regardless
                of addressing style.""",
        )
        parser.add_argument(
            '--region', required=True, help='Region the bucket is located in, e.g., us-west-2'
        )
        parser.add_argument(
            '--access-key-id',
            required=True,
            help="""Access key ID to use when communicating with the object store""",
        )
        parser.add_argument(
            '--secret-access-key',
            help="""Secret access key to use when communicating with the object store""",
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        secret_access_key = get_secret_access_key(args.secret_access_key)

        address = args.object_store_address
        if address is None:
            address = f's3.{args.region}.amazonaws.com'

        optional_args = {}

        if args.local_directory_id is not None:
            optional_args['local_directory_id'] = args.local_directory_id

        if args.local_directory_path is not None:
            optional_args['local_directory_path'] = args.local_directory_path

        if args.use_port is not None:
            optional_args['port'] = args.use_port

        if args.ca_certificate is not None:
            with open(args.ca_certificate) as f:
                optional_args['ca_certificate'] = f.read()

        if args.bucket_addressing_style is not None:
            optional_args['bucket_style'] = args.bucket_addressing_style

        print(
            replication_rest.create_object_relationship(
                conninfo,
                credentials,
                direction=args.direction,
                object_store_address=address,
                bucket=args.bucket,
                object_folder=args.object_folder,
                region=args.region,
                access_key_id=args.access_key_id,
                secret_access_key=secret_access_key,
                **optional_args,
            )
        )


class ListObjectRelationshipsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_list_object_relationships'

    SYNOPSIS = 'List all the existing object replication relationships.'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(replication_rest.list_object_relationships(conninfo, credentials))


class GetObjectRelationshipCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_get_object_relationship'

    SYNOPSIS = 'Get the configuration of the specified object replication relationship.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the object replication relationship'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(replication_rest.get_object_relationship(conninfo, credentials, args.id))


class DeleteObjectRelationshipCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_delete_object_relationship'

    SYNOPSIS = (
        'Delete the specified object replication relationship, which must not be running a job.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the object replication relationship'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        replication_rest.delete_object_relationship(conninfo, credentials, args.id)


class AbortObjectReplicationCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_abort_object_replication'

    SYNOPSIS = (
        'Abort any ongoing replication job for the specified object replication relationship.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the object replication relationship'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        replication_rest.abort_object_replication(conninfo, credentials, args.id)


class ListObjectRelationshipStatusesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_list_object_relationship_statuses'

    SYNOPSIS = 'List the statuses for all existing object replication relationships.'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(replication_rest.list_object_relationship_statuses(conninfo, credentials))


class GetObjectRelationshipStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_get_object_relationship_status'

    SYNOPSIS = 'Get current status of the specified object replication relationship.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the object replication relationship'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(replication_rest.get_object_relationship_status(conninfo, credentials, args.id))


class StartObjectRelationshipCommand(qumulo.lib.opts.Subcommand):
    NAME = 'replication_start_object_relationship'

    SYNOPSIS = 'Start a new replication job for an existing object replication relationship'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the object replication relationship'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(replication_rest.replicate_object_relationship(conninfo, credentials, args.id))
