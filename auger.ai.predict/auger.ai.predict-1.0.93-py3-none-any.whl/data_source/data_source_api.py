from auger_ml.FSClient import *

class DataSourceProxyBaseAPI(object):
    def __init__(self, options):
        self.sync_mode = True
        self.options = options

    def run_ds_method(self, func, *args):
        pass

    def set_sync_mode(self, sync):
        self.sync_mode = sync

    def _get_datacache_path(self, suffix):
        return self.run_ds_method("_get_datacache_path", suffix)

    def getOptions(self):
        return self.options

    def setOptions(self, value):
        self.options = value
        return self

    def load(self, features=None, use_cache=True):
        self.run_ds_method("load", features, use_cache)
        return self

    def load_records(self, records, features=None, use_cache=False ):
        self.run_ds_method("load_records", records, features, use_cache)
        return self

    def count(self):
        return self.run_ds_method("count")

    @property
    def columns(self):
        return self.run_ds_method("columns")

    @property
    def dtypes(self):
        return self.run_ds_method("dtypes")

    def getCategoricalsInfo(self):
        return self.run_ds_method("getCategoricalsInfo")

    def getSummary(self):
        return self.run_ds_method("getSummary")

    def getStatistics(self):
        return self.run_ds_method("getStatistics")

    def getMetaFeatures(self):
        return self.run_ds_method("getMetaFeatures")

    def withJsonColumn(self, col_name, json_col_name, child_name, col_type):
        self.run_ds_method("withJsonColumn", col_name, json_col_name, child_name, col_type)
        return self

    def withCustomColumn(self, col_name, eval_text):
        self.run_ds_method("withCustomColumn", col_name, eval_text)
        return self

    def withColumn(self, col_name, expr):
        self.run_ds_method("withColumn", col_name, expr)
        return self

    def withNumericColumn(self, col_name):
        self.run_ds_method("withNumericColumn", col_name)
        return self

    def withBooleanColumn(self, col_name):
        self.run_ds_method("withBooleanColumn", col_name)
        return self
        
    def convertToCategorical(self, col_names, is_target = False, categories = None):
        self.run_ds_method("convertToCategorical",col_names, is_target, categories)
        return self

    def getFoldPath(self, nFold=0):
        return self.run_ds_method("getFoldPath", nFold)

    def transform(self, transforms):
        return self.run_ds_method("transform", transforms)

    def expandCategoricalFeatures(self, features):        
        return self.run_ds_method("expandCategoricalFeatures", features)

    def saveToCacheFile(self, name):
        self.run_ds_method("saveToCacheFile", name)

    def loadFromCacheFile(self, name):
        return self.run_ds_method("loadFromCacheFile", name)

    def select_and_limit(self, features, limit):
        return self.run_ds_method("select_and_limit", features, limit)

    def dropna(self, columns=None):
        self.run_ds_method("dropna", columns)
        return self

    def fillna(self, value):
        self.run_ds_method("fillna", value)
        return self

    def search(self, params, features, limit):
        return self.run_ds_method("search", params, features, limit)

    def calculateFeaturesCorrelation(self, features, target):
        return self.run_ds_method("calculateFeaturesCorrelation", features, target)

    def calculateAllFeaturesCorrelation(self, names):
        return self.run_ds_method("calculateAllFeaturesCorrelation", names)

    def saveAsSingleCSVFile(self, path):
        return self.run_ds_method("saveAsSingleCSVFile", path)

    def splitToFiles(self, save_to_csv=False):
        return self.run_ds_method("splitToFiles", save_to_csv)

    def splitToFoldFiles(self, fold_name=None):
        return self.run_ds_method("splitToFoldFiles", fold_name)

    def filter_ex(self, params, conditions=None):
        self.run_ds_method("filter_ex", params, conditions)
        return self

    def update_options_by_dataset_statistics(self):
        self.run_ds_method("update_options_by_dataset_statistics")
        return self

class DataSourceAPIDirect(DataSourceProxyBaseAPI):
    def __init__(self, ds_impl):
        self.ds_impl = ds_impl        
        super(DataSourceAPIDirect, self).__init__(ds_impl.getOptions())

    def run_ds_method(self, func, *args):
        if type(func) is str:
            func_name = func
        else:
            func_name = func.__name__

        if self.ds_impl:
            result = getattr(self.ds_impl, func_name)
            if callable(result):
                if args:
                    result = result(*args)
                else:
                    result = result()

            #print(result)        
            if result != self.ds_impl:        
                return result
                
        return None    
