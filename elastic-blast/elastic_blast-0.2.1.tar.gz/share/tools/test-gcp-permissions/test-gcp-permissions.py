#!/usr/bin/env python3
#                           PUBLIC DOMAIN NOTICE
#              National Center for Biotechnology Information
#  
# This software is a "United States Government Work" under the
# terms of the United States Copyright Act.  It was written as part of
# the authors' official duties as United States Government employees and
# thus cannot be copyrighted.  This software is freely available
# to the public for use.  The National Library of Medicine and the U.S.
# Government have not placed any restriction on its use or reproduction.
#   
# Although all reasonable efforts have been taken to ensure the accuracy
# and reliability of the software and data, the NLM and the U.S.
# Government do not and cannot warrant the performance or results that
# may be obtained by using this software or data.  The NLM and the U.S.
# Government disclaim all warranties, express or implied, including
# warranties of performance, merchantability or fitness for any particular
# purpose.
#   
# Please cite NCBI in any work or product based on this material.
#
import argparse, os, sys

from google.oauth2 import service_account
import googleapiclient.discovery

def test_permissions(project_id: str) -> None:
    """Tests IAM permissions of the caller"""

    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    service = googleapiclient.discovery.build(
        "cloudresourcemanager", "v1", credentials=credentials
    )

    permissions = {
        "permissions": [
            "compute.disks.get",
            "compute.disks.list",
            "compute.disks.delete",
            "compute.disks.update",
            "compute.regions.get",
            "storage.objects.list",
            "serviceusage.services.list",
            "container.clusters.create",
            "container.clusters.delete",
            "container.clusters.get",
            "container.clusters.list",
            "container.clusterRoleBindings.create",
            "container.storageClasses.get",
            "container.clusters.update",
        ]
    }

    request = service.projects().testIamPermissions(
        resource=project_id, body=permissions
    )
    returnedPermissions = request.execute()
    for requested in permissions["permissions"]:
        if requested not in returnedPermissions["permissions"]:
            print(f"ERROR: {requested} permission is NOT available to caller")
    print(f"\nPermissions available to caller in project {project_id}:")
    for p in returnedPermissions["permissions"]:
        print(p)


def create_arg_parser():
    """ Create the command line options parser object for this script. """
    parser = argparse.ArgumentParser(description='Script to test permissions needed to run ElasticBLAST')
    parser.add_argument('--project', metavar='GCP_PROJECT', type=str, 
            help='GCP project name, unless provided via CLOUDSDK_CORE_PROJECT or ELB_GCP_PROJECT')
    return parser


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    gcp_project = None
    if args.project:
        gcp_project = args.project
    elif 'CLOUDSDK_CORE_PROJECT' in os.environ:
        gcp_project = os.environ['CLOUDSDK_CORE_PROJECT']
    elif 'ELB_GCP_PROJECT' in os.environ:
        gcp_project = os.environ['ELB_GCP_PROJECT']

    test_permissions(gcp_project)


if __name__ == "__main__":
    sys.exit(main())
