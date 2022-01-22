import os
import sys

PATH = os.path.abspath(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(PATH)
print(PATH)

from src.winhye_common.utils.oss_base import OssBucket


def test_oss():
    oss_config = {
        "AccessKey_ID": "LTAI5tFbpMr1R4CVCbUePMWy",
        "AccessKey_Secret": "MJ2WWUbIKDg4UY5EbEsgQ983Lkfwff",
        "endpoint": "oss-cn-beijing.aliyuncs.com",
        "bucket_name": "winhye-kaifa"
    }
    oss_conn = OssBucket(
        oss_config["AccessKey_ID"],
        oss_config["AccessKey_Secret"],
        oss_config["endpoint"],
        oss_config["bucket_name"]
    )
    # url = oss_conn.upload_from_file("123.txt", "123.txt")
    oss_conn.del_file("123.txt")


if __name__ == '__main__':
    test_oss()
