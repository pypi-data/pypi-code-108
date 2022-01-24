#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author: AnhNT
    Company: MobioVN
    Date created: 26/02/2021

"""
from .config import SystemConfigKeys
from .http_jwt_auth import ProjectAuthorization, TYPICALLY
from flask import json, request
from jose import jwt
from mobio.libs.Singleton import Singleton
from mobio.sdks.license import MobioLicenseSDK
from .date_utils import *


@Singleton
class MobioAuthorization(ProjectAuthorization):
    def __init__(self):
        self.key = None
        self.algorithm = None
        self.options = {
            "verify_signature": True,
            "verify_aud": False,
            "verify_iat": False,
            "verify_exp": True,
            "verify_nbf": False,
            "verify_iss": False,
            "verify_sub": False,
            "verify_jti": False,
        }
        self.local_redis = None

    @staticmethod
    def __merchant_id__(jwt_token=None):
        merchant_id = None
        if jwt_token:
            try:
                from .utils import Base64

                b_json = json.loads(Base64.decode(jwt_token.split(".")[1]))
                merchant_id = b_json.get("merchant_id", None)
            except Exception as e:
                print("admin_sdk:: __merchant_id__ error: {}".format(e))
                merchant_id = None

        if not merchant_id:
            merchant_id = request.headers.get(SystemConfigKeys.X_MERCHANT_ID, None)  # from Mobile
        return merchant_id

    @staticmethod
    def get_auth_info(merchant_id):
        from .utils import get_merchant_auth

        auth_info = get_merchant_auth(merchant_id)
        return (
            auth_info[SystemConfigKeys.JWT_SECRET_KEY],
            auth_info[SystemConfigKeys.JWT_ALGORITHM],
        )

    @staticmethod
    def get_jwt_info():
        return MobioAuthorization.get_auth_info(MobioAuthorization.__merchant_id__())

    def get(self, token, field_name):
        """
        lấy thông tin theo tên trường từ Json Web Token
        :param token:
        :param field_name:
        :return:
        """
        try:
            merchant_id = MobioAuthorization.__merchant_id__(token)
            self.key, self.algorithm = MobioAuthorization.get_auth_info(merchant_id)
        except Exception as e:
            self.key = None
            self.algorithm = None
            raise e

        body = self._decode(token)
        if body is None:
            return None
        return body.get(field_name, None)

    def _encode(self, body):
        try:
            return jwt.encode(body, self.key, self.algorithm)
        except Exception as e:
            print("admin_sdk::can not encode token: %s" % e)
            return None

    def _decode(self, body):
        try:
            return jwt.decode(body, self.key, self.algorithm, self.options)
        except Exception as e:
            print("admin_sdk::can not decode token: %s" % e)
            return None

    def is_permitted(self, jwt_token, typically, method):
        """
        hàm kiểm tra method có được phân quyền hay không
        :param jwt_token:
        :param typically:
        :param method:
        :return:
        """
        return True

    def verify_token(self, jwt_token, typically):
        """
        nếu là module có chức năng au then thì kiem tra trong redis
        nếu là module khác thì gọi moddule authen để verify token
        :param typically:
        :param jwt_token:
        :return: trả về token nếu hợp lệ
        """
        try:
            # if MobioAuthorization.license_merchant_expire():
            #     return None

            if typically == TYPICALLY.BEARER or typically == TYPICALLY.DIGEST:
                is_staff = self.get(jwt_token, "is_mobio") is not None
                if is_staff and typically != TYPICALLY.BEARER:
                    raise ValueError(
                        "typically invalidated, this must is %s" % TYPICALLY.BEARER
                    )
                if (not is_staff) and typically != TYPICALLY.DIGEST:
                    raise ValueError(
                        "typically invalidated, this must is %s" % TYPICALLY.DIGEST
                    )
                arr_token = jwt_token.split(".")
                # kiểm tra token trong REDIS
                verify_token = arr_token[2]
                value = self.local_redis.get(verify_token)
                return jwt_token if value is not None else None

            elif typically == TYPICALLY.BASIC:
                from .utils import check_basic_auth_v2

                return jwt_token if check_basic_auth_v2(jwt_token) else None

        except Exception as e:
            print("admin_sdk::MobioAuthorization::verify_token: ERROR: %s" % e)
            return None
        return None
    
    def get_jwt_value(self, key):
        try:
            auth_type, token = request.headers["Authorization"].split(None, 1)
            return self.get(token, key)
        except Exception:
            return None

    @staticmethod
    def license_merchant_expire():
        from .utils import get_list_parent_merchant
        merchant_expire = True
        try:
            x_merchant_id = request.headers.get(SystemConfigKeys.X_MERCHANT_ID)
            if not x_merchant_id:
                print("admin_sdk::check_time_merchant_expire X-Merchant-ID not found")
            else:
                data_parent = get_list_parent_merchant(merchant_id=x_merchant_id,
                                                       token_value=SystemConfigKeys.MOBIO_TOKEN)
                if data_parent and data_parent.get("data") and len(data_parent.get("data")) > 0:
                    root_merchant_id = data_parent.get("data")[0].get("root_merchant_id")
                    if root_merchant_id:
                        merchant_expire = MobioLicenseSDK().merchant_has_expired(
                            root_merchant_id
                        )
                    else:
                        print("admin_sdk::check_time_merchant_expire root_merchant_id not found")
                else:
                    print("admin_sdk::check_time_merchant_expire parent merchant not found")

        except Exception as e:
            print("admin_sdk::check_time_merchant_expire: ERROR: %s" % e)
        return merchant_expire

