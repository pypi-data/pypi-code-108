from pyocs import pyocs_config
from pyocs.pyocs_database import pyocsDataBase
class commonDataBase:
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(commonDataBase, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = pyocs_config.PyocsConfig.get_config()
        self.database = pyocsDataBase(
            pyocsDataBase.sql_server(config['sql_host'], int(config['sql_port']), config['sql_user_name'],
                                     config['sql_password'], config['sql_database_name']))
    def is_all_chinese(self, strs):
        for i in strs:
            if not '\u4e00' <= i <= '\u9fa5':
                return False
        return True

    def get_code_mapping_info_by_project(self, project):
        data = self.database.get_value_of_key('pyocs_jenkins_autobuild_map', 'project', project)
        result = list(data)
        return result

    def get_download_link_of_dt_by_customer(self, customer):
        data = self.database.get_value_of_key('pyocs_customer_need_map', 'customer', customer)
        return data[0]

    def get_region_mapping_info_by_country(self, country):
        i = 0
        if self.is_all_chinese(country):
            maplist = self.database.get_value_of_key('pyocs_auto_conf_country_map', 'country_ch', country)
        else:
            maplist = self.database.get_value_of_key('pyocs_auto_conf_country_map', 'country_en', country)
        maplist = list(maplist[1:])
        while i < len(maplist):
            if maplist[i] == '':
                maplist[i] = None
            i += 1
        return maplist

    def get_osm_distribute_mapping_info_by_user(self, user):
        maplist = self.database.get_value_of_key('pyocs_osm_data', 'User', user)
        return list(maplist)

    def get_download_link_software_confirm_table_by_customer(self, customer_name: str):
        maplist = self.database.get_value_of_key('pyocs_customer_sw_confirm_table', 'customer', customer_name)
        return maplist[0]

if __name__ == "__main__":
    db = commonDataBase()
    re = db.get_osm_distribute_mapping_info_by_user('功能元.xls')
    print(re)
