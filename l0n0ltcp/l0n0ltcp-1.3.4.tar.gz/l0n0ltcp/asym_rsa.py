import rsa
from l0n0ltcp.asym_enc_base import AsymDecBase, AsymEncBase

help_info = """
RSA私钥格式PKCS1和PKCS8相互转换
RSA公钥格式PKCS1和PKCS8相互转换
以下转换基于openssl命令的操作；
1. openssl 生成pkcs1格式的私钥，密钥长度1024位, (PKCS1)
openssl genrsa -out private.pem 1024

-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDlLm5+Kosybacfp8hzjn1fl2wT7Au2lm5SEtz6r+/wwSfq5KfY
H8q1AO/C92IwEpplNbrqYmOXQu6P07mg0lQOCvE5sdtmAvD2ex3wCef8lWmgdh5q
Uo4OMcmoSz3IAp/7/FnMag1IelSfdronPBDxazp6NUmQZITsYK6CsEl/ewIDAQAB
AoGBAJkMdvF+i9Kzc6YqMC0rfQJ3Zs+vFOtsbmQVAMnQ8JWBCJ1O8d/c60wRQgyb
lFCyO7VXOmoIJqX/Jr2aER8bFtG+Yxy6jsMu3ynwMwbhcVmCWCmZoWuE5pZdEJk6
lOdOay7TkE45X/Wc7K9iZs2uuB7sylIvK/HVxxit6FGePa4RAkEA9e+VoAbxBv78
HyxRcStW+Kc3lmE4zYBGAb2IYx48UEN34nP5rI8Tusqsy7CZ3rvSMi1CpVlj2eQK
FU8FzVFyjwJBAO6PU9q7il8NtecdvYBkDErlCawSeCdk9s79helT0Mrg9cWaVWFO
n0UxgT55MPXWGdMRXUUOCNnMilaw/p7dKlUCQDpjGeu3GivmB2dDN0ad2nUIBftu
s3SeWoB5RdL6T6liiyi5DfJ4uV9kVKe7Epy9jIabFjJ5SWpmaDps21zGVGMCQQCB
HvK0IW3zpOgf/+jh5UUCBJYHnLeMGwm7X11rvQH1zW05Vx9/W565ROI/fjkR1qCD
rZJeHgqMWDlIUuR9+BdBAkAI8+JWgWLdWceXX9Puu4KNmGukx4GZw2n53vMKp0Fu
puQxMonRWTN+kA76cq8QIj8xuEBkdxy1NFRMEkGu675m
-----END RSA PRIVATE KEY-----

2. PKCS1私钥转换为PKCS8

openssl pkcs8 -topk8 -inform PEM -in private.pem -outform pem -nocrypt -out pkcs8.pem


-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAOUubn4qizJtpx+n
yHOOfV+XbBPsC7aWblIS3Pqv7/DBJ+rkp9gfyrUA78L3YjASmmU1uupiY5dC7o/T
uaDSVA4K8Tmx22YC8PZ7HfAJ5/yVaaB2HmpSjg4xyahLPcgCn/v8WcxqDUh6VJ92
uic8EPFrOno1SZBkhOxgroKwSX97AgMBAAECgYEAmQx28X6L0rNzpiowLSt9Andm
z68U62xuZBUAydDwlYEInU7x39zrTBFCDJuUULI7tVc6aggmpf8mvZoRHxsW0b5j
HLqOwy7fKfAzBuFxWYJYKZmha4Tmll0QmTqU505rLtOQTjlf9Zzsr2Jmza64HuzK
Ui8r8dXHGK3oUZ49rhECQQD175WgBvEG/vwfLFFxK1b4pzeWYTjNgEYBvYhjHjxQ
Q3fic/msjxO6yqzLsJneu9IyLUKlWWPZ5AoVTwXNUXKPAkEA7o9T2ruKXw215x29
gGQMSuUJrBJ4J2T2zv2F6VPQyuD1xZpVYU6fRTGBPnkw9dYZ0xFdRQ4I2cyKVrD+
nt0qVQJAOmMZ67caK+YHZ0M3Rp3adQgF+26zdJ5agHlF0vpPqWKLKLkN8ni5X2RU
p7sSnL2MhpsWMnlJamZoOmzbXMZUYwJBAIEe8rQhbfOk6B//6OHlRQIElgect4wb
CbtfXWu9AfXNbTlXH39bnrlE4j9+ORHWoIOtkl4eCoxYOUhS5H34F0ECQAjz4laB
Yt1Zx5df0+67go2Ya6THgZnDafne8wqnQW6m5DEyidFZM36QDvpyrxAiPzG4QGR3
HLU0VEwSQa7rvmY=
-----END PRIVATE KEY-----

3. PKCS8格式私钥再转换为PKCS1格式

openssl rsa -in pkcs8.pem -out pkcs1.pem


-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDlLm5+Kosybacfp8hzjn1fl2wT7Au2lm5SEtz6r+/wwSfq5KfY
H8q1AO/C92IwEpplNbrqYmOXQu6P07mg0lQOCvE5sdtmAvD2ex3wCef8lWmgdh5q
Uo4OMcmoSz3IAp/7/FnMag1IelSfdronPBDxazp6NUmQZITsYK6CsEl/ewIDAQAB
AoGBAJkMdvF+i9Kzc6YqMC0rfQJ3Zs+vFOtsbmQVAMnQ8JWBCJ1O8d/c60wRQgyb
lFCyO7VXOmoIJqX/Jr2aER8bFtG+Yxy6jsMu3ynwMwbhcVmCWCmZoWuE5pZdEJk6
lOdOay7TkE45X/Wc7K9iZs2uuB7sylIvK/HVxxit6FGePa4RAkEA9e+VoAbxBv78
HyxRcStW+Kc3lmE4zYBGAb2IYx48UEN34nP5rI8Tusqsy7CZ3rvSMi1CpVlj2eQK
FU8FzVFyjwJBAO6PU9q7il8NtecdvYBkDErlCawSeCdk9s79helT0Mrg9cWaVWFO
n0UxgT55MPXWGdMRXUUOCNnMilaw/p7dKlUCQDpjGeu3GivmB2dDN0ad2nUIBftu
s3SeWoB5RdL6T6liiyi5DfJ4uV9kVKe7Epy9jIabFjJ5SWpmaDps21zGVGMCQQCB
HvK0IW3zpOgf/+jh5UUCBJYHnLeMGwm7X11rvQH1zW05Vx9/W565ROI/fjkR1qCD
rZJeHgqMWDlIUuR9+BdBAkAI8+JWgWLdWceXX9Puu4KNmGukx4GZw2n53vMKp0Fu
puQxMonRWTN+kA76cq8QIj8xuEBkdxy1NFRMEkGu675m
-----END RSA PRIVATE KEY-----

可以看出结果和1是一致的；

4. 从pkcs1私钥中生成pkcs8公钥

openssl rsa -in private.pem -pubout -out public.pem


-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlLm5+Kosybacfp8hzjn1fl2wT
7Au2lm5SEtz6r+/wwSfq5KfYH8q1AO/C92IwEpplNbrqYmOXQu6P07mg0lQOCvE5
sdtmAvD2ex3wCef8lWmgdh5qUo4OMcmoSz3IAp/7/FnMag1IelSfdronPBDxazp6
NUmQZITsYK6CsEl/ewIDAQAB
-----END PUBLIC KEY-----

5. 从pkcs8私钥中生成pkcs8公钥
openssl rsa -in pkcs8.pem -pubout -out public_pkcs8.pem


-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlLm5+Kosybacfp8hzjn1fl2wT
7Au2lm5SEtz6r+/wwSfq5KfYH8q1AO/C92IwEpplNbrqYmOXQu6P07mg0lQOCvE5
sdtmAvD2ex3wCef8lWmgdh5qUo4OMcmoSz3IAp/7/FnMag1IelSfdronPBDxazp6
NUmQZITsYK6CsEl/ewIDAQAB
-----END PUBLIC KEY-----

可以看出结果和4是一样的；


6. pkcs8公钥转pkcs1公钥

openssl rsa -pubin -in public.pem -RSAPublicKey_out


-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAOUubn4qizJtpx+nyHOOfV+XbBPsC7aWblIS3Pqv7/DBJ+rkp9gfyrUA
78L3YjASmmU1uupiY5dC7o/TuaDSVA4K8Tmx22YC8PZ7HfAJ5/yVaaB2HmpSjg4x
yahLPcgCn/v8WcxqDUh6VJ92uic8EPFrOno1SZBkhOxgroKwSX97AgMBAAE=
-----END RSA PUBLIC KEY-----


openssl rsa -pubin -in public_pkcs8.pem -RSAPublicKey_out

-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAOUubn4qizJtpx+nyHOOfV+XbBPsC7aWblIS3Pqv7/DBJ+rkp9gfyrUA
78L3YjASmmU1uupiY5dC7o/TuaDSVA4K8Tmx22YC8PZ7HfAJ5/yVaaB2HmpSjg4x
yahLPcgCn/v8WcxqDUh6VJ92uic8EPFrOno1SZBkhOxgroKwSX97AgMBAAE=
-----END RSA PUBLIC KEY-----

可以看出转换的结果是一致的；

7. pkcs1公钥转换为pkcs8公钥

openssl rsa -RSAPublicKey_in -in pub_pkcs1.pem -pubout


-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlLm5+Kosybacfp8hzjn1fl2wT
7Au2lm5SEtz6r+/wwSfq5KfYH8q1AO/C92IwEpplNbrqYmOXQu6P07mg0lQOCvE5
sdtmAvD2ex3wCef8lWmgdh5qUo4OMcmoSz3IAp/7/FnMag1IelSfdronPBDxazp6
NUmQZITsYK6CsEl/ewIDAQAB
-----END PUBLIC KEY-----

"""


class AsymRsaEnc(AsymEncBase):
    def __init__(self, public_key: bytes, format: str = "PEM") -> None:
        self.key = rsa.PublicKey.load_pkcs1(public_key, format)

    def encode(self, data: bytes) -> bytes:
        return rsa.encrypt(data, self.key)

    def print_help(self):
        print(help_info)


class AsymRsaDec(AsymDecBase):
    def __init__(self, private_key: bytes, format: str = "PEM") -> None:
        self.key = rsa.PrivateKey.load_pkcs1(private_key, format)

    def decode(self, data: bytes) -> bytes:
        return rsa.decrypt(data, self.key)

    def print_help(self):
        print(help_info)

if __name__ == "__main__":
    with open("test/priv_pkcs1.pem") as fp:
        private_key = fp.read()
    with open("test/pub_pkcs1.pem") as fp:
        public_key = fp.read()
    enc = AsymRsaEnc(public_key)
    dec = AsymRsaDec(private_key)

    ddd = enc.encode(b"123")
    print(ddd)
    print(dec.decode(ddd))
