#!usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'mayanqiong'


import asyncio
import json
import lzma

from tqsdk import TqChan
from tqsdk.connect import TqConnect
from tqsdk.utils import _generate_uuid


TestScriptChanMap = {}
TestScript = ""


def set_test_script(file_name):
    global TestScriptChanMap, TestScript
    TestScriptChanMap = {}
    TestScript = file_name


async def _script_runner(api, file_name):
    """只有一个 reader 读取日志文件，保证录多个连接的建立连接、收到数据包的顺序，在测试回放脚本和录制脚本时，时机完全一致的"""
    with lzma.open(file_name, "rt", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            if item["name"] != "TqApi.TqConnect":
                continue
            # 处理三种 msg
            # 收数据 - 比较用户发出的数据和脚本中完全一致
            # 发数据 - 用户发出的数据和脚本中一致
            # 连接建立 - 用户建立连接的时机
            if item["msg"] != "websocket send data" and item["msg"] != "websocket received data" and item["msg"] != "websocket connected":
                continue
            url = item["url"]
            account_id = item.get("account_id")
            TestScriptChanMap.setdefault(url, {}).setdefault(account_id, {
                "init_chan": TqChan(api),
            })
            try:
                await TestScriptChanMap[url][account_id]["init_chan"].recv()
            except asyncio.CancelledError:
                api._logger.error("script_runner wait init done", url, account_id)
                raise
            # 通过 account_id 取到这行日志对应的 send_chan / recv_chan
            send_chan = TestScriptChanMap[url][account_id]["send_chan"]
            recv_chan = TestScriptChanMap[url][account_id]["recv_chan"]
            if item["msg"] == "websocket send data":
                expected = json.loads(item['pack'])
                try:
                    pack = await send_chan.recv()
                except asyncio.CancelledError:
                    api._logger.error("script_runner wait send data", url=url, account_id=account_id, expected=expected)
                    raise
                try:
                    if expected['aid'] == 'req_login':
                        assert pack['user_name'] == expected['user_name']
                        assert pack['bid'] == expected['bid']
                        assert pack['password'] == expected['password']
                    elif expected['aid'] == 'ins_query':
                        assert pack["query_id"] == expected['query_id']
                    else:
                        assert pack == expected
                except:
                    api._logger.error("script_runner send data", url, account_id, expected=expected, actual=pack)
                    raise
            elif item["msg"] == "websocket received data":
                # 保持和实盘运行一致，等到 api 真正需要收取数据包时才会被调度
                await api._wait_until_idle()
                expected = json.loads(item['pack'])
                await recv_chan.send(expected)
            elif item["msg"] == "websocket connected":
                # 保持和实盘运行一致，等到 api 真正需要收取数据包时才会被调度
                await api._wait_until_idle()
                # 发送网络连接建立的通知
                notify_id = _generate_uuid()
                await recv_chan.send({
                    "aid": "rtn_data",
                    "data": [{
                        "notify": {
                            notify_id: {
                                "type": "MESSAGE",
                                "level": "INFO",
                                "code": 2019112901,
                                "content": "与 %s 的网络连接已建立" % url,
                                "url": url
                            }
                        }
                    }]
                })

async def _mock_run(self, api, url, send_chan, recv_chan):
    account_id = self._logger.extra.get('account_id', None)
    # 这个 api 实例，只有会创建一个 _script_runner task
    # 每个测试用例运行前会调用 set_test_script，保证每个测试用例运行时 TestScriptChanMap 对象置为空
    if not TestScriptChanMap:
        api.create_task(_script_runner(api, TestScript), _caller_api=True)
    TestScriptChanMap.setdefault(url, {}).setdefault(account_id, {
        "init_chan": TqChan(api),
    })
    # 将网络连接的 send_chan、 recv_chan 分别记录在对应的 account_id 下
    # 不同的 account_id 对应不同的交易连接，行情连接 account_id == None
    TestScriptChanMap[url][account_id]["send_chan"] = send_chan
    TestScriptChanMap[url][account_id]["recv_chan"] = recv_chan
    await TestScriptChanMap[url][account_id]["init_chan"].close()

TqConnect._run = _mock_run
