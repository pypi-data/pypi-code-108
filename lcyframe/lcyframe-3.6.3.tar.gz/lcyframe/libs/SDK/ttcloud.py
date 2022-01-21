# -*- coding: utf-8 -*-
"""
腾讯云
"""
import base64
from configs import config_tencentcloud

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.iai.v20180301 import iai_client, models

config = config_tencentcloud.get()


# TODO 先安装，后使用：pip install --upgrade tencentcloud-sdk-python

class TencentCloud():
    cred = credential.Credential(config["secretid"], config["secretkey"])

class Iai(TencentCloud):
    """
    人脸识别相关API
    """
    client = iai_client.IaiClient(TencentCloud.cred, "ap-guangzhou")
    client._apiVersion = "2020-03-03"
    client._endpoint = "https://iai.tencentcloudapi.com"

    @classmethod
    def DetectLiveFaceRequest(cls, url=None, image=None):
        """
        人脸静态活体验证：通过后才能注册存库
        """
        req = models.DetectLiveFaceRequest()
        req.FaceModelVersion = "3.0"

        if url:
            req.Url = url
        elif image:
            req.Image = image

        try:
            resp = cls.client.DetectFaceAttributes(req)
            return resp
        except TencentCloudSDKException as e:
            return e

    @classmethod
    def CreateGroup(cls, group_id, group_name, group_desc=[], tag=""):
        """
        创建人员库
        group_id: 系统内确保唯一
        """
        req = models.CreateGroupRequest()
        req.FaceModelVersion = "3.0"

        req.GroupId = str(group_id)
        req.GroupName = str(group_name)
        req.GroupExDescriptions = list(group_desc)
        req.Tag = str(tag) if tag else None

        try:
            resp = cls.client.CreateGroup(req)
            return resp
        except TencentCloudSDKException as e:
            return e

    @classmethod
    def CreatePerson(cls, group_id, person_name, person_id, gender=0, url=None, image=None, UniquePersonControl=2):
        """
        创建人员
        person_id: 内部user_id，确保唯一
        image: 图片 base64 数据，base64 编码后大小不可超过5M。
        jpg格式长边像素不可超过4000，其他格式图片长边像素不可超2000。
        支持PNG、JPG、JPEG、BMP，不支持 GIF 图片。
        url: 图片的 Url 。对应图片 base64 编码后大小不可超过5M。
        jpg格式长边像素不可超过4000，其他格式图片长边像素不可超2000。
        Url、Image必须提供一个，如果都提供，只使用 Url。
        """
        req = models.CreatePersonRequest()

        req.GroupId = str(group_id)
        req.PersonName = str(person_name)
        req.PersonId = str(person_id)
        req.Gender = int(gender)
        req.UniquePersonControl = int(UniquePersonControl) if UniquePersonControl else 0

        if url:
            req.Url = url
        elif image:
            req.Image = image

        try:
            resp = cls.client.CreatePerson(req)
            return resp
        except TencentCloudSDKException as e:
            return e

    @classmethod
    def VerifyFaceRequest(cls, person_id, url=None, image=None):
        """
        人脸验证：用于确认本次上传图与刚才上传的是否为同一人

        person_id: 内部user_id，确保唯一
        image: 图片 base64 数据，base64 编码后大小不可超过5M。
        jpg格式长边像素不可超过4000，其他格式图片长边像素不可超2000。
        支持PNG、JPG、JPEG、BMP，不支持 GIF 图片。
        url: 图片的 Url 。对应图片 base64 编码后大小不可超过5M。
        jpg格式长边像素不可超过4000，其他格式图片长边像素不可超2000。
        Url、Image必须提供一个，如果都提供，只使用 Url。
        """
        req = models.VerifyFaceRequest()
        req.PersonId = str(person_id)

        if url:
            req.Url = url
        elif image:
            req.Image = image

        try:
            resp = cls.client.VerifyFace(req)
            return resp
        except TencentCloudSDKException as e:
            return e

    @classmethod
    def SearchFacesRequest(cls, group_id, url=None, image=None):
        """
        人脸搜索：用于刷脸登录，每次提供一张图片，返回1条最匹配的人员信息
        """
        req = models.SearchFacesRequest()
        req.GroupIds = [str(group_id)]
        if url:
            req.Url = url
        elif image:
            req.Image = image

        try:
            resp = cls.client.SearchFaces(req)
            # {"PersonId": "0", "FaceId": "4100131568524211187", "Score": 100, "PersonName": null, "Gender": null, "PersonGroupInfos": null}
            return resp.Results[0].Candidates[0]
        except TencentCloudSDKException as e:
            return e
        
if __name__ == "__main__":

    # resp = Iai.DetectLiveFaceRequest("https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fattachbak.dataguru.cn%2Fattachments%2Fportal%2F201812%2F29%2F161729gqqfq4qa4oli51oi.jpg&refer=http%3A%2F%2Fattachbak.dataguru.cn&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1619580553&t=a773a07cdaabae7977cf8434278eeacf")
    # resp = Iai.CreateGroup(2, "我是人员库名", ["描述1", "描述2", "描述3"], "我是tag")
    # resp = Iai.CreatePerson(2, "我是人名", "0", url="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fattachbak.dataguru.cn%2Fattachments%2Fportal%2F201812%2F29%2F161729gqqfq4qa4oli51oi.jpg&refer=http%3A%2F%2Fattachbak.dataguru.cn&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1619580553&t=a773a07cdaabae7977cf8434278eeacf")
    # resp = Iai.VerifyFaceRequest("0", url="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fattachbak.dataguru.cn%2Fattachments%2Fportal%2F201812%2F29%2F161729gqqfq4qa4oli51oi.jpg&refer=http%3A%2F%2Fattachbak.dataguru.cn&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1619580553&t=a773a07cdaabae7977cf8434278eeacf")
    resp = Iai.SearchFacesRequest("2", url="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fattachbak.dataguru.cn%2Fattachments%2Fportal%2F201812%2F29%2F161729gqqfq4qa4oli51oi.jpg&refer=http%3A%2F%2Fattachbak.dataguru.cn&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1619580553&t=a773a07cdaabae7977cf8434278eeacf")
    print(resp)
