from fastapi import FastAPI
import typing
import uvicorn
import json


try:
    from . import models
    from .base import Core, CatchErr
except:
    import models
    from base import Core, CatchErr


core = Core()


app = FastAPI(title="TANZE", version="0.1.0", description="自写sdk, 增加 test接口可以测试连接器，连接器并不为单例的，第一执行的组件")

# web 调用　自写方法　关键　
plugins = None


class Server(object):


    def __init__(self, plus):

        global plugins
        plugins = plus

    @staticmethod
    @app.post("/triggers/{trigger_name}")
    def triggers(trigger_name: str, plugin_stdin: typing.Optional[models.PluginStdin]):

        # 外部类
        trigger_model = plugins.triggers[trigger_name]


        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        inp = core.extract_pointer(stdin_body, "/input")
        connect_data = core.extract_pointer(stdin_body, "/connection")
        dispatcher_url = core.extract_pointer(stdin_body, "/dispatcher/url")


        # 执行　外部run 相关操作
        output = trigger_model._run(inp, connect_data, dispatcher_url)

        return output


    @staticmethod
    @app.post("/triggers/{trigger_name}/test")
    def trigger_test(trigger_name: str, plugin_stdin: typing.Optional[models.PluginStdin] = None):
        # 外部类
        trigger_model = plugins.triggers[trigger_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        connect_data = core.extract_pointer(stdin_body, "/connection")

        output = trigger_model.test(connect_data)

        return output


    @staticmethod
    @app.post("/actions/{action_name}")
    def actions(action_name, plugin_stdin: typing.Optional[models.PluginStdin] = None):


        # 外部类
        action_model = plugins.actions[action_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        inp = core.extract_pointer(stdin_body, "/input")
        connect_data = core.extract_pointer(stdin_body, "/connection")

        # 执行　外部run 相关操作
        action_model.connection(connect_data)
        output = action_model._run(inp, connect_data)

        return output


    @staticmethod
    @app.post("/actions/{action_name}/test")
    def actions_test(action_name: str, plugin_stdin: typing.Optional[models.PluginStdin] = None):
        # 外部类
        action_model = plugins.actions[action_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        connect_data = core.extract_pointer(stdin_body, "/connection")

        output = action_model.test(connect_data)

        return output

    @staticmethod
    @app.post("/indicator_receivers/{indicator_receiver_name}")
    def indicator_receivers(indicator_receiver_name: str, plugin_stdin: typing.Optional[models.PluginStdin]):
        # 外部类
        indicator_receiver_model = plugins.indicator_receivers[indicator_receiver_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        inp = core.extract_pointer(stdin_body, "/input")
        connect_data = core.extract_pointer(stdin_body, "/connection")
        dispatcher_url = core.extract_pointer(stdin_body, "/dispatcher/url")

        # 执行　外部run 相关操作
        output = indicator_receiver_model._run(inp, connect_data, dispatcher_url)

        return output

    @staticmethod
    @app.post("/indicator_receivers/{indicator_receiver_name}/test")
    def indicator_receivers_test(indicator_receiver_name: str, plugin_stdin: typing.Optional[models.PluginStdin] = None):
        # 外部类
        indicator_receiver_model = plugins.indicator_receivers[indicator_receiver_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        connect_data = core.extract_pointer(stdin_body, "/connection")

        output = indicator_receiver_model.test(connect_data)

        return output
    
    
    @staticmethod
    @app.post("/alarm_receivers/{alarm_receiver_name}")
    def alarm_receivers(alarm_receiver_name: str, plugin_stdin: typing.Optional[models.PluginStdin]):
        # 外部类
        alarm_receiver_model = plugins.alarm_receivers[alarm_receiver_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        inp = core.extract_pointer(stdin_body, "/input")
        connect_data = core.extract_pointer(stdin_body, "/connection")
        dispatcher_url = core.extract_pointer(stdin_body, "/dispatcher/url")

        # 执行　外部run 相关操作
        output = alarm_receiver_model._run(inp, connect_data, dispatcher_url)

        return output

    @staticmethod
    @app.post("/alarm_receivers/{alarm_receiver_name}/test")
    def alarm_receivers_test(alarm_receiver_name: str, plugin_stdin: typing.Optional[models.PluginStdin] = None):
        # 外部类
        alarm_receiver_model = plugins.alarm_receivers[alarm_receiver_name]

        # 取出body
        plugin_stdin = json.dumps(plugin_stdin.dict())
        stdin_body = core.parse_stdin(plugin_stdin)

        # 获取input
        connect_data = core.extract_pointer(stdin_body, "/connection")

        output = alarm_receiver_model.test(connect_data)

        return output

    

    def runserver(self):
        uvicorn.run(app, host="0.0.0.0", port=10001)

