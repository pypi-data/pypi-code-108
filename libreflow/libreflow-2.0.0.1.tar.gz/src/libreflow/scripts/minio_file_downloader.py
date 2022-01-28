import os
import sys
from minio import Minio


server_url = sys.argv[1]
access_key = sys.argv[2]
secret_key = sys.argv[3]
local_path = sys.argv[4]
server_path = sys.argv[5]

minioClient = Minio(server_url,
                  access_key=access_key,
                  secret_key=secret_key,
                  secure=True)

minioClient.fget_object(
    "testbucked",
    server_path,
    local_path
)
