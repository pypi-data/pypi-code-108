# AES加密使用
import base64
#注：python3 安装 Crypto 是 pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pycryptodome<br><br>
from Crypto.Cipher import AES
import hashlib


class UtilsEncrypt():
    def __init__(self):
        pass


    def k_md5(self, s: str):
        """
            function: 获取md5哈希编码后的值;
            输入类型: 必须为str (因为需要encode, 其他类型都不能encode)
            返回类型: 为str
            notes: md5是不可逆的加密 (不属于对称加密和非对称加密)
        """
        if isinstance(s, str) is False:
            raise Exception("[error]: 输入类型不是str\n")
        MD5 = hashlib.md5()
        MD5.update(s.encode("utf-8"))
        encrypted_s = MD5.hexdigest()
        print(f"加密后的值为: {encrypted_s}\n")
        return encrypted_s


    def k_sha256(self, s: str):
        """
            function: 获取sha256哈希编码后的值;
            输入类型: 必须为str (因为需要encode, 其他类型都不能encode)
            返回类型: 为str
            notes: sha256是不可逆的加密 (不属于对称加密和非对称加密)

            (方法与上面的md5基本一样..)
        """
        if isinstance(s, str) is False:
            raise Exception("[error]: 输入类型不是str\n")
        SHA256 = hashlib.sha256()
        SHA256.update(s.encode("utf-8"))
        encrypted_s = SHA256.hexdigest()
        print(f"加密后的值为: {encrypted_s}\n")
        return encrypted_s


    def k_hmac_sha256(self, key, data):
        """
        (网上白嫖来的方法)
            function: 根据 hmac sha256 算法, 使用 key 作为密钥, 对 data 进行加密 (应该是包含了哈希加密和对称加密两部分)
                    (应该是比单纯的sha256更安全?)
            params:
                key: 密钥
                data: 需要加密的数据
            return: 加密后的数据
        """

        import hmac
        data = data.encode('utf-8')
        encrypted_data = hmac.new(key.encode('utf-8'), data, digestmod=hashlib.sha256).hexdigest().upper()
        # print(f"\n\n加密后的数据: {encrypted_data}\n\n")
        return encrypted_data


    def create_encrypted_cookie(self, key: str, salt="618"):
        "通过加盐, 加时间数, 加随机数, 获得一个md5加密后的随机cookies (其实也没必要加密,只是用于记录登录状态,并没有其他作用)"
        "应用场景: 服务端记录这个哈希值, 用于验证浏览器的30分钟有效登录"
        s = key + salt + get_sim_this_time() + str(np.random.randint(10, 1000000))
        encrypted_s = k_md5(s)
        return encrypted_s


    def base64_encrypt(self, data):
        """
        in:
            data: str类型 / bytes类型
        out:
            encrypted_b: bytes类型
        """
        # base64编码
        if type(data) == str:
            encrypted_b = base64.b64encode(data.encode('utf-8'))
        elif type(data) == bytes:
            encrypted_b = base64.b64encode(data)
        print(f"base64加密后的字节码: {encrypted_b}\n")
        return encrypted_b


    def base64_decrypt(self, b):
        """
        in:
            b: bytes类型
        out:
            origin_s: str类型
        """
        # base64解码
        origin_s = base64.b64decode(b).decode("utf-8")
        print(f"base64解密后的'原始字符串': {origin_s}\n")
        return origin_s



class kwEncryption():
    "支持中文的AES加密!!(mode:CBC模式)"
    def __init__(self, key):
        """
        params:
            key: 必须是ascii字符 (不能是中文) (可以不要求16个字符, 因为后续会自动填充)

        function:
            1. 初始化 key值 和 iv值

        notes:
            1. key,iv使用同一个值
            2. key值和iv值必须要16个字节才行, 所以当key小于16位的时候, 使用"!"自动填充
        """
        # key 和 iv 使用同一个值
        key = key.ljust(16,'!')
        self.key = key
        self.iv = key
        self.key_bytes = bytes(key, encoding='utf-8')
        self.iv_bytes = bytes(key, encoding='utf-8')


    def pkcs7padding(self, text):
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
        :param text: 待加密内容(明文)
        :return:
        """
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if(bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text


    def pkcs7unpadding(self, text):
        """
        处理使用PKCS7填充过的数据
        :param text: 解密后的字符串
        :return:
        """
        try:
            length = len(text)
            unpadding = ord(text[length-1])
            return text[0:length-unpadding]
        except Exception as e:
            pass


    def aes_encode(self, content):
        """
        function: AES加密
        参数:
            content: 待加密的内容(原内容)
        模式: cbc
        填充: pkcs7
        return:
            加密后的内容

        """
        cipher = AES.new(self.key_bytes, AES.MODE_CBC, self.iv_bytes)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        aes_encode_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(base64.b64encode(aes_encode_bytes), encoding='utf-8')
        return result


    def aes_decode(self, content):
        """
        function: AES解密
        参数:
            content: 加密后的内容
        模式: cbc
        去填充: pkcs7
        return:
            加密前的内容(原内容)
        """
        try:
            cipher = AES.new(self.key_bytes, AES.MODE_CBC, self.iv_bytes)
            # base64解码
            aes_encode_bytes = base64.b64decode(content)
            # 解密
            aes_decode_bytes = cipher.decrypt(aes_encode_bytes)
            # 重新编码
            result = str(aes_decode_bytes, encoding='utf-8')
            # 去除填充内容
            result = self.pkcs7unpadding(result)
        except Exception as e:
            raise Exception(f"该内容:'{content}', 无法被AES解密!!\n")
            # pass
        if result == None:
            return ""
        else:
            return result



utils_encrypt = UtilsEncrypt()



if __name__ == "__main__":
    # 对中文加密
    x = kwEncryption("kw618").aes_encode("萧山")
    # 对中文解密
    s = kwEncryption("kw618").aes_decode(x)
