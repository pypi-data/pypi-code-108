from auger_ml.data_source.data_source_api import DataSourceProxyBaseAPI
from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas

class DataSourceAPIPandasProxy(DataSourceProxyBaseAPI):
    def __init__(self, options):
        super(DataSourceAPIPandasProxy, self).__init__(options)

    def run_ds_method(self, func, *args):
        if type(func) is str:
            func_name = func
        else:
            func_name = func.__name__

        params = {"remote_method_name": func_name, "remote_method_arguments": list(args),
            'data_path': self.options.get('data_path')}

        from auger_ml.tasks_queue.tasks import datasource_task, execute_task
        return execute_task(self.options, datasource_task, params, wait_for_result=self.sync_mode)

    def _get_datacache_path(self, suffix):
        return DataSourceAPIPandas.get_datacache_path_s(self.options, suffix)

    def getFoldPath(self, nFold=0):
        return DataSourceAPIPandas.getFoldPath_s(self.options, nFold)

    def loadFoldFile(self, nFold=0):
        return DataSourceAPIPandas.loadFoldFile_s(self.options, nFold)
    
