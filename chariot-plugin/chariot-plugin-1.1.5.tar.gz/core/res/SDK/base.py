import json
import traceback
from pydantic import BaseModel, ValidationError
import importlib
import sys
from jsonpointer import resolve_pointer, JsonPointerException


try:
    from . import models
except:
    import models


"""
错误处理以及一些零散的方法
"""


class CatchErr(object):

    @staticmethod
    def print_err_stack(func):
        # 打印错误堆栈

        def inner(*args, **kwargs):

            try:
                return func(*args, **kwargs)
            except:
                traceback.print_exc(file=sys.stderr)

        return inner


class Core(object):

    def get_stdin(self):

        assert not sys.stdin.isatty(), "Stdin is empty!!"

        return sys.stdin.read()


    def print_to_stdout(self, args, rt=""):

        data = json.dumps(args, ensure_ascii=False)

        sys.stdout.write(data + rt)

        sys.stdout.flush()


    def print_to_stderr(self, args):

        data = json.dumps(args, ensure_ascii=False)

        sys.stderr.write(data)

        sys.stderr.flush()


    @CatchErr.print_err_stack
    def get_cmd(self):

        cmd_list = ["run", "test", "http"]
        cmd = ''
        if len(sys.argv) >= 2:
            cmd = sys.argv[1]

        assert any([cmd == i for i in cmd_list]), f"invalid cmd: `{cmd}`"

        return cmd


    @CatchErr.print_err_stack
    def load_cls(self, module: str, model: str = None) -> object:

        mod = importlib.import_module(module)
        if model:
            cls = getattr(mod, model)
            return cls
        else:
            return mod


    def check_data(self, data: dict, model) -> BaseModel:

        try:
            cls_obj = model(**data)

            return cls_obj

        except ValidationError as e:
            raise Exception(f"{model} 验证不通过 - {e.json()}")


    @CatchErr.print_err_stack
    def complete_output(self, body, log=None, error=None) -> dict:
        """
        完整output
        """

        output_body_object = {'output': body}

        if log:
            output_body_object['log'] = log
            output_body_object['status'] = 'ok'
        if error:
            output_body_object['error'] = error
            output_body_object['status'] = 'error'

        output = {'version': 'v1', 'type': 'action_event', 'body': output_body_object}

        return output


    @CatchErr.print_err_stack
    def parse_stdin(self, stdin: str) -> dict:

        stdin_obj = json.loads(stdin)

        # 验证stdin 入参是否有误
        plugin_stdin = self.check_data(stdin_obj, models.PluginStdin)

        body_obj = plugin_stdin.body

        assert body_obj, 'Input must be has `body` attribute'

        return body_obj


    @CatchErr.print_err_stack
    def extract_pointer(self, content: dict, pointer: str = "", default=None):
        """
        dict　中提取指定数据
        无则不报错
        """

        data = None

        try:
            data = resolve_pointer(content, pointer, default)
        except JsonPointerException as e:
            self.print_to_stdout(e)

        return data


    @CatchErr.print_err_stack
    def to_model_name(self, name, put="Input"):
        """
        拼接　model　name，以用来类型验证或调用类
        model_name遵循大驼峰规范
        格式：　
            name = "action_name"
            model_name = "ActionNameInput"
        """

        model_name = "".join([i.capitalize() for i in name.split("_")]) + put

        return model_name







