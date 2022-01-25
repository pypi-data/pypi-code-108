# -*- coding: future_fstrings -*-
import os
import shutil
import boto3


def upload_code_in_S3(filepath, bucket_name, region, filename=None,is_public=False, prefix=""):
    print("Uploading %s file in S3 region %s" % (filepath, region))
    s3 = boto3.client('s3', region)
    filename = os.path.basename(filepath) if not filename else filename
    if is_public:
        s3.upload_file(filepath, bucket_name, prefix+filename,
                       ExtraArgs={'ACL': 'public-read'})
    else:
        s3.upload_file(filepath, bucket_name, prefix+filename)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
