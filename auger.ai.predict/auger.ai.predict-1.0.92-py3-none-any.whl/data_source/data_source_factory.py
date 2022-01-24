#from data_source_api_proxy import *
import os

class DataSourceFactory(object):
    @classmethod
    def create(cls, options):
        ds_type = options.get("data_source_type", "pandas")
        job_server_url = options.get("job_server_url", None)

        if job_server_url:
            if ds_type == 'spark':
                from auger_ml.data_source.data_source_api_spark_proxy import DataSourceAPISparkProxy
                return DataSourceAPISparkProxy(options)
            elif ds_type == 'pandas':
                from auger_ml.data_source.data_source_api_pandas_proxy import DataSourceAPIPandasProxy                
                return DataSourceAPIPandasProxy(options)
            else:
                raise Exception("Unknown datasource type: %s"%ds_type)
        else:
            if ds_type == 'spark':
                from auger_ml.data_source.data_source_api_spark import DataSourceAPISpark
                return DataSourceAPIDirect(DataSourceAPISpark(options))
            elif ds_type == 'pandas':
                from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas
                from auger_ml.data_source.data_source_api import DataSourceAPIDirect

                return DataSourceAPIDirect(DataSourceAPIPandas(options))
            else:
                raise Exception("Unknown datasource type: %s"%ds_type)
