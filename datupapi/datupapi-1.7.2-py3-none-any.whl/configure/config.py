import logging
import os
import yaml

from datetime import date, datetime, timedelta


class Config():

    LOCAL_PATH = '/tmp'

    def __init__(self, config_file=None, logfile=None):
        try:
            #Initialize config parameters
            with open(config_file) as file:
                params = yaml.full_load(file)
            self.access_key = params.get('aws_access_key')
            self.secret_key = params.get('aws_secret_key')
            self.region = params.get('aws_region')
            self.sql_database = params.get('sql_database')
            self.forecast_role = params.get('forecast_role')
            # Initialize Prepare training parameters
            self.dataset_orig_cols = params.get('prepare')[0].get('dataset_orig_cols')
            self.items_metadata = params.get('prepare')[1].get('items_metadata')
            # Initialize Paths parameters
            self.tenant_id = params.get('paths')[0].get('tenant_id')
            self.datalake = params.get('paths')[1].get('datalake')
            self.config_path = params.get('paths')[2].get('config_path')
            self.response_path = params.get('paths')[3].get('response_path')
            self.dataset_import_path = params.get('paths')[4].get('dataset_import_path')
            self.backtest_export_path = params.get('paths')[5].get('backtest_export_path')
            self.forecast_export_path = params.get('paths')[6].get('forecast_export_path')
            self.results_path = params.get('paths')[7].get('results_path')
            self.multiforecast_path = params.get('paths')[8].get('multiforecast_path')
            self.sftp_export = params.get('paths')[9].get('sftp_export')
            # Initialize Training parameters
            self.dataset_frequency = params.get('training')[0].get('dataset_frequency')
            self.forecast_types = params.get('training')[1].get('forecast_types')
            self.forecast_horizon = params.get('training')[2].get('forecast_horizon')
            self.input_window = params.get('training')[3].get('input_window')
            self.backtests = params.get('training')[4].get('backtests')
            self.backtest_ids = params.get('training')[5].get('backtest_ids')[:self.backtests]
            self.use_location = params.get('training')[6].get('use_location')
            self.normalization = params.get('training')[7].get('normalization')
            self.dropout_train = params.get('training')[8].get('dropout_train')
            # Initialize DeepAR training parameters
            self.epochs = params.get('deepar')[0].get('epochs')
            self.neurons = params.get('deepar')[1].get('neurons')
            self.hidden_layers = params.get('deepar')[2].get('hidden_layers')
            self.backtest_horizon = params.get('deepar')[3].get('backtest_horizon')
            self.use_automl = params.get('deepar')[4].get('use_automl')
            # Initialize Attention model training parameters
            self.epochs_attup = params.get('attup')[0].get('epochs_attup')
            self.save_last_epoch = params.get('attup')[1].get('save_last_epoch')
            self.lr = params.get('attup')[2].get('lr')
            self.units = params.get('attup')[3].get('units')
            self.batch_size = params.get('attup')[4].get('batch_size')
            self.n_iter = params.get('attup')[5].get('n_iter')
            self.momentum = params.get('attup')[6].get('momentum')
            self.lrS = params.get('attup')[7].get('lrS')
            # Initialize TFT
            self.epochs_tft = params.get('tft')[0].get('epochs_tft')
            self.gradient_clip_val = params.get('tft')[1].get('gradient_clip_val')
            self.lr_tft = params.get('tft')[2].get('lr_tft')
            self.lstm_layers = params.get('tft')[3].get('lstm_layers')
            self.hidden_size = params.get('tft')[4].get('hidden_size')
            self.attention_head_size = params.get('tft')[5].get('attention_head_size')
            self.hidden_continuous_size = params.get('tft')[6].get('hidden_continuous_size')
            self.n_iter_tft = params.get('tft')[7].get('n_iter_tft')
            self.batch_size_tft = params.get('tft')[8].get('batch_size_tft')
            # Initialize Importance parameters
            self.sku_impct = params.get('importance')[0].get('sku_impct')
            self.items_simulation= params.get('importance')[1].get('items_simulation')
            # Initialize Transform parameters
            self.abc_threshold = params.get('transform')[0].get('abc_threshold')
            self.fsn_threshold = params.get('transform')[1].get('fsn_threshold')
            self.xyz_threshold = params.get('transform')[2].get('xyz_threshold')
            self.export_item_ranking = params.get('transform')[3].get('export_item_ranking')
            self.error_ids = params.get('transform')[4].get('error_ids')
            self.upsample_frequency = params.get('transform')[5].get('upsample_frequency')
            # Initialize logger
            self.logfile = logfile + '_' + datetime.today().strftime("%Y%m%d-%H%M%S") + '.log'
            self.logger = logging.getLogger('__name__')
            self.logger.setLevel(logging.DEBUG)
            self.file_handler = logging.FileHandler(os.path.join(Config.LOCAL_PATH, self.logfile))
            self.file_format = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            self.file_handler.setLevel(logging.DEBUG)
            self.file_handler.setFormatter(self.file_format)
            self.logger.addHandler(self.file_handler)
        except FileNotFoundError as err:
            self.logger.exception(f'Config file not found. Please check entered path: {err}')
            raise
        finally:
            file.close()