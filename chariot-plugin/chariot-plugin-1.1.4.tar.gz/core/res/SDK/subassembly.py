import requests
from typing import Optional
import sys
from pydantic import BaseModel, ValidationError

try:
    from .base import Core, CatchErr
except:
    from base import Core, CatchErr


"""
插件各组件基类
"""


class Actions(object):
    # 类变量　格式化输出
    format_output = {
        "type": "trigger_event",
        "version": "v1",
        "body": {
            "meta": {},
            "output": None,
            "status": "ok",
            "log": "succ",
        }
    }

    log_out = Core().print_to_stdout
    log_err = Core().print_to_stderr

    def __init__(self):

        # action name 按规范应小写且用下划线隔开单词
        self.name = ""

        # 入参　校验类
        self.inputModel = None

        # 出参　校验类
        self.outputModel = None

        # 连接器　校验类
        self.connModel = None





    def connection(self, data: Optional[dict] = None):

        ...


    def run(self, params):
        ...

    @CatchErr.print_err_stack
    def test(self, connect):
        output = self.format_output

        try:
            self.connection(connect)
            output['body']["log"] = f"{self.name} 连接器测试无异常"
        except Exception as e:
            print(f"连接器　测试失败 - {str(e)}", file=sys.stderr)
            output['body']["log"] = f"{self.name} 连接器　测试异常 - {str(e)}"
        finally:
            self.log_out(output)
            return output

    @CatchErr.print_err_stack
    def _run(self, inp, connect):
        """
        私有函数，一切从我运行
        """

        core = Core()

        # 入参验证
        core.check_data(inp, self.inputModel)
        core.check_data(connect, self.connModel)

        # 运行自写　run
        self.connection(connect)
        data = self.run(inp)


        # 出参验证
        core.check_data(data, self.outputModel)

        # 补全output
        output = core.complete_output(data, "succ")

        # 输出到 stdout
        self.log_out(output)

        return output


class Triggers(object):
    # 类变量　格式化输出
    format_output = {
        "type": "trigger_event",
        "version": "v1",
        "body": {
            "meta": {},
            "output": None,
            "status": "ok",
            "log": "succ",
        }
    }
    log_out = Core().print_to_stdout
    log_err = Core().print_to_stderr

    def __init__(self):
        # action name 按规范应小写且用下划线隔开单词
        self.name = ""

        # 发送到
        self.dispatcher_url = ""

        # 入参　校验类
        self.inputModel = None

        # 出参　校验类
        self.outputModel = None

        # 类型
        self.connModel = None



    def connection(self, data: Optional[dict] = None):

        ...

    def run(self, params):
        ...

    @CatchErr.print_err_stack
    def test(self, connect):

        output = self.format_output

        try:
            self.connection(connect)
            output['body']["log"] = f"{self.name} 连接器测试无异常"
        except Exception as e:
            print(f"连接器　测试失败 - {str(e)}", file=sys.stderr)
            output['body']["log"] = f"{self.name} 连接器　测试异常 - {str(e)}"
        finally:
            self.log_out(output)
            return output

    @CatchErr.print_err_stack
    def _run(self, inp, connect, dispatcher_url):
        """
        私有函数，一切从我运行
        """

        self.dispatcher_url = dispatcher_url

        core = Core()

        # 入参验证
        core.check_data(inp, self.inputModel)
        core.check_data(connect, self.connModel)

        # 运行自写　run
        self.connection(connect)
        self.run(inp)

        output = self.format_output
        output["body"]["log"] = f"{self.name} succ"

        self.log_out(output)
        return output

    @CatchErr.print_err_stack
    def send(self, data: dict = {}) -> None:
        core = Core()

        core.check_data(data, self.outputModel)
        self.log_out(data)

        resp = requests.post(self.dispatcher_url, json=data)


class IndicatorReceivers(object):
    # 类变量　格式化输出
    format_output = {
        "type": "indicator_receiver_event",
        "version": "v1",
        "body": {
            "meta": {},
            "output": None,
            "status": "ok",
            "log": "succ",
        }
    }
    log_out = Core().print_to_stdout
    log_err = Core().print_to_stderr

    def __init__(self):
        # action name 按规范应小写且用下划线隔开单词
        self.name = ""

        # 发送到
        self.dispatcher_url = ""

        # 入参　校验类
        self.inputModel = None

        # 出参　校验类
        self.outputModel = None

        # 类型
        self.connModel = None



    def connection(self, data: Optional[dict] = None):

        ...

    def run(self, params):
        ...

    @CatchErr.print_err_stack
    def test(self, connect):

        output = self.format_output

        try:
            self.connection(connect)
            output['body']["log"] = f"{self.name} 连接器测试无异常"
        except Exception as e:
            print(f"连接器　测试失败 - {str(e)}", file=sys.stderr)
            output['body']["log"] = f"{self.name} 连接器　测试异常 - {str(e)}"
        finally:
            self.log_out(output)
            return output

    @CatchErr.print_err_stack
    def _run(self, inp, connect, dispatcher_url):
        """
        私有函数，一切从我运行
        """

        self.dispatcher_url = dispatcher_url

        core = Core()

        # 入参验证
        core.check_data(inp, self.inputModel)
        core.check_data(connect, self.connModel)

        # 运行自写　run
        self.connection(connect)
        self.run(inp)

        output = self.format_output
        output["body"]["log"] = f"{self.name} succ"

        self.log_out(output)
        return output

    @CatchErr.print_err_stack
    def send(self, data: dict = {}) -> None:
        core = Core()

        core.check_data(data, self.outputModel)
        self.log_out(data)

        resp = requests.post(self.dispatcher_url, json=data)

        self.log_out(f"[Response {resp.status_code}] {resp.text}")


class AlarmReceivers(object):
    # 类变量　格式化输出
    format_output = {
        "type": "alarm_receiver_event",
        "version": "v1",
        "body": {
            "meta": {},
            "output": None,
            "status": "ok",
            "log": "succ",
        }
    }
    log_out = Core().print_to_stdout
    log_err = Core().print_to_stderr

    def __init__(self):
        # action name 按规范应小写且用下划线隔开单词
        self.name = ""

        # 发送到
        self.dispatcher_url = ""

        # 入参　校验类
        self.inputModel = None

        # 出参　校验类
        self.outputModel = None

        # 类型
        self.connModel = None



    def connection(self, data: Optional[dict] = None):

        ...

    def run(self, params):
        ...

    @CatchErr.print_err_stack
    def test(self, connect):

        output = self.format_output

        try:
            self.connection(connect)
            output['body']["log"] = f"{self.name} 连接器测试无异常"
        except Exception as e:
            print(f"连接器　测试失败 - {str(e)}", file=sys.stderr)
            output['body']["log"] = f"{self.name} 连接器　测试异常 - {str(e)}"
        finally:
            self.log_out(output)
            return output

    @CatchErr.print_err_stack
    def _run(self, inp, connect, dispatcher_url):
        """
        私有函数，一切从我运行
        """

        self.dispatcher_url = dispatcher_url

        core = Core()

        # 入参验证
        core.check_data(inp, self.inputModel)
        core.check_data(connect, self.connModel)

        # 运行自写　run
        self.connection(connect)
        self.run(inp)

        output = self.format_output
        output["body"]["log"] = f"{self.name} succ"

        self.log_out(output)
        return output

    @CatchErr.print_err_stack
    def send(self, data: dict = {}) -> None:
        core = Core()

        core.check_data(data, self.outputModel)
        self.log_out(data)

        resp = requests.post(self.dispatcher_url, json=data)

        self.log_out(f"[Response {resp.status_code}] {resp.text}")





