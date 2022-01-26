"""Implement utilities for transferring data to/from Terality.

Data transfers are usually done in two separate steps, one transfer between Terality internal systems
and a Terality export S3 bucket, and one transfer between a Terality export S3 bucket and a user-controlled
system. This two-step process has the advantage of simplicity (the implementation of these two steps
is decoupled).

When copying between Terality transfer buckets and other cloud storage systems (AWS S3, Azure Datalake...),
the copy is performed server-side to avoid the client having to download and reupload files.

There are some details in the implementation that are mostly the result of incremental design decisions.
Some simplifications are probably possible. Below is a high level overview of the flow.

Security
~~~~~~~~

At no point the Terality API gets access to the user cloud credentials. When copying to or from a cloud
storage provider, the Terality client generates pre-signed URLs (or the equivalent for the cloud provider
at hand) using the user local credentials, and send these URLs to the server.  These URLs have a limited
expiry time and don't carry any privileges (outside the pre-signed API call).

When the client calls the S3 API on a Terality export bucket, it uses temporary credentials generated
by the Terality server. We don't depend on the user credentials having enough S3 permissions to access the
Terality bucket.

Imports
~~~~~~~

First step: copy from the user-controlled system to the Terality export S3 bucket
 -> For local files, directly upload the file using the boto3 library (using credentials provided by
    the Terality API).
 -> For files stored in a S3 bucket, generate pre-signed URLs for the GetObject operation (using user
    credentials as discovered by boto3), send these URLs to the Terality API. The copy is implemented
    server-side.
 -> For files stored in an Azure Gen2 Datalake filesystem, generate shared access signature for each
    file (= blob) to copy. Send these signatures to the Terality API. The copy is implemented server-side.
This generates a transfer ID.

Second step: import data into Terality
 -> Call the `read_csv`, `read_parquet`... pandas function passing the location (transfer ID + AWS region)
    of the S3 objects in the Terality import bucket.

Exports
~~~~~~~

First step: export data from Terality to a Terality export bucket
 -> Call the `to_csv`, `to_parquet`... pandas function. The API returns a transfer ID.

Second step: copy from the Terality export S3 bucket to the user-controlled system
 -> Download to a local file: directly download the file using the boto3 library
    (using credentials provided by the Terality API).
 -> Copy to a S3 bucket: the client starts a multipart upload (using user credentials as discovered by
    boto3), generates a list of presigned URLs (one for each part to write), send these URLs to the server,
    then complete the multipart upload. The actual copy is performed server-side.
 -> Copy to an Azure Gen2 Datalake filesystem: the client generates shared access signature for each
    file (= blob) to copy. The client sends these signatures to the Terality API. The copy is
    implemented server-side.
"""
from .s3 import (
    upload_s3_files,
    copy_to_user_s3_bucket,
)
from .local import (
    upload_local_files,
)

# Don't import Azure here, because the Azure dependency is optional and the import may fail.
