"""
@author: cuny
@fileName: utils.py
@create_time: 2021/12/29 下午1:29
@introduce:
焕影服务的一些工具函数,涉及两类:
1. 开发debug时候的工具函数
2. 初始化COS配置时的工具函数
"""
try:  # 加上这个try的原因在于本地环境和云函数端的import形式有所不同
    import qcloud_cos
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
except ImportError:
    try:
        from qcloud_cos_v5 import CosConfig
        from qcloud_cos_v5 import CosS3Client
    except ImportError:
        raise ImportError("请下载腾讯云COS相关代码包:pip install cos-python-sdk-v5")
import os
import json
import cv2
import numpy as np

class ProcessError(Exception):
    def __init__(self, err):
        super().__init__(err)
        self.err = err
    def __str__(self):
        return self.err

class WrongImageType(TypeError):
    def __init__(self, err):
        super().__init__(err)
        self.err = err
    def __str__(self):
        return self.err


class GetConfig(object):
    @staticmethod
    def hy_sdk_client(Id:str, Key:str):
        # 从cos中寻找文件
        REGION: str = 'ap-beijing'
        TOKEN = None
        SCHEME: str = 'https'
        BUCKET: str = 'hy-sdk-config-1305323352'
        client_config = CosConfig(Region=REGION,
                                  SecretId=Id,
                                  SecretKey=Key,
                                  Token=TOKEN,
                                  Scheme=SCHEME)
        return CosS3Client(client_config), BUCKET

    def load_json(self, path:str, default_download=False):
        try:
            if os.path.isdir(path):
                raise ProcessError("请输入具体的配置文件路径,而非文件夹!")
            if default_download is True:
                print(f"\033[34m 默认强制重新下载配置文件...\033[0m")
                raise FileNotFoundError
            with open(path) as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            dir_name = os.path.dirname(path)
            try:
                os.makedirs(dir_name)
            except FileExistsError:
                pass
            base_name = os.path.basename(path)
            print(f"\033[34m 正在从COS中下载配置文件...\033[0m")
            print(f"\033[31m 请注意,接下来会在{dir_name}路径下生成文件{base_name}...\033[0m")
            Id = input("请输入SecretId:")
            Key = input("请输入SecretKey:")
            client, bucket = self.hy_sdk_client(Id, Key)
            data_bytes = client.get_object(Bucket=bucket,Key=base_name)["Body"].get_raw_stream().read()
            data = json.loads(data_bytes.decode("utf-8"))
            # data["SecretId"] = Id  # 未来可以把这个加上
            # data["SecretKey"] = Key
            with open(path, "w") as f:
                data_str = json.dumps(data, ensure_ascii=False)
                # 如果 ensure_ascii 是 true (即默认值),输出保证将所有输入的非 ASCII 字符转义。
                # 如果 ensure_ascii 是 false，这些字符会原样输出。
                f.write(data_str)
                f.close()
            print(f"\033[32m 配置文件保存成功\033[0m")
            return data
        except json.decoder.JSONDecodeError:
            print(f"\033[31m WARNING: 配置文件为空!\033[0m")
            return {}

    def load_file(self, cloud_path:str, local_path:str):
        """
        从COS中下载文件到本地,本函数将会被默认执行的,在使用的时候建议加一些限制.
        :param cloud_path: 云端的文件路径
        :param local_path: 将云端文件保存在本地的路径
        """
        if os.path.isdir(cloud_path):
            raise ProcessError("请输入具体的云端文件路径,而非文件夹!")
        if os.path.isdir(local_path):
            raise ProcessError("请输入具体的本地文件路径,而非文件夹!")
        dir_name = os.path.dirname(local_path)
        base_name = os.path.basename(local_path)
        try:
            os.makedirs(dir_name)
        except FileExistsError:
            pass
        cloud_name = os.path.basename(cloud_path)
        print(f"\033[31m 请注意,接下来会在{dir_name}路径下生成文件{base_name}\033[0m")
        Id = input("请输入SecretId:")
        Key = input("请输入SecretKey:")
        client, bucket = self.hy_sdk_client(Id, Key)
        print(f"\033[34m 正在从COS中下载文件: {cloud_name}, 此过程可能耗费一些时间...\033[0m")
        data_bytes = client.get_object(Bucket=bucket,Key=cloud_path)["Body"].get_raw_stream().read()
        # data["SecretId"] = Id  # 未来可以把这个加上
        # data["SecretKey"] = Key
        with open(local_path, "wb") as f:
            # 如果 ensure_ascii 是 true (即默认值),输出保证将所有输入的非 ASCII 字符转义。
            # 如果 ensure_ascii 是 false，这些字符会原样输出。
            f.write(data_bytes)
            f.close()
        print(f"\033[32m 文件保存成功\033[0m")

    def update_config(self, path:str):
        if os.path.isdir(path):
            raise ProcessError("请输入具体的配置文件路径,而非文件夹!")
        base_name = os.path.basename(path)
        print(f"\033[34m 正在保存{base_name}到COS中...\033[0m")
        try:
            with open(path) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"\033[31m {path}文件不存在!\033[0m")
        try:
            Id = data["SecretId"]
            Key = data["SecretKey"]
        except KeyError:
            Id = input("请输入SecretId:")
            Key = input("请输入SecretKey:")
        client, bucket = self.hy_sdk_client(Id, Key)
        a = json.dumps(data)
        try:
            client.put_object(Bucket=bucket,Body=a,Key=base_name)
        except qcloud_cos.cos_exception.CosServiceError:
            print(f"\033[31m 本h函数暂时不可用, 云端COS的权限为只可读不可写\033[0m")
            print(f"\033[31m 保存失败!\033[0m")
        return True


class Debug(object):
    color_dir:dict = {
        "red":"31m",
        "green":"32m",
        "yellow":"33m",
        "blue":"34m",
        "common":"38m"
    }  # 颜色值
    __DEBUG:bool = True

    @property
    def debug(self):
        return self.__DEBUG

    @debug.setter
    def debug(self, value):
        if not isinstance(value, bool):
            raise TypeError("你必须设定debug的值为bool的True或者False")
        print(f"设置debug为: {value}")
        self.__DEBUG = value

    def debug_print(self, text, **kwargs):
        if self.debug is True:
            key = self.color_dir["common"] if "font_color" not in kwargs else self.color_dir[kwargs["font_color"]]
            print(f"\033[{key}{text}\033[0m")

    @staticmethod
    def resize_image_esp(input_image, esp=2000):
        """
        输入：
        input_path：numpy图片
        esp：限制的最大边长
        """
        # resize函数=>可以让原图压缩到最大边为esp的尺寸(不改变比例)
        width = input_image.shape[0]

        length = input_image.shape[1]
        max_num = max(width, length)

        if max_num > esp:
            print("Image resizing...")
            if width == max_num:
                length = int((esp / width) * length)
                width = esp

            else:
                width = int((esp / length) * width)
                length = esp
            print(length, width)
            im_resize = cv2.resize(input_image, (length, width), interpolation=cv2.INTER_AREA)
            return im_resize
        else:
            return input_image

    def cv_show(self, *args, **kwargs):
        def check_images(img):
            # 判断是否是矩阵类型
            if not isinstance(img, np.ndarray):
                raise WrongImageType("输入的图像必须是 np.ndarray 类型!")
        if self.debug is True:
            size = 500 if "size" not in kwargs else kwargs["size"]  # 默认缩放尺寸为最大边500像素点
            if len(args) == 0:
                raise ProcessError("你必须传入若干图像信息!")
            flag = False
            base = None
            for image in args:
                check_images(image)
                if flag is False:
                    image = self.resize_image_esp(image, size)
                    h, w, c = image.shape
                    flag = (w, h)
                    base = image
                else:
                    image = cv2.resize(image, flag)
                    base = np.hstack((base, image))
            title = "cv_show" if "winname" not in kwargs else kwargs["winname"]
            cv2.imshow(title, base)
            cv2.waitKey(0)
        else:
            pass


if __name__ == "__main__":
    gc = GetConfig()
    gc.load_json("conf/params.json", default_download=True)
    # update_config("conf/params.json")