from tcell_agent.rust.models.appfirewall_request_response import MAX_COOKIE_LENGTH
from tcell_agent.rust.models.utils import convert_post_params, convert_multidict_params, \
    convert_single_dict_params
from tcell_agent.utils.strings import ensure_str_or_unicode


class PatchesRequest(dict):
    def __init__(self, appsensor_meta):
        dict.__init__(self)
        # todo: cache these params if/when Patches requests converts them so they're not double converted.  sep. PR
        post_params_list = convert_post_params(appsensor_meta.post_dict, appsensor_meta.files_dict,
                                               appsensor_meta.encoding)

        self["full_uri"] = appsensor_meta.location
        self["method"] = appsensor_meta.method
        self["path"] = appsensor_meta.path
        self["remote_address"] = appsensor_meta.remote_address
        self["request_bytes_length"] = appsensor_meta.request_content_bytes_len
        # todo: cache these params if/when Patches requests converts them so they're not double converted.  sep. PR
        self["query_params"] = convert_multidict_params(appsensor_meta.get_dict, appsensor_meta.encoding)
        self["post_params"] = post_params_list
        self["headers"] = convert_multidict_params(appsensor_meta.headers_dict, appsensor_meta.encoding)
        self["cookies"] = convert_single_dict_params(appsensor_meta.cookie_dict, MAX_COOKIE_LENGTH)
        self["content_type"] = appsensor_meta.content_type
        self["request_body"] = ensure_str_or_unicode(appsensor_meta.encoding, appsensor_meta.request_body)
        self["reverse_proxy_header_value"] = appsensor_meta.reverse_proxy_header_value


class PatchesQuickCheck(dict):
    def __init__(self, appsensor_meta):
        dict.__init__(self)
        self["reverse_proxy_header_value"] = appsensor_meta.reverse_proxy_header_value
        self["method"] = appsensor_meta.method
        self["path"] = appsensor_meta.path
        self["full_uri"] = appsensor_meta.location
        self["request_bytes_length"] = appsensor_meta.request_content_bytes_len

        if self["reverse_proxy_header_value"] is None:
            self["client_ip_override"] = appsensor_meta.remote_address
