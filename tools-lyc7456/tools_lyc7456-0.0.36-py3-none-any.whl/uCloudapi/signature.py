import operator
from ucloud.core import auth

# Write by lyc at 2020-4-29
# [UCloud api签名算法](https://docs.ucloud.cn/api/summary/signature)

def verify_ac(public_key, private_key, parm):
    '''
    计算签名 signature
    :param public_key: 公钥
    :param private_key: 私钥
    :param parm: 按照key升序排列后的请求参数字典
    :return: signature 签名值
    '''
    # 升序排列dict
    parm = dict(sorted(parm.items(), key=operator.itemgetter(0), reverse=False))
    cred = auth.Credential(
        "%s"%public_key,
        "%s"%private_key,
    )
    return cred.verify_ac(parm)






