#!/usr/bin/env python
#  -*- coding: utf-8 -*-


import json
import lzma
import os
import socket
import threading
import asyncio
import urllib

from aiohttp import web

from tqsdk import TqAuth


origin_has_account = TqAuth._has_account


def mock_has_account(self, account):
    if self._user_name == "tianqin" and self._password == "tianqin":
        return True
    else:
        return origin_has_account(account)


origin_has_feature = TqAuth._has_feature


def mock_has_feature(self, feature):
    if self._user_name == "tianqin" and self._password == "tianqin":
        return True
    else:
        return origin_has_feature(feature)


TqAuth._has_account = mock_has_account
TqAuth._has_feature = mock_has_feature


class MockInsServer():
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.symbols_dir = os.path.join(os.path.dirname(__file__), 'symbols')
        self.stop_signal = self.loop.create_future()
        self.semaphore = threading.Semaphore(value=0)
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        self.semaphore.acquire()

    def close(self):
        self.loop.call_soon_threadsafe(lambda: self.stop_signal.set_result(0))
        self.thread.join()
        self.loop.close()

    async def handle(self, request):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "mock_files", request.url.name)
        if os.path.exists(file_path):
            with open(file_path, "rt", encoding="utf-8") as f:
                return web.json_response(json.loads(f.read()))
        else:
            file_path += ".lzma"
            with lzma.open(file_path, "rt", encoding="utf-8") as f:
                return web.json_response(json.loads(f.read()))

    async def auth_handle(self, request):
        """
        对于 mock auth 服务， 只有 auth="tianqin,tianqin" 是收费全功能用户，其他是免费用户
        """
        query_str = await request.text()
        query = urllib.parse.parse_qs(query_str)
        if query["username"][0] == "tianqin" and query["password"][0] == "tianqin":
            s = '{"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiI4NTMxZTY5Zi03OGExLTQwNzktOTNkNy1jOTVlNDQ1ZWFlMzUiLCJleHAiOjE2MDQ4ODc2MTMsIm5iZiI6MCwiaWF0IjoxNjA0MjgyODEzLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsInN1YiI6IjBkZWRkNTFhLTI4MjYtNDZkMC1hZjgyLTBlMjZmZmNiNTYyNSIsInR5cCI6IkJlYXJlciIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6IjVhNzNiY2JiLTg0MTUtNDYxOS05MzliLTBkNTI3ZGE3M2U5NCIsImFjciI6IjEiLCJzY29wZSI6ImF0dHJpYnV0ZXMtZ3JhbnQtdHEgcHJvZmlsZSB1c2VybmFtZSIsImdyYW50cyI6eyJmZWF0dXJlcyI6WyJvcHQiLCJzdXAiLCJtYyIsInNlYyIsImZ1dHIiLCJ0cV9kbCIsInRxX2J0IiwiY21iIiwibG10X2lkeCIsInRxX21hIiwiYWR2Il0sImV4cGlyeV9kYXRlIjoiMCIsImFjY291bnRzIjpbIjAwMDE5OSIsIjgzMDExMTE5IiwiMTIzNDU2IiwiMTcyMjg5IiwiOTAwODQzMjEiLCI5MDEwMTA4NyIsIjk5OTkiLCI5MDA5MjMwNyIsIjE0NzcxNiIsIjBkZWRkNTFhLTI4MjYtNDZkMC1hZjgyLTBlMjZmZmNiNTYyNSIsIjEwMzk4OCJdfSwic2V0bmFtZSI6dHJ1ZSwibmFtZSI6Ik5VTEwgTlVMTCIsInByZWZlcnJlZF91c2VybmFtZSI6Im1heWFucWlvbmcxIiwiaWQiOiIwZGVkZDUxYS0yODI2LTQ2ZDAtYWY4Mi0wZTI2ZmZjYjU2MjUiLCJnaXZlbl9uYW1lIjoiTlVMTCIsImZhbWlseV9uYW1lIjoiTlVMTCIsInVzZXJuYW1lIjoibWF5YW5xaW9uZzEifQ.en9vKhjS4FX1DG2r3sfA3I0a8NQsOrZl_dPqBSydw3SiEzwoN21T2FUfUz7BzJ1WXDIMauYWSvaLr0IVRSafC715B4gmQ_24iy7S2T7OD7MECsdnQq2jzynCEsIEe4jhfBtn5vOZeVV2q2woBmYFcpYbIQjr4F60o0I5vddd7lo1kFUfLi8AkPYRRUDZ0qG8dAYKIYvewq40OS_QbrHU4JJDkFIyFMqlCkhed2b0zZanaDILuvEc190WkFs8IuKeQklZ_ZcBDUVHDD3kgKk7yErxySnWIvc0PY9oSg0rEsXG_eAS0ksnBfYtnN_CFbOwM4S2xkpuZxlFzE-hEudezQ","expires_in":604800,"refresh_expires_in":2592000,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmZDNjMjQwYS00ODcyLTRiYTAtODNlZC04OGRjNWU4ZDE2ODAifQ.eyJqdGkiOiI5Y2Y0YjlhYS1lOTMxLTQ5MzEtYTc4Yi0yMjgwZjBkZGY2YzEiLCJleHAiOjE2MDY4NzQ4MTMsIm5iZiI6MCwiaWF0IjoxNjA0MjgyODEzLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsImF1ZCI6Imh0dHBzOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiMGRlZGQ1MWEtMjgyNi00NmQwLWFmODItMGUyNmZmY2I1NjI1IiwidHlwIjoiUmVmcmVzaCIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6IjVhNzNiY2JiLTg0MTUtNDYxOS05MzliLTBkNTI3ZGE3M2U5NCIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIn0.3sco_1DI4d0fbTgi5gi56uE6K_MKrWIk8ta9_bc2agM","token_type":"bearer","not-before-policy":0,"session_state":"5a73bcbb-8415-4619-939b-0d527da73e94","scope":"attributes-grant-tq profile username"}'
        elif query["username"][0] == "ringo" and query["password"][0] == "ringo":
            s = "{\"access_token\":\"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiI2NTFjNWJlNi04OTZkLTRjMWUtOGE4NS1hNWVhZmFiY2JiN2YiLCJleHAiOjE2MTk2NzMxODcsIm5iZiI6MCwiaWF0IjoxNjE5MDY4Mzg3LCJpc3MiOiJodHRwOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiMmFiN2QyZjQtN2NmMi00NjIyLTlkNzMtNDI0N2VmODNmNTE3IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoic2hpbm55X3RxIiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiYmZmMjBiN2EtM2QyNy00NjJhLTk4ZGYtODU4MjYxY2RkNGU4IiwiYWNyIjoiMSIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIiwiZ3JhbnRzIjp7ImZlYXR1cmVzIjpbImZ1dHIiLCJ0cV9kbCIsImxtdF9pZHgiLCJvcHQiLCJtYyIsImNtYiIsInRxX2N0cCIsInN1cCIsInRxX21hIiwiYWR2Iiwic2VjIiwidHFfYnQiXSwiZXhwaXJ5X2RhdGUiOiIwIiwiYWNjb3VudHMiOlsiNjg4MTcyOTAiLCIxNzIyODkiLCIxMDM5ODgiLCIyMDEzOTAxOCIsIjEwMzk4OCIsIjEyMzQ1NiIsIjkwMDg0MzIxIiwiOTAxMjA1NzA4IiwiNzAwMjEwMTIiLCI0MTAwODIwNiIsIjEyMzQ1NjciLCIxNzIyODkiLCIxMDAwMDA0MSIsIjE0NzcxNiIsIjMzMzM3NjcyIiwiOTAwOTk4OTQiLCIxMDAwIiwiOTAxMjA1MDc4IiwiOTAxMTAxMDg3IiwiMTIwOTk1IiwiMmFiN2QyZjQtN2NmMi00NjIyLTlkNzMtNDI0N2VmODNmNTE3IiwiMjAxMDM3OTEiLCI5MDA5OTg3NSIsIjgwMDEwMDg2IiwiMDAwMDAxIiwiOTAwODQzNDMiLCI5MDA5ODEzNyIsIjkwMTAxMDg3IiwiNjc3MTAwMzkwIl19LCJzZXRuYW1lIjp0cnVlLCJuYW1lIjoicmluZ28gbm9uZSIsInByZWZlcnJlZF91c2VybmFtZSI6InJpbmdvIiwiaWQiOiIyYWI3ZDJmNC03Y2YyLTQ2MjItOWQ3My00MjQ3ZWY4M2Y1MTciLCJnaXZlbl9uYW1lIjoicmluZ28iLCJmYW1pbHlfbmFtZSI6Im5vbmUiLCJ1c2VybmFtZSI6InJpbmdvIn0.YL1lW_Sds-vMThhBjWWzqNWqbBEg8fYJ2m3-EnqSfheS8kVgcaGvcXBW9QmBIBK3sC7hG6sTNSpYaZdKXrNAmFhVUbma4yN4mPUVh_mWGwPxjSEoxe0bmi6_P5ZOZpDrNJAmRZeMry59RHJtDKE6uzi66_gDQpXY7MQN8TRtVQaYjEmkf-W7hxWXSCGN2qVyEemt3IpyTm4E4qSWzicgmWPIzPsicXhuvS7CgCy4bIPBHFy5mvrBbnWUVd7QPrcidW8hU766zR9koBmVFTF_qbx8URk7JIbDEj7t9Ksz9HB1Cp83tjkaoZ-PBKXONPHM_IWyR4WWBHAfTuEq6WO2jg\",\"expires_in\":604800,\"refresh_expires_in\":2592000,\"refresh_token\":\"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmZDNjMjQwYS00ODcyLTRiYTAtODNlZC04OGRjNWU4ZDE2ODAifQ.eyJqdGkiOiIwZWNiZTM0MS01NzA3LTRlM2ItYWQzNy0xN2I0M2JmM2M4YTgiLCJleHAiOjE2MjE2NjAzODcsIm5iZiI6MCwiaWF0IjoxNjE5MDY4Mzg3LCJpc3MiOiJodHRwOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwiYXVkIjoiaHR0cDovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsInN1YiI6IjJhYjdkMmY0LTdjZjItNDYyMi05ZDczLTQyNDdlZjgzZjUxNyIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJzaGlubnlfdHEiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJiZmYyMGI3YS0zZDI3LTQ2MmEtOThkZi04NTgyNjFjZGQ0ZTgiLCJzY29wZSI6ImF0dHJpYnV0ZXMtZ3JhbnQtdHEgcHJvZmlsZSB1c2VybmFtZSJ9.ZjiDw5LIQu1GGX1afkairiTAi-c7UO5XPqbJLVQjXos\",\"token_type\":\"bearer\",\"not-before-policy\":1601371595,\"session_state\":\"bff20b7a-3d27-462a-98df-858261cdd4e8\",\"scope\":\"attributes-grant-tq profile username\"}"
        elif query["username"][0] == "ringo" and query["password"][0] == "ringo":
            s = "{\"access_token\":\"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiJjNmE0ZmFlNC00Y2EzLTRlMjUtYWI5Yi0wMjRjNmI2ODJjYmIiLCJleHAiOjE2MTk2ODA1NzUsIm5iZiI6MCwiaWF0IjoxNjE5MDc1Nzc1LCJpc3MiOiJodHRwOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiNGM1MDQ3YzAtNWYyYi00MmJiLWEzMTYtZjg2MTkzZjhhYjRmIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoic2hpbm55X3RxIiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiYTUzZGNhOGYtZThhNi00N2MxLWEwOWMtY2RiNGY3ZjBjMTZmIiwiYWNyIjoiMSIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIiwiZ3JhbnRzIjp7ImZlYXR1cmVzIjpbInNlYyIsIm1jIiwiY21iIiwidHFfbWEiLCJzdXAiLCJsbXRfaWR4IiwiZnV0ciIsInRxX2N0cCIsImFkdiIsIm9wdCIsInRxX2J0IiwidHFfZGwiXSwiZXhwaXJ5X2RhdGUiOiIyMDIwMDEwMTEyNTk1OSIsImFjY291bnRzIjpbIjY4ODE3MjkwIiwiODAwNzk5MzIiLCJjdXN0b21lcjg0NiIsIjkwMTIwNTcwOCIsIjkwMDgwMTMxMyIsIjcwMDIxMDEyIiwiNGM1MDQ3YzAtNWYyYi00MmJiLWEzMTYtZjg2MTkzZjhhYjRmIl19LCJzZXRuYW1lIjp0cnVlLCJtb2JpbGUiOiIxODM1MjUxMjgxNiIsIm1vYmlsZVZlcmlmaWVkIjoidHJ1ZSIsInByZWZlcnJlZF91c2VybmFtZSI6Imhvbmd5YW4iLCJpZCI6IjRjNTA0N2MwLTVmMmItNDJiYi1hMzE2LWY4NjE5M2Y4YWI0ZiIsInVzZXJuYW1lIjoiaG9uZ3lhbiJ9.iSgOI9pVQ7o8UJr7sy_1KuHnSiKKJAJeSzvqKsB7AF9aUYMGwd5LQSRXF1GulkZ3D4QWSB8EHUM2OS87zgoE5ytI3b-98Tpu7U5Q_IO4aYiNbnBLrQU4wL3Z-pm1c0p2CgYYbu8vDmkvEKQ_g0n6FBXo9bMzXuINyq8mYncP_-hyoIVQ3W1RgiLQA6JRkBzqS1V2j14gFoa9bmGiiLcL4ose-uibX6AAf7_36_sw1m59YQe_TvZbz8AVTYRsoaVO0BNxn6PFWyytMMInSFAs3I0c2cfyw76hny2-vgrCddx4Nk7RwWEF5LN-8m21FGVAiTQlzGjwWNIgu37kVubLjw\",\"expires_in\":604800,\"refresh_expires_in\":2592000,\"refresh_token\":\"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmZDNjMjQwYS00ODcyLTRiYTAtODNlZC04OGRjNWU4ZDE2ODAifQ.eyJqdGkiOiI3N2ZlYWM5Yi1kMGI1LTRhMTktYTJkMy01ODVkM2M4MWE0MTUiLCJleHAiOjE2MjE2Njc3NzUsIm5iZiI6MCwiaWF0IjoxNjE5MDc1Nzc1LCJpc3MiOiJodHRwOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwiYXVkIjoiaHR0cDovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsInN1YiI6IjRjNTA0N2MwLTVmMmItNDJiYi1hMzE2LWY4NjE5M2Y4YWI0ZiIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJzaGlubnlfdHEiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJhNTNkY2E4Zi1lOGE2LTQ3YzEtYTA5Yy1jZGI0ZjdmMGMxNmYiLCJzY29wZSI6ImF0dHJpYnV0ZXMtZ3JhbnQtdHEgcHJvZmlsZSB1c2VybmFtZSJ9.T2javLs7i3I22sLvkDNkyea60fyhv6eTXfwPSwH1TQk\",\"token_type\":\"bearer\",\"not-before-policy\":1601347321,\"session_state\":\"a53dca8f-e8a6-47c1-a09c-cdb4f7f0c16f\",\"scope\":\"attributes-grant-tq profile username\"}"
        else:
            s = '{"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiI2YTFhZmE0MC1lMDczLTRhMmQtODljYy04MDFmZmRkMjgxM2YiLCJleHAiOjE2Mjk0MjQ3NDAsIm5iZiI6MCwiaWF0IjoxNTk3ODg4NzQwLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsInN1YiI6IjcwZTQ0YWU1LTY0YjgtNDdlMC1iYjU0LWE1ZWVkY2RjZDM3YyIsInR5cCI6IkJlYXJlciIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFmOWNjZDNhLTI1MDktNGUzOC04MTBiLThjNjE4YWQzNmFjYiIsImFjciI6IjEiLCJzY29wZSI6ImF0dHJpYnV0ZXMtZ3JhbnQtdHEgcHJvZmlsZSB1c2VybmFtZSIsImdyYW50cyI6eyJmZWF0dXJlcyI6WyJmdXRyIiwibG10X2lkeCJdLCJleHBpcnlfZGF0ZSI6IjAiLCJhY2NvdW50cyI6WyI3MGU0NGFlNS02NGI4LTQ3ZTAtYmI1NC1hNWVlZGNkY2QzN2MiLCIxMDM5ODgiLCIqIl19LCJzZXRuYW1lIjp0cnVlLCJuYW1lIjoieWFucWlvbmcgTWEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJlbGl6YWJldGhtYSIsImlkIjoiNzBlNDRhZTUtNjRiOC00N2UwLWJiNTQtYTVlZWRjZGNkMzdjIiwiZ2l2ZW5fbmFtZSI6InlhbnFpb25nIiwiZmFtaWx5X25hbWUiOiJNYSIsInVzZXJuYW1lIjoiZWxpemFiZXRobWEifQ.en9vKhjS4FX1DG2r3sfA3I0a8NQsOrZl_dPqBSydw3SiEzwoN21T2FUfUz7BzJ1WXDIMauYWSvaLr0IVRSafC715B4gmQ_24iy7S2T7OD7MECsdnQq2jzynCEsIEe4jhfBtn5vOZeVV2q2woBmYFcpYbIQjr4F60o0I5vddd7lo1kFUfLi8AkPYRRUDZ0qG8dAYKIYvewq40OS_QbrHU4JJDkFIyFMqlCkhed2b0zZanaDILuvEc190WkFs8IuKeQklZ_ZcBDUVHDD3kgKk7yErxySnWIvc0PY9oSg0rEsXG_eAS0ksnBfYtnN_CFbOwM4S2xkpuZxlFzE-hEudezQ","expires_in":31536000,"refresh_expires_in":7776000,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmZDNjMjQwYS00ODcyLTRiYTAtODNlZC04OGRjNWU4ZDE2ODAifQ.eyJqdGkiOiIxNzMyYmU1ZS02ZmY2LTQ0NGQtOGIzMC0xNzFlODhmNTQyYjUiLCJleHAiOjE2MDU2NjQ3NDAsIm5iZiI6MCwiaWF0IjoxNTk3ODg4NzQwLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsImF1ZCI6Imh0dHBzOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiNzBlNDRhZTUtNjRiOC00N2UwLWJiNTQtYTVlZWRjZGNkMzdjIiwidHlwIjoiUmVmcmVzaCIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFmOWNjZDNhLTI1MDktNGUzOC04MTBiLThjNjE4YWQzNmFjYiIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIn0.Zuq-TsXC0D_rtk07JR1Dhd_iYNLxd5xg1s4jSrEZLBw","token_type":"bearer","not-before-policy":0,"session_state":"af9ccd3a-2509-4e38-810b-8c618ad36acb","scope":"attributes-grant-tq profile username"}'
        return web.json_response(text=s)

    async def task_serve(self):
        try:
            app = web.Application()
            app.add_routes([web.post('/auth/realms/shinnytech/protocol/openid-connect/token', self.auth_handle)])
            app.add_routes([web.get('/{tail:.*}', self.handle)])
            runner = web.AppRunner(app)
            await runner.setup()
            server_socket = socket.socket()
            server_socket.bind(('127.0.0.1', 0))
            site = web.SockSite(runner, server_socket)
            await site.start()
            self.port = server_socket.getsockname()[1]
            self.semaphore.release()
            await self.stop_signal
        finally:
            await runner.shutdown()
            await runner.cleanup()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.task_serve())
