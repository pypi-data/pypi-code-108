"""
焕影小程序功能服务端的基本工具函数,以类的形式封装
"""
try:  # 加上这个try的原因在于本地环境和云函数端的import形式有所不同
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
except ImportError:
    try:
        from qcloud_cos_v5 import CosConfig
        from qcloud_cos_v5 import CosS3Client
    except ImportError:
        raise ImportError("请下载腾讯云COS相关代码包:pip install cos-python-sdk-v5")
import requests
import json
import cv2
import numpy as np
from hyService.utils import Debug, GetConfig
import os
local_path = os.path.dirname(__file__)

class CosConf(Debug, GetConfig):
    """
    从安全的角度出发,将一些默认配置文件上传至COS中,接下来使用COS和它的子类的时候,在第一次使用时需要输入Cuny给的id和key
    用于连接cos存储桶,下载配置文件.
    当然,在service_default_download = False的时候,如果在运行路径下已经有conf/service_config.json文件了,
    那么就不用再次下载了,也不用输入id和key
    事实上这只需要运行一次,因为配置文件将会被下载至源码文件夹中
    如果要自定义路径,请在继承的子类中编写__init__函数,将service_path定向到指定路径
    """
    __SECRET_ID:str = None  # 服务的id
    __SECRET_KEY:str = None  # 服务的key
    __REGION: str = None  # 服务的存储桶地区
    __TOKEN:str = None  # 服务的token,目前一直是None
    __SCHEME:str = None  # 服务的访问协议,默认实际上是https
    __BUCKET:str = None  # 服务的存储桶
    __SERVICE_CONFIG:dict = None  # 服务的配置文件
    service_path:str = f"{local_path}/conf/service_config.json"  #配置文件路径,默认是函数运行的路径下的conf文件夹
    service_default_download = False  # 是否在每次访问配置的时候都重新下载文件
    @property
    def service_config(self):
        if self.__SERVICE_CONFIG is None or self.service_default_download is True:
            self.__SERVICE_CONFIG = self.load_json(self.service_path, self.service_default_download)
        return self.__SERVICE_CONFIG

    @property
    def client(self):
        client_config = CosConfig(Region=self.region,
                                  SecretId=self.secret_id,
                                  SecretKey=self.secret_key,
                                  Token=self.token,
                                  Scheme=self.scheme)
        return CosS3Client(client_config)

    def get_key(self, key:str):
        try:
            data = self.service_config[key]
            if data == "None":
                return None
            else:
                return data
        except KeyError:
            self.debug_print(f"没有对应键值{key},默认返回None", font_color="red")
            return None

    @property
    def secret_id(self):
        if self.__SECRET_ID is None:
            self.__SECRET_ID = self.get_key("SECRET_ID")
        return self.__SECRET_ID

    @secret_id.setter
    def secret_id(self, value:str):
        self.__SECRET_ID = value

    @property
    def secret_key(self):
        if self.__SECRET_KEY is None:
            self.__SECRET_KEY = self.get_key("SECRET_KEY")
        return self.__SECRET_KEY

    @secret_key.setter
    def secret_key(self, value:str):
        self.__SECRET_KEY = value

    @property
    def region(self):
        if self.__REGION is None:
            self.__REGION = self.get_key("REGION")
        return self.__REGION

    @region.setter
    def region(self, value:str):
        self.__REGION = value

    @property
    def token(self):
        # if self.__TOKEN is None:
        #     self.__TOKEN = self.get_key("TOKEN")
        # 这里可以注释掉
        return self.__TOKEN

    @token.setter
    def token(self, value:str):
        self.__TOKEN= value

    @property
    def scheme(self):
        if self.__SCHEME is None:
            self.__SCHEME = self.get_key("SCHEME")
        return self.__SCHEME

    @scheme.setter
    def scheme(self, value:str):
        self.__SCHEME = value

    @property
    def bucket(self):
        if self.__BUCKET is None:
            self.__BUCKET = self.get_key("BUCKET")
        return self.__BUCKET

    @bucket.setter
    def bucket(self, value):
        self.__BUCKET = value

    def downloadFile_COS(self, key, bucket:str=None, if_read:bool=False):
        """
        从COS下载对象(二进制数据), 如果下载失败就返回None
        """
        CosBucket = self.bucket if bucket is None else bucket
        try:
            self.debug_print(f"Download from {CosBucket}", font_color="blue")
            obj = self.client.get_object(
                Bucket=CosBucket,
                Key=key
            )
            if if_read is True:
                data = obj["Body"].get_raw_stream().read()  # byte
                return data
            else:
                return obj
        except Exception as e:
            self.debug_print(f"{e}", font_color="red")
            return None

    def showFileList_COS_base(self, key, bucket, marker:str=""):
        """
        返回cos存储桶内部的某个文件夹的内部名称
        :param key: cos云端的存储路径
        :param bucket: cos存储桶名称，如果没指定名称（None）就会寻找默认的存储桶
        :param marker: 标记,用于记录上次查询到哪里了
        ps:如果需要修改默认的存储桶配置，请在代码运行的时候加入代码 s.bucket = 存储桶名称 （s是对象实例）
        返回的内容存储在response["Content"]，不过返回的数据大小是有限制的，具体内容还是请看官方文档。
        """
        response = self.client.list_objects(
            Bucket=bucket,
            Prefix=key,
            Marker=marker
        )
        return response

    def showFileList_COS(self, key, bucket:str=None)->list:
        """
        实现查询存储桶中所有对象的操作，因为cos的sdk有返回数据包大小的限制，所以我们需要进行一定的改动
        """
        marker = ""
        file_list = []
        CosBucket = self.bucket if bucket is None else bucket
        while True:  # 轮询
            response = self.showFileList_COS_base(key, CosBucket, marker)
            try:
                file_list.extend(response["Contents"])
            except KeyError:
                pass
            if response['IsTruncated'] == 'false':
                # todo 后续加个无数据的debug报警
                break
            file_list.extend(response["Contents"])
            marker = response['NextMarker']
        return file_list

    def uploadFile_COS(self, buffer, key, bucket:str=None):
        """
        从COS上传数据,需要注意的是必须得是二进制文件
        """
        CosBucket = self.bucket if bucket is None else bucket
        try:
            self.client.put_object(
                Bucket=CosBucket,
                Body=buffer,
                Key=key
            )
            return True
        except Exception as e:
            print(e)
            return False

class ResponseWebSocket(CosConf):
    # 网关推送地址
    __HOST:str = None
    @property
    def sendBackHost(self):
        if self.__HOST is None:
            self.__HOST = self.get_key("HOST")
        return self.__HOST

    @sendBackHost.setter
    def sendBackHost(self, value):
        self.__HOST = value

    def sendMsg_toWebSocket(self, message,connectionID:str = None):
        if connectionID is not None:
            retmsg = {'websocket': {}}
            retmsg['websocket']['action'] = "data send"
            retmsg['websocket']['secConnectionID'] = connectionID
            retmsg['websocket']['dataType'] = 'text'
            retmsg['websocket']['data'] = json.dumps(message)
            requests.post(self.sendBackHost, json=retmsg)
            print("send success!")
        else:
            pass

    @staticmethod
    def create_Msg(status, msg):
        """
        本方法用于创建一个用于发送到WebSocket客户端的数据
        输入的信息部分,需要有如下几个参数:
        1. id,固定为"return-result"
        2. status,如果输入为1则status=true, 如果输入为-1则status=false
        3. obj_key, 图片的云端路径, 这是输入的msg本身自带的
        """
        msg['status'] = "false" if status == -1 else 'true'  # 其实最好还是用bool
        msg['id'] = "async-back-msg"
        msg['type'] = "funcType"
        msg["format"] = "imageType"
        return msg

class Service(ResponseWebSocket):
    """
    服务的主函数,封装了cos上传\下载功能以及与api网关的一键通讯
    将类的实例变成一个可被调用的对象,在服务运行的时候,只需要运行该对象即可
    当然,因为是类,所以支持继承和修改
    """
    @staticmethod
    def byte_cv2(image_byte, flags=cv2.IMREAD_COLOR) ->np.ndarray:
        """
        将传入的字节流解码为图像, 当flags为 -1 的时候为无损解码
        """
        np_arr = np.frombuffer(image_byte,np.uint8)
        image = cv2.imdecode(np_arr, flags)
        return image

    @staticmethod
    def cv2_byte(image:np.ndarray, imageType:str=".jpg"):
        """
        将传入的图像解码为字节流
        """
        _, image_encode = cv2.imencode(imageType, image)
        image_byte = image_encode.tobytes()
        return image_byte

    def process(self, *args, **kwargs) ->np.ndarray:
        """
        处理函数,在使用的时候请将之重构
        """
        pass

    def __call__(self, *args, **kwargs):
        """
        调用函数，下面的调用函数实际上是一个模板，后续是可以重写的
        *args, **kwargs用于方便继承时候的拓展
        下列模板仅仅是一种服务的使用方式：
        前端传入特定格式的信息，本方法通过前端信息下载cos图片
        根据下载的图片“直接”输入到process()方法中，得到结果图片，然后再上传至cos
        根据前端的信息格式，本模板自动判定是否需要回传消息（但是无论是否回传，消息都在代码执行的时候被生成了）
        实际上“判定”的工作被封装在sendMsg_toWebSocket方法中，如果connectionID为None（即前端信息中没有单独的connectionID），
        就不发送数据。
        """
        msg = kwargs["msg"]
        # print("GET", msg)
        back_msg = {}  # 回传消息
        connectionID = None
        try:
            # 初始化一些数据
            send_msg: dict = msg["send_msg"]  # 获得cos数据字典
            download_path: str = send_msg["obj_key"]  # 获得cos下载路径
            upload_path = download_path.replace("old-image", "new-image")  # 获得cos上传路径
            back_msg["time"] = send_msg["time"]  # 时间戳
            back_msg["uid"] = send_msg["uid"]  # 用户id
            back_msg["hd_key"] = upload_path  # 回传云端结果图片路径
            connectionID = msg["connectionID"] if "connectionID" in msg.keys() else None  # 获得长连接id
            # 开始处理
            print("start...")
            resp = self.downloadFile_COS(download_path, if_read=False)  # 下载图片
            image_byte = resp['Body'].get_raw_stream().read()  # 读取二进制图片
            image_pre = self.byte_cv2(image_byte, flags=cv2.IMREAD_COLOR)  # 将二进制图片转为cv2格式
            # 数据图片下载完毕，开始功能处理
            print("processing...")
            image = self.process(image_pre)
            image_byte = self.cv2_byte(image, imageType=".jpg")  # 将处理完毕的图片转为二进制格式
            self.uploadFile_COS(buffer=image_byte, key=upload_path)  # 将字节流图片上传至cos
            back_msg = self.create_Msg(status=1, msg=back_msg)  # 处理成功,在回传消息中添加成功的消息
            print("success!")
        except Exception as e:
            # 处理失败
            print(e)
            back_msg = self.create_Msg(status=-1, msg=back_msg)  # 给WebSocket返回一个处理失败的消息
            print("fail!")
        self.sendMsg_toWebSocket(message=back_msg, connectionID=connectionID)  # 向websocket返回消息


if __name__ == "__main__":
    s = Service()
