import platform
from pyocs.pyocs_interface import UniteInterface
import abc
import os
import json
from pathlib import Path
from pyocs import pyocs_constant


class DTRuler(UniteInterface):

    panel_config_resource = "panel"
    country_config_resource = "country"
    ir_config_resource = "ir"
    hardware_config_resource = "hardware"
    language_config_resource = "language"

    def __init__(self, ocs_demand, excel_para: str, excel_file_location: str):
        super(DTRuler, self).__init__(ocs_demand=ocs_demand)
        self.line_number = excel_para  # excel中的行号
        self.excel_file_location = excel_file_location

    def resource_check(self):
        pass

    @abc.abstractmethod
    def get_ocs_modelid(self):
        pass

    @abc.abstractmethod
    def get_ocs_require(self):
        pass

    @abc.abstractmethod
    def get_code_branch(self):
        pass

    @staticmethod
    def get_json_base_dir(customer_id, project_name):
        if platform.system() == "Linux":
            home = Path(os.environ['HOME'])
        else:
            home = Path.home()
        json_base_path = home / pyocs_constant.JSON_BASE_DIR_NAME / customer_id / project_name
        return str(json_base_path)

    def get_config_res(self, key_type: str):
        """
        获取软件配置资源信息
        key_type: 可选值有 panel, hardware, ir, language, country
        """
        config_file = self.get_json_base_dir(self._customer_id, self.ocs_demand.get_ocs_project_name())
        config_file_type = config_file + '/' + key_type + '_config.json'
        try:
            with open(str(config_file_type), 'r', encoding='utf-8') as obj_res:
                res_dict = json.load(obj_res)
                return res_dict
        except FileNotFoundError:
            return None

