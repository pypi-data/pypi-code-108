from mobio.libs.Singleton import Singleton
from mobio.libs.caching import LruCache
from .config import StoreCacheType, Cache, SystemConfigKeys
from .mobio_authorization import MobioAuthorization
from .http_jwt_auth import HttpJwtAuth
# from mobio.libs.ciphers import MobioCrypt2
import redis
from mobio.sdks.license import MobioLicenseSDK
from .aes_cipher import CryptUtil


def sdk_pre_check(func):
    def decorated_function(*args, **kwargs):
        if not MobioAdminSDK().admin_host:
            raise ValueError("admin_host None")
        if not MobioAdminSDK().lru_cache:
            raise ValueError("redis_uri None")
        if not MobioAdminSDK().module_encrypt:
            raise ValueError("module_encrypt None")
        if not MobioAdminSDK().module_use:
            raise ValueError("module_use None")
        if MobioAdminSDK().admin_version not in MobioAdminSDK.LIST_VERSION_VALID:
            raise ValueError("admin_version invalid")
        # if not MobioAdminSDK().module_valid:
        #     raise ValueError("module invalid")
        if SystemConfigKeys.vm_type and not CryptUtil.license_server_valid():
            raise ValueError("license server invalid")
        return func(*args, **kwargs)

    return decorated_function


@Singleton
class MobioAdminSDK(object):
    lru_cache = None
    DEFAULT_REQUEST_TIMEOUT_SECONDS = 15
    LIST_VERSION_VALID = ["v1.0", "api/v2.0", "api/v2.1"]

    def __init__(self):
        self.admin_host = ""
        self.admin_version = MobioAdminSDK.LIST_VERSION_VALID[-1]
        self.module_encrypt = ""
        self.module_use = ""
        self.request_header = None
        self.module_valid = False
        self.redis_uri = None

    @property
    def p_module_valid(self):
        return self.module_valid

    def config(
        self,
        admin_host=None,
        redis_uri=None,
        module_use=None,
        module_encrypt=None,
        api_admin_version=None,
    ):
        self.admin_host = admin_host
        self.module_encrypt = module_encrypt
        self.module_use = module_use
        if api_admin_version:
            self.admin_version = api_admin_version
        if module_use:
            self.request_header = {"X-Module-Request": module_use, "X-Mobio-SDK": "ADMIN"}
        # if module_use and module_encrypt:
        #     # if module_use == MobioCrypt2.d1(module_encrypt, enc="utf-8"):
        #     #     self.module_valid = True
        #     # else:
        #     #     self.module_valid = False
        #     self.module_valid = True


        if redis_uri:
            self.redis_uri = redis_uri
            MobioAdminSDK.lru_cache = LruCache(
                store_type=StoreCacheType.REDIS,
                cache_prefix=Cache.PREFIX_KEY,
                redis_uri=redis_uri,
            )

        MobioLicenseSDK().config(
            admin_host=admin_host,
            redis_uri=redis_uri,
            module_use=module_use,
            module_encrypt=module_encrypt,
            license_key=SystemConfigKeys.LICENSE_KEY,
        )

    @staticmethod
    @sdk_pre_check
    def create_mobio_verify_token():
        MobioAuthorization().local_redis = redis.from_url(MobioAdminSDK().redis_uri)
        return HttpJwtAuth(MobioAuthorization())

    @staticmethod
    @sdk_pre_check
    def get_value_from_token(key, access_token=None):
        if access_token:
            return MobioAuthorization().get(access_token, key)
        else:
            return MobioAuthorization().get_jwt_value(key=key)

    @staticmethod
    @sdk_pre_check
    def request_get_info_merchant_config(
        merchant_id,
        key=None,
        token_value=None,
        admin_version=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_info_merchant_config

        return get_info_merchant_config(
            merchant_id,
            key=key,
            token_value=token_value,
            admin_version=admin_version,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_merchant_config_host(
            merchant_id,
            key=None,
            admin_version=None,
            request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_merchant_config_host

        return get_merchant_config_host(
            merchant_id,
            key_host=key,
            admin_version=admin_version,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_check_merchant_is_brand(
        merchant_id,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_info_merchant_brand_sub_brand

        return get_info_merchant_brand_sub_brand(
            merchant_id,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_info_staff(
        merchant_id,
        account_id,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_info_staff

        return get_info_staff(
            merchant_id,
            account_id,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_list_info_staff(
        merchant_id,
        params=None,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_list_info_staff

        return get_list_info_staff(
            merchant_id,
            params=params,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_list_parent_merchant(
        merchant_id,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_list_parent_merchant

        return get_list_parent_merchant(
            merchant_id,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_list_profile_group(
        merchant_id=None,
        params=None,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_list_profile_group

        return get_list_profile_group(
            merchant_id=merchant_id,
            params=params,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_list_sub_brand(
        params=None,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_list_subbrands

        return get_list_subbrands(
            params=params,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_info_sub_brand(
        subbrand_id=None,
        admin_version=None,
        token_value=None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_info_subbrand

        return get_info_subbrand(
            subbrand_id=subbrand_id,
            admin_version=admin_version,
            token_value=token_value,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def admin_save_log_action_account(json_mess):
        from .utils import push_kafka_log_action_account

        return push_kafka_log_action_account(json_mess)

    @staticmethod
    @sdk_pre_check
    def request_get_merchant_config_other(
            merchant_id=None,
            list_key=None,
            admin_version=None,
            request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_merchant_config_other

        return get_merchant_config_other(
            merchant_id,
            list_key=list_key,
            admin_version=admin_version,
            request_timeout=request_timeout,
        )

    @staticmethod
    @sdk_pre_check
    def request_get_server_database_from_merchant(
            merchant_id=None,
            key_uri_module=None,
            token_value=None,
            request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_all_key_uri_from_merchant

        result = get_all_key_uri_from_merchant(
            merchant_id=merchant_id,
            token_value=token_value,
            request_timeout=request_timeout,
        )
        if result and key_uri_module:
            return {
                "server_id": result.get("server_id"),
                "server_name": result.get("server_name"),
                key_uri_module: result.get(key_uri_module)
            }
        return result

    @staticmethod
    @sdk_pre_check
    def request_get_list_server_database(
            key_uri_module=None,
            token_value=None,
            request_timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ):
        from .utils import get_list_all_server_uri

        result = get_list_all_server_uri(
            token_value=token_value,
            request_timeout=request_timeout,
        )
        if result and key_uri_module:
            list_server = []
            for server in result:
                list_server.append({
                    "server_id": server.get("server_id"),
                    "server_name": server.get("server_name"),
                    key_uri_module: server.get(key_uri_module)
                })
            return list_server
        return result

    @staticmethod
    @sdk_pre_check
    def request_get_partner_info(
            partner_key=None,
            decrypt_data=False,
    ):
        from .utils import get_partner_info_decrypt
        return get_partner_info_decrypt(partner_key=partner_key, decrypt=decrypt_data)
