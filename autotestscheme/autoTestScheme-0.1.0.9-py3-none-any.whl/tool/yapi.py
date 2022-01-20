import requests
import os
from autoTestScheme import conf, logger
from autoTestScheme.common import constant, config
from autoTestScheme.common.common import hump2underline


class Yapi(object):
    """
    yapi
    """

    def __init__(self, name):
        if conf.settings.exists(name):
            self.yapi_config = conf.settings.get(name)
            assert self.yapi_config.get('case_folder') is not None, "case_folder 配置不存在"
            assert self.yapi_config.get('api_folder') is not None, "api_folder 配置不存在"
            assert self.yapi_config.get('data_folder') is not None, "data_folder 配置不存在"
        else:
            assert False, "不存在配置:{}".format(name)

    def send_yapi_request(self, url, data):
        """
        发送yapi请求
        :param url:
        :param data:
        :return:
        """
        if self.yapi_config.base_url.endswith("/") is False:
            self.yapi_config.base_url += "/"
        data['token'] = self.yapi_config.token
        url = self.yapi_config.base_url + url
        response = requests.get(url, data).json()
        logger.debug('url:{}, data:{}\n, response:{}'.format(url, data, response))
        assert response['errcode'] != 40011, 'token错误'
        return response['data']

    def load_yapi(self):
        """
        加载Yapi用例、api、代码
        :return:
        """
        case_id_list = self.yapi_config.get('case_id_list', [])
        if len(case_id_list) == 0:
            module_list = self.yapi_config.get('module_list')
            limit = self.yapi_config.get('limit', 10000)
            if module_list is None:
                data = {'project_id': self.yapi_config.project_id, 'limit': limit}
                case_id_list = [i['_id'] for i in self.send_yapi_request("api/interface/list", data)]
            else:
                for module in module_list:
                    data = {'catid': module, 'limit': limit}
                    case_id_list += [i['_id'] for i in self.send_yapi_request("api/interface/list_cat", data)['list']]
        self.load_yapi_by_id_list(case_id_list, conf.settings.run.test_tags)

    def load_yapi_by_id_list(self, id_list, tag=[]):
        """
        根据用例ID列表加载yapi用例
        :param id_list:
        :param tag:
        :return:
        """
        if len(id_list) == 0:
            logger.error("yapi加载错误，请确认项目ID、url是否配置正确")
            return
        module_info = {i['_id']: i['name'] for i in self.send_yapi_request("api/interface/getCatMenu", {'project_id': self.yapi_config.project_id})}
        project_name = self.send_yapi_request("api/project/get", {})['name']
        api_folder = os.path.join(constant.BASE_DIR, *self.yapi_config.api_folder)
        data_folder = os.path.join(constant.BASE_DIR, *self.yapi_config.data_folder)
        case_folder = os.path.join(constant.BASE_DIR, *self.yapi_config.case_folder)
        for _id in id_list:
            api_info = self.send_yapi_request("api/interface/get", {'id': _id})

            _path = os.path.split(api_info['path'])
            api_id = hump2underline(_path[-1])
            if len(_path) > 1 and _path[-2].startswith('v') is False:
                api_id += '_{}'.format(os.path.split(_path[-2])[-1])
            module_name = module_info[api_info['catid']]
            ins = self.get_yapi_ins(api_info)
            self.write(api_id, api_info['title'].strip(), api_info['method'], api_info['path'], project_name, module_name,
                       tag, api_folder, data_folder, case_folder, ins, base=self.yapi_config.base)

    def get_yapi_ins(self, api_info):
        """
        获取yapi的入参
        :param api_info:
        :return:
        """
        ins = {}
        for i in api_info['req_body_form']:
            example = i.get('example')
            if example is None:
                if i.get('type', 'text') == 'text':
                    example = str(3)
            ins[i['name']] = example
        return ins

    def write(self, api_id, title, method, path, project_name, module_name, tag, api_folder, data_folder, case_folder,
              ins={}, outs={}, base="from base.base import TestBase"):
        """
        写入
        :param api_id: api的ID号
        :param title: api标题
        :param method: 请求方式
        :param project_name: 项目名
        :param module_name: 模块名
        :param path: 请求路径
        :param tag: 当前环境
        :param api_folder: api的路径
        :param data_folder: data的路径
        :param case_folder: case的路径
        :param ins: 输入
        :param outs: 输出
        :return:
        """
        data = {"id": api_id, "title": title, "method": method, "params": {}, "data": {},
                "headers": {}, "path": path}
        # 写入API
        api_path = os.path.join(api_folder, api_id + ".json")
        case_name = 'test_{}'.format(api_id)
        if os.path.exists(api_path) is False:
            logger.info("开始写入api:路径({}), 标题({}), api_id({})".format(api_path, title, api_id))
            config.Json(api_path).set_object(data)
        # 写入case
        case_path = os.path.join(case_folder, case_name + '.py')
        if os.path.exists(case_path) is False:
            case_code = self.get_case_code(module_name, title, api_id, base)
            logger.info("开始写入case:路径({}), 标题({}), api_id({})".format(case_path, title, api_id))
            with open(case_path, 'w') as f:
                f.write(case_code)

        # 写入data数据
        data_path = os.path.join(data_folder, case_name + ".json")
        if os.path.exists(data_path) is False:
            logger.info("开始写入data:路径({}), 标题({}), api_id({})".format(data_path, title, api_id))
            data = []
            data.append({"__file": case_name, "__func": "test_01", "__dependent_class": None})
            data.append({"title": title, "tags": tag, "ins": ins, "outs": outs})
            config.Json(data_path).set_object(data)

    def get_case_code(self, epic, feature, api_id, base="from base.base import TestBase"):
        return """
import allure
{}


@allure.epic("{}")
@allure.feature("{}")
class TestCase(TestBase):

    def test_01(self, data_conversion, data):
        ins, outs = data_conversion.get('ins', 'outs')
        response = self.send_post_request("{}", ins)
        self.check_response(response, outs)\n""".format(base, epic, feature, api_id)
