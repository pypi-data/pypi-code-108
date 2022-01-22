import os
import sys

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(PATH)


from src.winhye_common.utils import CookieRsa


def test_ras():
    obj = CookieRsa()
    # encrypt = obj.rsa_encrypt('text')
    decrypt = obj.rsa_decrypt("RtM26n+1fZ5DMGwLdZCWEYUkGxfntJdIvKgkvX61Qsq1bsTae+vdat37jL9UttUd1wB9vl42nIf00m2eCnky3LZta6/FL3qIyKR5seI4GHsFtY1HyDX4HQR4QvGy7j27o8M5Ow3yYyrNGZLXctXEb1BlqBvoKMsILlnLDdXEk80=")
    # print(encrypt)
    print(decrypt)


if __name__ == '__main__':
    test_ras()
