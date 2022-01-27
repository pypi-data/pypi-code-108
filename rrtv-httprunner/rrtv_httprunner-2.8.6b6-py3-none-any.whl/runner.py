import datetime
import json
import os
import sys
import time
import uuid
from typing import List, Dict, Text, NoReturn
from urllib.parse import unquote

import demjson3 as demjson

from rrtv_httprunner.mysqls import MySQLHandler
from rrtv_httprunner.rediss import RedisHandler

try:
    import allure

    USE_ALLURE = True
except ModuleNotFoundError:
    USE_ALLURE = False
# import allure
from loguru import logger

from rrtv_httprunner import utils, exceptions, globalvar
from rrtv_httprunner.client import HttpSession
from rrtv_httprunner.exceptions import ValidationFailure, ParamsError
from rrtv_httprunner.ext.uploader import prepare_upload_step
from rrtv_httprunner.loader import load_project_meta, load_testcase_file
from rrtv_httprunner.models import (
    TConfig,
    TStep,
    VariablesMapping,
    StepData,
    TestCaseSummary,
    TestCaseTime,
    TestCaseInOut,
    ProjectMeta,
    TestCase,
    Hooks, data_enum, AllureParameter, DiffParameter
)
from rrtv_httprunner.parser import build_url, parse_data, parse_variables_mapping
from rrtv_httprunner.response import ResponseObject, extend_validate
from rrtv_httprunner.testcase import Config, Step
from rrtv_httprunner.utils import merge_variables, write_excel, md5_encode


class HttpRunner(object):
    config: Config
    teststeps: List[Step]

    success: bool = False  # indicate testcase execution result
    __config: TConfig
    __teststeps: List[TStep]
    __project_meta: ProjectMeta = None
    __case_id: Text = ""
    __export: List[Text] = []
    __step_datas: List[StepData] = []
    __session: HttpSession = None
    __session_variables: VariablesMapping = {}
    __validate: List[Dict] = []
    # time
    __start_at: float = 0
    __duration: float = 0
    # log
    __log_path: Text = ""

    def __init_tests__(self) -> NoReturn:
        self.__config = self.config.perform()
        self.__teststeps = []
        for step in self.teststeps:
            self.__teststeps.append(step.perform())

    @property
    def raw_testcase(self) -> TestCase:
        if not hasattr(self, "__config"):
            self.__init_tests__()

        return TestCase(config=self.__config, teststeps=self.__teststeps)

    def with_project_meta(self, project_meta: ProjectMeta) -> "HttpRunner":
        self.__project_meta = project_meta
        return self

    def with_session(self, session: HttpSession) -> "HttpRunner":
        self.__session = session
        return self

    def with_case_id(self, case_id: Text) -> "HttpRunner":
        self.__case_id = case_id
        return self

    def with_variables(self, variables: VariablesMapping) -> "HttpRunner":
        self.__session_variables = variables
        return self

    def with_export(self, export: List[Text]) -> "HttpRunner":
        self.__export = export
        return self

    def with_validate(self, validate: List[Dict]) -> "HttpRunner":
        self.__validate = validate
        return self

    def __call_hooks(
            self, hooks: Hooks, step_variables: VariablesMapping, hook_msg: Text,
    ) -> NoReturn:
        """ call hook actions.

        Args:
            hooks (list): each hook in hooks list maybe in two format.

                format1 (str): only call hook functions.
                    ${func()}
                format2 (dict): assignment, the value returned by hook function will be assigned to variable.
                    {"var": "${func()}"}

            step_variables: current step variables to call hook, include two special variables

                request: parsed request dict
                response: ResponseObject for current response

            hook_msg: setup/teardown request/testcase

        """
        logger.info(f"call hook actions: {hook_msg}")

        if not isinstance(hooks, List):
            logger.error(f"Invalid hooks format: {hooks}")
            return

        for hook in hooks:
            if isinstance(hook, Text):
                # format 1: ["${func()}"]
                logger.debug(f"call hook function: {hook}")
                parse_data(hook, step_variables, self.__project_meta.functions)
            elif isinstance(hook, Dict) and len(hook) == 1:
                # format 2: {"var": "${func()}"}
                var_name, hook_content = list(hook.items())[0]
                hook_content_eval = parse_data(
                    hook_content, step_variables, self.__project_meta.functions
                )
                logger.debug(
                    f"call hook function: {hook_content}, got value: {hook_content_eval}"
                )
                logger.debug(f"assign variable: {var_name} = {hook_content_eval}")
                step_variables[var_name] = hook_content_eval
            else:
                logger.error(f"Invalid hook format: {hook}")

    def __execute(self, aspect: Text, step: TStep, variables_mapping=None,
                  functions_mapping=None, ) -> NoReturn:

        def execute(opportunity):
            for s in opportunity:
                if data_enum.VAR_SYMBOL in s:
                    var_name = s.split(data_enum.VAR_SYMBOL)[1]
                    hook_content_eval = parse_data(s.split(data_enum.VAR_SYMBOL)[0], variables_mapping,
                                                   functions_mapping)
                    extract_mapping[var_name] = hook_content_eval
                    variables_mapping.update(extract_mapping)
                    logger.debug(f"assign variable: {var_name} = {hook_content_eval}")
                else:
                    parse_data(
                        s, variables_mapping, functions_mapping
                    )

        need_configured_attr = data_enum.SUPPORT_TYPES
        extract_mapping = {}
        has_attr = any(attr in step.variables for attr in need_configured_attr)  # 判断是否有数据源
        if has_attr is False and len(step.begin) == 1 and step.begin[0].startswith("cmd:"):
            has_attr = True

        if aspect == "begin":
            if not has_attr:
                has_attr = any(data_enum.DB_CONFIG_SYMBOL in begin for begin in step.begin)
            if not has_attr:
                raise Exception("data source not found, please check configuration")
            if has_attr is True and step.begin:
                logger.info("begin start execute >>>>>>")
                execute(step.begin)

        elif aspect == "end":
            if not has_attr:
                has_attr = any(data_enum.DB_CONFIG_SYMBOL in end for end in step.end)
            if not has_attr:
                raise Exception("data source not found, please check configuration")
            if has_attr is True and step.end:
                logger.info("end start execute >>>>>>")
                execute(step.end)

    def build_api_testcase(self, config: TConfig) -> int:
        if self.__project_meta.datasource == {}:
            raise Exception("data source not found, please check configuration in .env") from None
        db = MySQLHandler(self.__project_meta.datasource)
        # 测试用例表
        if config.path is None:
            path = ""
        else:
            path = config.path.split(self.__project_meta.RootDir)[-1].replace("\\", "/")

        case_name = config.name if config.name is not None else ""  # 用例名称
        mark = {}
        source = "python"  # 脚本来源
        _format = ""  # 脚本格式
        created_by, updated_by, mode = self.__project_meta.created_by, self.__project_meta.updated_by, self.__project_meta.mode
        if path.endswith(".py"):
            _format = "python"
        elif path.endswith(".json"):
            _format = "json"
        elif path.endswith(".yml") or path.endswith(".yaml"):
            _format = "yaml"
        else:
            _format = "http"
        if _format != "yaml":
            if hasattr(self, "pytestmark"):
                for m in self.pytestmark:
                    mark[m.name] = m.args
        mark = json.dumps(mark, ensure_ascii=False)
        api_testcase = db.query(
            f"select * from t_api_testcase where path='{path}'and deleted=0 and enable=1 order by created_time desc limit 1;")
        if api_testcase is None:
            _id = db.insert(
                "insert into t_api_testcase (name, mark, mode, source, format, path ,enable, deleted, created_by, updated_by) values (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s)",
                (case_name, mark, mode, source, _format, path, 1, 0, created_by, updated_by))
            return _id
        else:
            db.query(
                "update t_api_testcase set name = %s,mark=%s,mode=%s,source=%s,format=%s,path=%s,enable=%s,deleted=%s ,created_by=%s, updated_by=%s where id=%s;",
                (case_name, mark, mode, source, _format, path, 1, 0, created_by, updated_by, api_testcase['id']))
            return api_testcase['id']

    def build_api_testcase_config(self, _id, config: TConfig):
        db = MySQLHandler(self.__project_meta.datasource)
        # 用例配置表
        created_by, updated_by, mode = self.__project_meta.created_by, self.__project_meta.updated_by, self.__project_meta.mode
        config_name = config.name  # 配置名称
        verify = 1 if config.verify is True else 0
        base_url = config.base_url if config.base_url is not None else ""
        variables = json.dumps(config.variables, ensure_ascii=False)
        parameters = json.dumps(globalvar.get_value("parameters", None), ensure_ascii=False) if globalvar.get_value(
            "parameters",
            None) is not None else ""
        export = json.dumps(config.export, ensure_ascii=False)
        datasource = json.dumps(config.datasource, ensure_ascii=False)
        api_testcase_config = db.query(f"select * from t_api_testcase_config where case_id={_id};")
        if api_testcase_config is None:
            db.insert(
                "insert into t_api_testcase_config (case_id, name, verify, base_url, variables, parameters, export, datasource, created_by, updated_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                (_id, config_name, verify, base_url, variables, parameters, export, datasource, created_by, updated_by))
        else:
            db.query(
                f"update t_api_testcase_config set name=%s,verify=%s,base_url=%s,variables=%s,parameters=%s,export=%s,datasource=%s,created_by=%s,updated_by=%s where case_Id={_id};",
                (config_name, verify, base_url, variables, parameters, export, datasource, created_by, updated_by))

    def build_project_meta(self, _id):
        db = MySQLHandler(self.__project_meta.datasource)
        rd = RedisHandler({'host': 'localhost', 'port': '6379', 'password': '', 'db': '0'})
        separator = "\\" if sys.platform.startswith("win") else "/"
        created_by, updated_by, mode = self.__project_meta.created_by, self.__project_meta.updated_by, self.__project_meta.mode

        rd.str_set("Python::Off::Datasource", json.dumps(self.__project_meta.datasource, ensure_ascii=False))

        def debugtalk():
            # 写入debugtalk文件
            path = self.__project_meta.debugtalk_path
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    debugtalk_py = f.read()
                    rd.str_set("Python::Off::Debugtalk", json.dumps(debugtalk_py, ensure_ascii=False))

        def custom():
            # 写入自定义路径文件
            custom_name = []
            if self.__project_meta.custom_path is not None:
                for path in self.__project_meta.custom_path:
                    if not path.startswith(separator):
                        path = separator + path
                    custom_name.append(path)
                    whole_path = self.__project_meta.RootDir + path
                    if os.path.exists(whole_path):
                        with open(whole_path, 'r', encoding='utf-8') as f:
                            custom_py = f.read()
                            if custom_py != "":
                                rd.hash_set("Python::Off::Custom", path, json.dumps(custom_py, ensure_ascii=False))

        def self_file():
            # 写入自身文件
            # 操作t_project_meta项目元数据表
            self_name = self.__config.path
            self_py = ""
            if self_name is not None:
                if len(self_name) != 0:
                    self_name = self_name.split(separator)[-1]
                if os.path.exists(self.__config.path):
                    with open(self.__config.path, 'r', encoding='utf-8') as f:
                        self_py = json.dumps(f.read(), ensure_ascii=False)
            project_meta = db.query(f"select * from t_project_meta where case_id={_id};")
            if project_meta is None:
                sql = "insert into t_project_meta (case_id, self_py_name, self_py, CREATED_BY, UPDATED_BY) VALUES (%s,%s,%s,%s,%s);"
                db.insert(sql, (_id, self_name, self_py, created_by, updated_by))
            else:
                sql = f"update t_project_meta set case_id=%s,self_py_name=%s,self_py=%s,CREATED_BY=%s,UPDATED_BY=%s where id={project_meta['id']};"
                db.query(sql, (_id, self_name, self_py, created_by, updated_by))

        debugtalk()
        custom()
        self_file()

    def build_api_testcase_step(self, _id, parent_id, teststeps: List[TStep], cite: bool):
        db = MySQLHandler(self.__project_meta.datasource)
        created_by, updated_by, mode = self.__project_meta.created_by, self.__project_meta.updated_by, self.__project_meta.mode

        def getLocalNoneStep(__md5_list: List, cid):
            """
            找出本地不存在 库中存在的step
            """
            step_db_list: List = db.query(f"select * from t_api_testcase_step where case_id='{cid}';", one=False)
            md5_local_list = [s for s in __md5_list if s is not None]
            md5_db_list = [s["md5"] for s in step_db_list if s["md5"] is not None]
            __diff = []
            for sdb in md5_db_list:
                for k, sl in enumerate(md5_local_list):
                    if sdb == sl:
                        break
                    if sdb != sl and k == len(md5_local_list) - 1:
                        __diff.append(sdb)
            return __diff

        def removeLocalNoneStepFromDb(__diff: List):
            for d in __diff:
                db.query(f"delete from t_api_testcase_step where md5='{d}'")

        md5_list = []

        def md5Step(*args):
            text = args.__str__()
            return md5_encode(text)

        # 测试用例步骤表
        for index, step in enumerate(teststeps):
            sequence = index
            if cite is True:
                step = step._Step__step_context
            if step.testcase is None:
                api = ""
                middleware_begin = json.dumps(step.begin, ensure_ascii=False)
                begin_hooks = json.dumps(step.begin_hooks, ensure_ascii=False)
                setup_hooks = json.dumps(step.setup_hooks, ensure_ascii=False)
                url = step.request.url if step.request.url is not None else ""
                request = json.dumps(step.request.__dict__, ensure_ascii=False)
                name = step.name
                extract = json.dumps(step.extract, ensure_ascii=False)
                tear_down_hooks = json.dumps(step.teardown_hooks, ensure_ascii=False)
                validate = json.dumps(step.validators, ensure_ascii=False)
                middleware_end = json.dumps(step.end, ensure_ascii=False)
                end_hooks = json.dumps(step.end_hooks, ensure_ascii=False)
                step.variables.pop("response")
                step.variables.pop("request")
                variables = json.dumps(step.variables, default=lambda o: o.__dict__, ensure_ascii=False)
                md5 = md5Step(api, sequence, middleware_begin, begin_hooks, variables, setup_hooks, url, request, name,
                              extract, tear_down_hooks, validate, middleware_end, end_hooks)
                md5_list.append(md5)
                # 判断该用例库中是否存在 用例不存在新增
                check = db.query("select * from t_api_testcase_step where md5=%s;", md5)
                if check is None:
                    sql = "insert into t_api_testcase_step (case_id, name ,api, testcase, sequence, middleware_begin, begin_hooks, variables,setup_hooks, url, request, extract, tear_down_hooks, validate, middleware_end, end_hooks,md5, created_by, updated_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                    db.insert(sql, (
                        _id, name, api, parent_id, sequence, middleware_begin, begin_hooks, variables, setup_hooks, url,
                        request,
                        extract,
                        tear_down_hooks, validate, middleware_end, end_hooks, md5, created_by, updated_by))
            else:
                # testcase不为空说明是引用用例
                path = step.testcase.config.path.split(self.__project_meta.RootDir)[-1].replace("\\", "/")
                export = json.dumps(step.export, ensure_ascii=False)
                api_testcase = db.query(
                    f"select * from t_api_testcase where path='{path}' and deleted=0 and enable=1 order by created_time desc limit 1;")
                if api_testcase is not None:
                    md5 = md5Step(_id, step.name, api_testcase['id'], sequence, export, created_by, updated_by)
                    md5_list.append(md5)
                    check = db.query("select * from t_api_testcase_step where md5=%s;", md5)
                    if check is None:
                        # 本地case数量大于db中的数量 代表有新case 所以插入该新增case
                        sql = "insert into t_api_testcase_step (case_id, name ,api, testcase, sequence, middleware_begin, begin_hooks, setup_hooks, url, request, extract, tear_down_hooks, validate, middleware_end, end_hooks, export, md5, created_by, updated_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                        db.insert(sql, (
                            _id, step.name, "", api_testcase['id'], sequence, "", "", "", "", "", "", "", "", "", "",
                            export, md5,
                            created_by,
                            updated_by))
                else:
                    # 递归新增
                    self.build_api_testcase_step(self._id, -1, step.testcase.teststeps, True)
        diff = getLocalNoneStep(md5_list, _id)
        removeLocalNoneStepFromDb(diff)

    def __run_step_request(self, step: TStep) -> StepData:
        """run teststep: request"""
        step_data = StepData(name=step.name)

        # parse
        prepare_upload_step(step, self.__project_meta.functions)
        request_dict = step.request.dict()
        request_dict.pop("upload", None)

        # begin hooks
        if step.begin_hooks:
            self.__call_hooks(step.begin_hooks, step.variables, "begin request")

        # execute begin
        if step.begin:
            self.__execute("begin", step, step.variables, self.__project_meta.functions)

        parsed_request_dict = parse_data(
            request_dict, step.variables, self.__project_meta.functions
        )
        parsed_request_dict["headers"].setdefault(
            "HRUN-Request-ID",
            f"HRUN-{self.__case_id}-{str(int(time.time() * 1000))[-6:]}",
        )
        step.variables["request"] = parsed_request_dict

        # setup hooks
        if step.setup_hooks:
            self.__call_hooks(step.setup_hooks, step.variables, "setup request")

        # prepare arguments
        method = parsed_request_dict.pop("method")
        url_path = parsed_request_dict.pop("url")
        url = build_url(self.__config.base_url, url_path)
        parsed_request_dict["verify"] = self.__config.verify
        parsed_request_dict["json"] = parsed_request_dict.pop("req_json", {})

        a = AllureParameter()
        diff_obj = DiffParameter()
        diff_obj.base_url = self.__config.base_url
        parsed_request_dict["allure"] = a
        parsed_request_dict["diff"] = diff_obj
        # request
        resp = self.__session.request(method, url, **parsed_request_dict)
        resp_obj = ResponseObject(resp)
        step.variables["response"] = resp_obj

        # teardown hooks
        if step.teardown_hooks:
            self.__call_hooks(step.teardown_hooks, step.variables, "teardown request")

        if USE_ALLURE:
            # update allure report meta
            allure.attach(str(resp_obj.resp_obj.status_code), "状态码:", allure.attachment_type.TEXT)
            try:
                if resp_obj.resp_obj.text is not None and resp_obj.resp_obj.text != "":
                    value = demjson.decode(resp_obj.resp_obj.text)
                    if "code" in value:
                        allure.attach(str(value["code"]), "code:", allure.attachment_type.TEXT)
                    if "msg" in value:
                        allure.attach(str(value["msg"]), "msg:", allure.attachment_type.TEXT)
                    if value != {}:
                        allure.attach(json.dumps(value, ensure_ascii=False), "data:",
                                      allure.attachment_type.TEXT)
            except:
                pass
            allure.attach(a.curl, "curl:", allure.attachment_type.TEXT)

        def log_req_resp_details():
            err_msg = "\n{} DETAILED REQUEST & RESPONSE {}\n".format("*" * 32, "*" * 32)

            # log request
            err_msg += "====== request details ======\n"
            err_msg += f"url: {url}\n"
            err_msg += f"method: {method}\n"
            headers = parsed_request_dict.pop("headers", {})
            err_msg += f"headers: {headers}\n"
            for k, v in parsed_request_dict.items():
                v = utils.omit_long_data(v)
                if isinstance(v, Text):
                    v = unquote(v)
                if isinstance(v, Dict):
                    v = {k: unquote(v) for k, v in v.items() if isinstance(v, Text)}
                err_msg += f"{k}: {repr(v)}\n"

            err_msg += "\n"

            # log response
            err_msg += "====== response details ======\n"
            err_msg += f"status_code: {resp.status_code}\n"
            err_msg += f"headers: {resp.headers}\n"
            err_msg += f"body: {repr(resp.text)}\n"
            logger.error(err_msg)

        # extract
        extractors = step.extract
        extract_mapping = resp_obj.extract(extractors, step.variables, self.__project_meta.functions)
        step_data.export_vars = extract_mapping

        variables_mapping = step.variables
        variables_mapping.update(extract_mapping)

        # validate
        validators = step.validators
        if diff_obj.diff != {}:
            validators = []
            validators.append(
                {'t1': resp_obj.body, 't2': demjson.decode(diff_obj.diff["t2"].resp_obj.text), 'kwargs': {},
                 'message': ''})
        session_success = False
        try:
            resp_obj.validate(
                validators, variables_mapping, self.__project_meta.functions
            )
            session_success = True

        except ValidationFailure:
            session_success = False
            log_req_resp_details()
            # log testcase duration before raise ValidationFailure
            self.__duration = time.time() - self.__start_at
            raise
        finally:
            self.success = session_success
            step_data.success = session_success

            if hasattr(self.__session, "data"):
                # rrtv_httprunner.client.HttpSession, not locust.clients.HttpSession
                # save request & response meta data
                self.__session.data.success = session_success
                self.__session.data.validators = resp_obj.validation_results

                # save step data
                step_data.data = self.__session.data

                # end hooks
                if step.end_hooks:
                    self.__call_hooks(step.end_hooks, step.variables, "end request")

                # execute end
                if step.end:
                    self.__execute("end", step, variables_mapping, self.__project_meta.functions)
            if globalvar.get_value("toexcel", "") != "":
                location = ""
                call = ""
                for marks in self.pytestmark:
                    if "location" == marks.name:
                        location = marks.args[0]
                    if "nocall" == marks.name:
                        call = "无"
                content = {"dir": self.config.path, "base_url": self.__config.base_url, "url": url_path,
                           "method": method, "name": self.config.name,
                           "location": location, "call": call, "response": resp_obj.body, "curl": a.curl}
                write_excel(content, globalvar.get_value("toexcel"))

        return step_data

    def __run_step_testcase(self, step: TStep) -> StepData:
        """run teststep: referenced testcase"""
        step_data = StepData(name=step.name)
        step_variables = step.variables
        step_export = step.export

        # step_testcase只有setup 无begin概念 此处setup等同于begin
        # setup hooks
        if step.setup_hooks:
            self.__call_hooks(step.setup_hooks, step.variables, "setup testcase")

        # execute setup
        if step.begin:
            self.__execute("begin", step, step.variables, self.__project_meta.functions)

        if hasattr(step.testcase, "config") and hasattr(step.testcase, "teststeps"):
            testcase_cls = step.testcase
            case_result = (
                testcase_cls()
                    .with_session(self.__session)
                    .with_case_id(self.__case_id)
                    .with_variables(step_variables)
                    .with_export(step_export)
                    .with_validate(step.validators)
                    .run()
            )

        elif isinstance(step.testcase, Text):
            if os.path.isabs(step.testcase):
                ref_testcase_path = step.testcase
            else:
                ref_testcase_path = os.path.join(
                    self.__project_meta.RootDir, step.testcase
                )

            case_result = (
                HttpRunner()
                    .with_session(self.__session)
                    .with_case_id(self.__case_id)
                    .with_variables(step_variables)
                    .with_export(step_export)
                    .run_path(ref_testcase_path)
            )

        else:
            raise exceptions.ParamsError(
                f"Invalid teststep referenced testcase: {step.dict()}"
            )

        # teardown hooks
        if step.teardown_hooks:
            self.__call_hooks(step.teardown_hooks, step.variables, "teardown request")

        # execute end
        if step.end:
            self.__execute("end", step, step.variables, self.__project_meta.functions)

        step_data.data = case_result.get_step_datas()  # list of step data
        step_data.export_vars = case_result.get_export_variables()
        step_data.success = case_result.success
        self.success = case_result.success

        if step_data.export_vars:
            logger.info(f"export variables: {step_data.export_vars}")

        return step_data

    def __run_step(self, step: TStep) -> Dict:
        """run teststep, teststep maybe a request or referenced testcase"""
        logger.info(f"run step begin: {step.name} >>>>>>")

        if step.request:
            step_data = self.__run_step_request(step)
        elif step.testcase:
            step_data = self.__run_step_testcase(step)
        else:
            raise ParamsError(
                f"teststep is neither a request nor a referenced testcase: {step.dict()}"
            )

        self.__step_datas.append(step_data)
        logger.info(f"run step end: {step.name} <<<<<<\n")
        return step_data.export_vars

    def __parse_config(self, config: TConfig) -> NoReturn:
        config.variables.update(self.__session_variables)
        config.variables.update(config.datasource)
        config.variables = parse_variables_mapping(
            config.variables, self.__project_meta.functions
        )
        config.name = parse_data(
            config.name, config.variables, self.__project_meta.functions
        )
        config.base_url = parse_data(
            config.base_url, config.variables, self.__project_meta.functions
        )

    def run_testcase(self, testcase: TestCase) -> "HttpRunner":
        """run specified testcase

        Examples:
            >>> testcase_obj = TestCase(config=TConfig(...), teststeps=[TStep(...)])
            >>> HttpRunner().with_project_meta(project_meta).run_testcase(testcase_obj)

        """
        self.__config = testcase.config
        self.__teststeps = testcase.teststeps

        # prepare
        self.__project_meta = self.__project_meta or load_project_meta(
            self.__config.path
        )
        self.__parse_config(self.__config)
        self.__start_at = time.time()
        self.__step_datas: List[StepData] = []
        self.__session = self.__session or HttpSession()
        # save extracted variables of teststeps
        extracted_variables: VariablesMapping = {}
        # run teststeps
        if globalvar.get_value("todb") is True:
            self._id = self.build_api_testcase(self.__config)
            self.build_api_testcase_config(self._id, self.__config)
            self.build_project_meta(self._id)
        for step in self.__teststeps:
            # override variables
            # step variables > extracted variables from previous steps
            step.variables = merge_variables(step.variables, extracted_variables)
            # step variables > testcase config variables
            step.variables = merge_variables(step.variables, self.__config.variables)
            step.variables = merge_variables(step.variables, self.__config.datasource)

            # parse variables
            step.variables = parse_variables_mapping(
                step.variables, self.__project_meta.functions
            )

            # run step
            if USE_ALLURE:
                with allure.step(f"step: {step.name}"):
                    extract_mapping = self.__run_step(step)
            else:
                extract_mapping = self.__run_step(step)

            # save extracted variables to session variables
            extracted_variables.update(extract_mapping)

        # 本地编写的脚本才会存储到db
        if globalvar.get_value("todb") is True and self.__project_meta.mode == "off-line":
            self.build_api_testcase_step(self._id, -1, self.__teststeps, False)
        self.__session_variables.update(extracted_variables)
        self.__duration = time.time() - self.__start_at
        return self

    def run_path(self, path: Text) -> "HttpRunner":
        if not os.path.isfile(path):
            raise exceptions.ParamsError(f"Invalid testcase path: {path}")

        testcase_obj = load_testcase_file(path)
        return self.run_testcase(testcase_obj)

    def run(self) -> "HttpRunner":
        """ run current testcase

        Examples:
            >>> TestCaseRequestWithFunctions().run()

        """
        self.__init_tests__()
        testcase_obj = TestCase(config=self.__config, teststeps=self.__teststeps)
        extend_validators = extend_validate(testcase_obj.teststeps[0].validators, self.__validate)
        testcase_obj.teststeps[0].validators = extend_validators
        return self.run_testcase(testcase_obj)

    def get_step_datas(self) -> List[StepData]:
        return self.__step_datas

    def get_export_variables(self) -> Dict:
        # override testcase export vars with step export
        export_var_names = self.__export or self.__config.export
        export_vars_mapping = {}
        for var_name in export_var_names:
            if var_name not in self.__session_variables:
                raise ParamsError(
                    f"failed to export variable {var_name} from session variables {self.__session_variables}"
                )

            export_vars_mapping[var_name] = self.__session_variables[var_name]

        return export_vars_mapping

    def get_summary(self) -> TestCaseSummary:
        """get testcase result summary"""
        start_at_timestamp = self.__start_at
        start_at_iso_format = datetime.datetime.fromtimestamp(start_at_timestamp).isoformat()
        return TestCaseSummary(
            name=self.__config.name,
            success=self.success,
            case_id=self.__case_id,
            time=TestCaseTime(
                start_at=self.__start_at,
                start_at_iso_format=start_at_iso_format,
                duration=self.__duration,
            ),
            in_out=TestCaseInOut(
                config_vars=self.__config.variables,
                export_vars=self.get_export_variables(),
            ),
            log=self.__log_path,
            step_datas=self.__step_datas,
        )

    def test_start(self, param: Dict = None) -> "HttpRunner":
        """main entrance, discovered by pytest"""
        self.__init_tests__()
        self.__project_meta = self.__project_meta or load_project_meta(
            self.__config.path
        )
        self.__case_id = self.__case_id or str(uuid.uuid4())
        self.__log_path = self.__log_path or os.path.join(
            self.__project_meta.RootDir, "logs", f"{self.__case_id}.run.log"
        )
        log_handler = logger.add(self.__log_path, level="DEBUG")

        # parse config name
        config_variables = self.__config.variables
        if param:
            config_variables.update(param)
        config_variables.update(self.__session_variables)
        self.__config.name = parse_data(
            self.__config.name, config_variables, self.__project_meta.functions
        )
        if USE_ALLURE:
            # update allure report meta
            allure.dynamic.title(self.__config.name)
            if self.__teststeps[-1].request is not None:
                requestUrl = self.__teststeps[-1].request.url
                url = str(self.__config.base_url if self.__config.base_url[-1] != "/" else self.__config.base_url[
                                                                                           0:-2]) + str(
                    requestUrl)
                allure.dynamic.description(f"URL:{url}")

        logger.info(
            f"Start to run testcase: {self.__config.name}, TestCase ID: {self.__case_id}"
        )

        try:
            return self.run_testcase(
                TestCase(config=self.__config, teststeps=self.__teststeps)
            )
        finally:
            logger.remove(log_handler)
            logger.info(f"generate testcase log: {self.__log_path}")
