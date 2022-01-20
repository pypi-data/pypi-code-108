import requests
import hashlib


# 超级鹰打码平台: 官方Demo
class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = hashlib.md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()



# 使用超级鹰打码!!
def ocr_captcha(img_bytes, captcha_type=4004):
    """
        captcha_type: 4004(4位纯数字): 平均10分一次. (我目前有1750分)
        超级鹰类的使用: Chaojiying_Client(<用户名>, <密码>, <软件ID>)
    """

    chaojiying = Chaojiying_Client('15168201914', '21nozui', '899088')
    # img_bytes = open('/Users/kerwin/captcha.jpg', 'rb').read()
    img_result_dict = chaojiying.PostPic(img_bytes, captcha_type)
    return img_result_dict


def main():
    import kwtools
    kwtools_full_path = kwtools.__path__
    img_bytes = open('kwtools_full_path/box/captcha.jpg', 'rb').read()
    img_result_dict = ocr_captcha(img_bytes)
    print(img_result_dict)


if __name__ == '__main__':
    print("start!")
    main()
    print("end!")
