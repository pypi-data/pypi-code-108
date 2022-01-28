import humailib.utils as hu

class Info(dict):
    
    def __init__(self):
        
        self.shorten_date_ranges = True
        
        return
    
    def init_for_email(
        self, 
        dataset_base, date_ranges, 
        activity, 
        min_hist_len, max_hist_len, 
        activity_column, activity_datetime_column, 
        send_datetime_column,
        cid_column,
        working_dir,
        shorten_date_ranges = True
    ):
        self['dataset_base'] = dataset_base
        self['dataset_table_base'] = dataset_base + '.mailings_events'
        self['date_ranges'] = date_ranges
        self['activity'] = activity
        self['min_hist_len'] = min_hist_len
        self['max_hist_len'] = max_hist_len
        self['activity_column'] = activity_column
        self['activity_datetime_column'] = activity_datetime_column
        self['send_datetime_column'] = send_datetime_column
        self['cid_column'] = cid_column
        self['working_dir'] = working_dir
        
        self.shorten_date_ranges = shorten_date_ranges
        
        self.__init_dateranges_str()
        self.__init_datasetname()
        self.__init_intermediate_and_training_files_email()
        self.__init_pipeline_files()
        self.__init_model_files()
        
        
    def init_for_transactions(
        self, 
        dataset_base, date_ranges, max_hist_len,
        datetime_column, cid_column,
        working_dir,
        table_name = None,
        shorten_date_ranges = True
    ):
        self['dataset_base'] = dataset_base
        if table_name is not None:
            self['dataset_table_base'] = dataset_base + '.' + table_name
        else:
            self['dataset_table_base'] = dataset_base + '.transactions'
        self['date_ranges'] = date_ranges
        self['activity'] = 'transactions'
        self['max_hist_len'] = max_hist_len
        self['datetime_column'] = datetime_column
        self['cid_column'] = cid_column
        self['working_dir'] = working_dir

        self.shorten_date_ranges = shorten_date_ranges

        self.__init_dateranges_str()
        self.__init_datasetname()
        self.__init_intermediate_and_training_files_transactions()
        self.__init_pipeline_files()
        self.__init_model_files()
        
        
    def init_for_products(
        self, 
        dataset_base, date_ranges, max_hist_len,
        datetime_column, cid_column, product_column,
        working_dir,
        shorten_date_ranges = True
     ):
        self['dataset_base'] = dataset_base
        self['dataset_table_base'] = dataset_base + '.products'
        self['date_ranges'] = date_ranges
        self['activity'] = 'products'
        self['max_hist_len'] = max_hist_len
        self['datetime_column'] = datetime_column
        self['cid_column'] = cid_column
        self['product_column'] = product_column
        self['working_dir'] = working_dir
        
        self.shorten_date_ranges = shorten_date_ranges

        self.__init_dateranges_str()
        self.__init_datasetname()
        self.__init_intermediate_and_training_files_products()      
        self.__init_pipeline_files()
        self.__init_model_files_product()
        
        
    def  __init_dateranges_str(self):
        
        if self.shorten_date_ranges:
            self.date_range_str = self['date_ranges'][0].split('to')[0] + 'to'+ self['date_ranges'][-1].split('to')[-1]
        else:
            self.date_range_str = '_'.join(self['date_ranges'])
            

    def __init_datasetname(self):
        
        self['source_datasets'] = ['{}_{}'.format(self['dataset_table_base'], dr) for dr in self['date_ranges']]
        self['datasetname'] = '_'.join([self['dataset_table_base']]+[self.date_range_str]).replace('.', '_')
        

    def __init_intermediate_and_training_files_base(self):
        
        self['hist_file_cached'] = "{}/data/{}_histories_{}.csv".format(
            self['working_dir'], self['datasetname'], self['activity']
        )
        
        """
        
        self['training_features_file'] = "{}/data/{}_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        self['training_file'] = "{}/data/{}_training_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        self['validation_file'] = "{}/data/{}_validation_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        self['test_file'] = "{}/data/{}_test_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        """
        
        self['all_training_features'] = "{}/data/{}_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        self['training_set'] = "{}/data/{}_training_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        self['validation_set'] = "{}/data/{}_validation_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        self['test_set'] = "{}/data/{}_test_features_max_hist_len_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        
    def __init_intermediate_and_training_files_email(self):
        
        self.__init_intermediate_and_training_files_base()
        
        
    def __init_intermediate_and_training_files_transactions(self):
        
        self.__init_intermediate_and_training_files_base()
        
        self['basic_training_features_file'] = "{}/data/{}_basic_training_features_{}_{}.csv".format(
            self['working_dir'], self['datasetname'], self['max_hist_len'], self['activity']
        )
        
        
    def __init_intermediate_and_training_files_products(self):
        
        self['transactions_training_features_file'] = "{}/data/{}_trans_training_features_{}.csv".format(
            self['working_dir'], self['datasetname'], self['activity']
        )
        
        self['items_training_features_file'] = "{}/data/{}_items_training_features_{}.csv".format(
            self['working_dir'], self['datasetname'], self['activity']
        )
        

    def __init_model_files(self):
        
        self['model_file'] = "{}/model.joblib".format(
            self['working_dir']
        )
        
        
    def __init_model_files_product(self):
        
        self['model_file'] = "{}/model.pkl".format(
            self['working_dir']
        )
        
        
    def __init_pipeline_files(self):
        
        self['preprocess_pipeline_file'] = "{}/preprocess_pipeline.joblib".format(
            self['working_dir']
        )
        
        self['preprocess_functions_file'] = "{}/preprocess_functions.pkl".format(
            self['working_dir']
        )


    
        

        