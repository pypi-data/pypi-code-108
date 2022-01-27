#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from src.rolling_king.jason.requests.http_sender_module import HttpSender
import json
import pytest


class TestMPlatform(object):

    def test_get(self):
        http_sender_obj = HttpSender("https://boe-pangle-ssr.bytedance.net")
        http_sender_obj.set_headers({"Cookie": "passport_csrf_token_default=7501cdcbfc561e1dffe8452164dece87; pangle-i18n=zh; Hm_lvt_ff76cafb7653fe92a16e2025d769a918=1612672717; ttwid=1|1Pu6X3dj5YcMDj9Dtss-tGhvumhWp9QZg2s4_utiIQ4|1612672716|18b21ed88c5818720d89aee191e66bd1638187844f611b0081a6a2388c5bc354; s_v_web_id=kkunp4qt_PTwUJMKm_Uonp_4Fwh_AsWK_zHI7O7fN80d7; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; passport_auth_status=f2c05d0bf656747c3d37303dc3e18bdc,; odin_tt=5d94aaa8493d549085bf91a5061f80e0ea261173c1d7750f9dd337506eac3514c2205482622ab8b69f957ece8ea74b55e0f1d34fe50e2fd1b6ba373004f76f20; sid_guard=09c5bfc37b0ecdacd699d86ddd66b828|1612861802|21600|Tue,+09-Feb-2021+15:10:02+GMT; uid_tt=9e04001ec1a1242ca4012de5252d12eb; uid_tt_ss=9e04001ec1a1242ca4012de5252d12eb; sid_tt=09c5bfc37b0ecdacd699d86ddd66b828; sessionid=09c5bfc37b0ecdacd699d86ddd66b828; sessionid_ss=09c5bfc37b0ecdacd699d86ddd66b828; Hm_lpvt_ff76cafb7653fe92a16e2025d769a918=1612861804; mhjseduw32ewkejf_gdald_sda7=P3nG6lT2_KmKQzKGgGf44J3rRfZFlrQne5aBB8N1VvJ2hNQBr_MNqmu3q0APHwel6wcSZ_Nj7ouasdtVAXk0FFGqoVN6YtBKm-5ksaDFdMOXYTIDDWlXD8UkP6y94ma-1uP_wEDvEHK4Lycz57eFFgb06B4ceIzJWthR0NzrL2g=; session=.eJw9jr0OgjAYRV_FfDNDqZSSJi4GBofiIhprDCltUVDQ8BO0hHeXGON0bs5y7ghSV0WdFhqY6_qEOiAvpu6-wiMEzUK1TZ52j5upgY2wyIABLyMkDuImdomNw3U183W0_C3CjT3aZIgtH7a79VWU-5Lj6BWX14IPqxVMDjybh-5VBwz_dwvshM8ONOYuO6PTvjXN9wFy4BeG3CMBpp5RLkFBRnBOJdKS-IqamRQrgvAyywOYPn-VQ2Y.YCJUoA.WRNs_NowrVpiR50sSuxR3_4F7W8; gftoken=MDljNWJmYzM3YnwxNjEyODYyNjI0MjZ8fDAGBgYGBgY; MONITOR_WEB_ID=45507"})
        input_param = {"AdUnitId": "1172",
                       "ExperimentGroupType": 1,
                       "Page": 1,
                       "StartDate": "2021-02-09",
                       "EndDate": "2021-02-09"}
        http_sender_obj.send_get_request_by_suburi("/union_pangle/api/mediation/waterfall/detail", input_param)
        result_str = http_sender_obj.get_response.text
        print("结果：", result_str)
        dict_val = json.loads(result_str)
        print(type(dict_val))
        print(json.dumps(dict_val, indent=2))


if __name__ == "__main__":
    pytest.main(["-s",  "test_m_project.py"])
