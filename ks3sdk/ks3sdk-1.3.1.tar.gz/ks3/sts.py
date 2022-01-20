# coding:utf-8
import json

from ks3.exception import S3ResponseError
from ks3.http import make_request_v4

def assumeRole(access_key_id, access_key_secret, role_krn, role_session_name, duration_seconds=3600, policy=None):
    query_args = {
        'Action': 'AssumeRole',
        'Version': '2015-11-01'
    }
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    body = {
        "RoleKrn": role_krn, # "krn:ksc:iam::xxx:role/xxx", 角色id
        "RoleSessionName": role_session_name, # "KS3", 该次扮演的名称
        "DurationSeconds": duration_seconds # 持续有效时间，非必须参数，默认3600秒
    }
    if policy != None:
        body['Policy'] = json.dumps(policy)

    response = make_request_v4(access_key_id, access_key_secret, method='GET', service='sts', region='cn-beijing-6', headers=headers,
                                 query_args=query_args, body=json.dumps(body))
    body = response.read()
    if response.status != 200:
        raise S3ResponseError(response.status, response.reason, body)
    return json.loads(body)