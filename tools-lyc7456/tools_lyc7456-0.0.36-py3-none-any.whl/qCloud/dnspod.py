import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

# Write by lyc at 2021-12-6

class DNSPOD():
    """[腾讯云Dnspod Python3 SDK方法封装]
    """
    def __init__(self, key) -> None:
        self.SecretId = key['SecretId']             # 公钥
        self.SecretKey = key['SecretKey']           # 私钥
        self.endpoint = 'dnspod.tencentcloudapi.com'      # 接口地址

        # 签名
        self.cred = credential.Credential(self.SecretId, self.SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = self.endpoint

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = dnspod_client.DnspodClient(self.cred, "", clientProfile)


    def describeDomainList(self):
        """[获取域名列表]https://cloud.tencent.com/document/api/1427/56172

        Returns:
            [json]: [json response]
        """
        try:
            req = models.DescribeDomainListRequest()
            params = {

            }
            req.from_json_string(json.dumps(params))

            resp = self.client.DescribeDomainList(req)
            # print(resp.to_json_string())
            return resp.to_json_string()

        except TencentCloudSDKException as err:
            # print(err)
            return err

