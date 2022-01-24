#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author: AnhNT
    Company: MobioVN
    Date created: 26/02/2021

"""


from .config import SystemConfigKeys, UrlConfig, KafkaTopic
import datetime
import requests
from dateutil.parser import parse
import base64
from .mobio_admin_sdk import MobioAdminSDK

from mobio.libs.ciphers import MobioCrypt2
import json
from flask import request
from .aes_cipher import AESCipher
from mobio.libs.kafka_lib.helpers.confluent_producer_manager import (
    ConfluentProducerManager,
)
import os


def decrypt_data(enc_data):
    try:
        while len(enc_data) % 4 != 0:
            enc_data = enc_data + "="
        decrypt_resp = AESCipher().decrypt(enc_data)
        if decrypt_resp:
            return json.loads(decrypt_resp, encoding="utf-8")
        return None
    except Exception as e:
        print("admin_sdk::decrypt_data: Exception: %s" % e)
        return None


def get_merchant_auth(merchant_id):
    result = get_info_merchant_config(merchant_id)
    return {
        SystemConfigKeys.JWT_ALGORITHM: result.get("jwt_algorithm"),
        SystemConfigKeys.JWT_SECRET_KEY: result.get("jwt_secret_key"),
    }


@MobioAdminSDK.lru_cache.add()
def get_info_merchant_config(
    merchant_id,
    key=None,
    token_value=None,
    admin_version=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.ADMIN_CONFIG).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": SystemConfigKeys.MOBIO_TOKEN}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    data = result.get("data", {})
    if key:
        return data.get(key)
    return data


def check_basic_auth(partner_key):
    try:
        partner_info = get_partner_info_decrypt(partner_key, decrypt=True)
        if not partner_info and partner_info.get("data"):
            return False
        # partner_info = decrypt_data(partner_info_enc)
        expire_time = parse(partner_info.get("expired_time"))
        if expire_time.replace(tzinfo=None) < datetime.datetime.utcnow():
            print("admin_sdk::check_basic_auth: reach expire time: %s" % str(expire_time))
            return False
        return True
    except Exception as e:
        print("admin_sdk::check_basic_auth: error: %s" % e)
        return False

def get_partner_info_decrypt(partner_key, decrypt=False):
    partner_info_enc = get_partner_info_by_key(partner_key)
    if not decrypt:
        return partner_info_enc
    else:
        if not partner_info_enc or not isinstance(partner_info_enc, dict) or not partner_info_enc.get("data"):
            return partner_info_enc
        partner_info_dec = MobioCrypt2.d1(partner_info_enc.get("data"), enc="utf-8")
        return {"code": 200, "data": json.loads(partner_info_dec)}

@MobioAdminSDK.lru_cache.add()
def get_partner_info_by_key(partner_key):
    if not partner_key:
        return None
    adm_url = str(UrlConfig.PARTNER_INFO_CIPHER_ENCRYPT).format(
        host=MobioAdminSDK().admin_host,
        version=MobioAdminSDK().admin_version,
        partner_id=partner_key,
    )
    resp = requests.get(
        adm_url,
        headers=MobioAdminSDK().request_header,
        timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json()


def check_basic_auth_v2(partner_key):
    partner_info_enc = get_partner_info_by_key_v2(partner_key)
    if not partner_info_enc:
        return False
    try:
        # partner_info_dec = MobioCrypt2.d1(partner_info_enc, enc="utf-8")
        # partner_info = json.loads(partner_info_dec)
        partner_info = decrypt_data(partner_info_enc)
        expire_time = parse(partner_info.get("expired_time"))
        if expire_time.replace(tzinfo=None) < datetime.datetime.utcnow():
            print("admin_sdk::check_basic_auth: reach expire time: %s" % str(expire_time))
            return False
        return True
    except Exception as e:
        print("admin_sdk::check_basic_auth: error: %s" % e)
        return False


@MobioAdminSDK.lru_cache.add()
def get_partner_info_by_key_v2(partner_key):
    if not partner_key:
        return None
    adm_url = str(UrlConfig.PARTNER_INFO).format(
        host=MobioAdminSDK().admin_host,
        version=MobioAdminSDK().admin_version,
        partner_id=partner_key,
    )
    resp = requests.get(
        adm_url,
        headers=MobioAdminSDK().request_header,
        timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    status_code = resp.status_code
    if status_code == 200:
        result = resp.json()
        enc_data = result["data"]
        return enc_data
    else:
        print("admin_sdk::get_expire_time_by_key: error: status_code = %d" % status_code)
        return None


class Base64(object):
    @staticmethod
    def encode(data):
        try:
            byte_string = data.encode("utf-8")
            encoded_data = base64.b64encode(byte_string)
            return encoded_data.decode(encoding="UTF-8")
        except Exception as ex:
            print(ex)
            return ""

    @staticmethod
    def decode(encoded_data):
        try:
            if isinstance(encoded_data, bytes):
                encoded_data = encoded_data.decode("UTF-8")
            decoded_data = base64.urlsafe_b64decode(
                encoded_data + "=" * (-len(encoded_data) % 4)
            )
            return decoded_data.decode(encoding="UTF-8")
        except Exception as ex:
            print(ex)
            return encoded_data


@MobioAdminSDK.lru_cache.add()
def get_info_merchant_brand_sub_brand(
    merchant_id,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.MERCHANT_RELATED).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}

    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


@MobioAdminSDK.lru_cache.add()
def get_info_staff(
    merchant_id,
    account_id,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.STAFF_INFO).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
        account_id=account_id,
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


@MobioAdminSDK.lru_cache.add()
def get_list_info_staff(
    merchant_id,
    params=None,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.LIST_STAFF_INFO).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        params=params,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


@MobioAdminSDK.lru_cache.add()
def get_list_parent_merchant(
    merchant_id,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.MERCHANT_PARENT).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


@MobioAdminSDK.lru_cache.add()
def get_list_profile_group(
    merchant_id=None,
    params=None,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.LIST_PROFILE_GROUP).format(
        host=MobioAdminSDK().admin_host, version=api_version
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if merchant_id:
        request_header["X-Merchant-Id"] = merchant_id
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        params=params,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


@MobioAdminSDK.lru_cache.add()
def get_list_subbrands(
    params=None,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.LIST_SUBBRANDS_BY_MERCHANT).format(
        host=MobioAdminSDK().admin_host, version=api_version
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        params=params,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


@MobioAdminSDK.lru_cache.add()
def get_info_subbrand(
    subbrand_id=None,
    admin_version=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.GET_INFO_SUBBRAND).format(
        host=MobioAdminSDK().admin_host, version=api_version, subbrand_id=subbrand_id
    )
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}

    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    return result


def push_kafka_log_action_account(json_mess):
    if not json_mess:
        raise ValueError("data none")
    if not json_mess.get("account_id"):
        raise ValueError("account_id not found")
    if not json_mess.get("merchant_id"):
        raise ValueError("merchant_id not found")
    if not json_mess.get("created_time"):
        raise ValueError("created_time not found")
    if not json_mess.get("action_name_vi") and not json_mess.get("action_name_en"):
        raise ValueError("action_name_vi and action_name_en not found")
    if not json_mess.get("action_name_vi") and json_mess.get("action_name_en"):
        json_mess["action_name_vi"] = json_mess.get("action_name_en")
    if json_mess.get("action_name_vi") and not json_mess.get("action_name_en"):
        json_mess["action_name_en"] = json_mess.get("action_name_vi")
    json_mess["source"] = "admin_sdk"
    ConfluentProducerManager.send_message_to_topic(
        topic=KafkaTopic.LogActionAccount, data=json.dumps({"message": json_mess})
    )


@MobioAdminSDK.lru_cache.add()
def get_merchant_config_host(
    merchant_id,
    key_host=None,
    admin_version=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.GET_DETAIL_MERCHANT_CONFIG).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    request_header = {}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    param = {"fields": ",".join(["internal_host", "module_host", "public_host", "config_host"])}
    response = requests.get(
        adm_url,
        params=param,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    data = result.get("data", {}) if result and result.get("data", {}) else {}
    if key_host:
        return data.get(key_host)
    return data

@MobioAdminSDK.lru_cache.add()
def get_merchant_config_other(
    merchant_id,
    list_key=None,
    admin_version=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    if admin_version and admin_version in MobioAdminSDK.LIST_VERSION_VALID:
        api_version = admin_version
    adm_url = str(UrlConfig.GET_DETAIL_MERCHANT_CONFIG).format(
        host=MobioAdminSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    request_header = {}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    param = None
    if list_key and isinstance(list_key, list):
        param = {"fields": ",".join(list_key)}
    response = requests.get(
        adm_url,
        params=param,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    data = result.get("data", {}) if result and result.get("data", {}) else {}
    return data

@MobioAdminSDK.lru_cache.add()
def get_all_key_uri_from_merchant(
    merchant_id=None,
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    adm_url = str(UrlConfig.GET_SERVER_FROM_MERCHANT).format(
        host=MobioAdminSDK().admin_host, version=api_version
    )
    params = {
        "merchant_id": merchant_id,
    }
    # if key_uri_module:
    #     params["key_module"] = key_uri_module
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        params=params,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    if result and result.get("data"):
        return result.get("data")
    else:
        return None


@MobioAdminSDK.lru_cache.add()
def get_list_all_server_uri(
    token_value=None,
    request_timeout=MobioAdminSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
):
    api_version = MobioAdminSDK().admin_version
    adm_url = str(UrlConfig.GET_LIST_SERVER_FROM_MODULE).format(
        host=MobioAdminSDK().admin_host, version=api_version
    )
    params = {
    }
    if token_value:
        request_header = {"Authorization": token_value}
    else:
        request_header = {"Authorization": request.headers.get("Authorization")}
    if MobioAdminSDK().request_header:
        request_header.update(MobioAdminSDK().request_header)
    response = requests.get(
        adm_url,
        params=params,
        headers=request_header,
        timeout=request_timeout,
    )
    response.raise_for_status()
    result = response.json()
    if result and result.get("data"):
        return result.get("data")
    else:
        return None


def get_server_uri_from_merchant(merchant_id, key_module):
    server_id, db_uri = "", ""
    try:
        if SystemConfigKeys.vm_type:
            result = get_all_key_uri_from_merchant(
                merchant_id=merchant_id,
                token_value=SystemConfigKeys.MOBIO_TOKEN,
            )
            if result:
                server_id = result.get("server_id")
                db_uri = result.get(key_module)
    except Exception as er:
        err_msg = "admin_sdk::get_server_uri_from_merchant ERR: {}".format(er)
        print(err_msg)
    if not server_id or not db_uri:
        server_id = key_module
        db_uri = os.environ.get(key_module)
    return server_id, db_uri


def get_server_uri_default_from_module(key_module):
    server_id = key_module
    db_uri = os.environ.get(key_module)
    return server_id, db_uri
