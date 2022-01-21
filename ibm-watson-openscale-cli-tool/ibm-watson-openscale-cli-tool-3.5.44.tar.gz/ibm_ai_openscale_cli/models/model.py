# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import datetime
import json
import os
import random
import pandas as pd
from io import StringIO
from pathlib import Path

from ibm_ai_openscale_cli.database_classes.cos import CloudObjectStorage
from ibm_ai_openscale_cli.enums import MLEngineType
from ibm_ai_openscale_cli.utility_classes.constants import WML_CHALLENGER_ENVIRONMENT_MAPPING, WML_SPARK_VERSION_SUPPORT_MAPPING
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.utility_classes.keras_unstructured_binary_text import read_lines, split_lines, format_scoring_input
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict, get_path, load_pickle_file

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import MonitorMeasurementRequest, Source
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord

logger = FastpathLogger(__name__)


class Model:

    CONFIGURATION_FILENAME = 'configuration.json'
    MODEL_META_FILENAME = 'model_meta.json'
    MODEL_CONTENT_FILENAME = 'model_content.gzip'
    PIPELINE_META_FILENAME = 'pipeline_meta.json'
    PIPELINE_CONTENT_FILENAME = 'pipeline_content.gzip'
    DRIFT_MODEL_FILENAME = 'drift_archive.tar.gz'
    TRAINING_DATA_STATISTICS_FILENAME = 'training_data_statistics.json'
    FAIRNESS_HISTORY_FILENAME = 'history_fairness.json'
    PAYLOAD_HISTORY_FILENAME = 'history_payloads.json'
    TRAINING_DATA_CSV_FILENAME = 'training_data.csv'
    SCORING_DATA_CSV_FILENAME = 'scoring_data.csv'
    FEEDBACK_HISTORY_CSV_FILENAME = 'history_feedback.csv'
    FEEDBACK_CSV_FILENAME = 'feedback_data.csv'
    MRM_EVALUATION_CSV_FILENAME = 'mrm_evaluation_data.csv'
    DEBIAS_HISTORY_FILENAME = 'history_debias.json'
    DEBIASED_PAYLOAD_HISTORY_FILENAME = 'history_debiased_payloads.json'
    QUALITY_MONITOR_HISTORY_FILENAME = 'history_quality_monitor.json'
    MANUAL_LABELING_HISTORY_FILENAME = 'history_manual_labeling.json'
    PERFORMANCE_HISTORY_FILENAME = 'history_performance.json'
    EXPLAIN_HISTORY_FILENAME = 'history_explanations.json'
    DRIFT_ANNOTATIONS_HISTORY_FILENAME = 'history_drift_annotations.json'
    DRIFT_MEASUREMENT_HISTORY_FILENAME = 'history_drift_measurement.json'
    TOKENIZER_PICKLE_FILENAME = 'tokenizer.pickle'

    def __init__(self, name, args, model_instances=1):
        self._args = args
        self.name = name
        if model_instances > 1:
            self.name += str(model_instances)

        cwd = os.path.dirname(__file__)
        if self._args.custom_model_directory:
            self._model_dir = self._args.custom_model_directory
        elif self._args.mrm and 'PreProd' in self.name:
            self._model_dir = get_path(cwd, [cwd, name.split('PreProd')[0]])
        elif self._args.mrm and 'Challenger' in self.name:
            self._model_dir = get_path(cwd, [cwd, name.split('Challenger')[0]])
        else:
            self._model_dir = get_path(cwd, [cwd, name])

        env_name = '' if self._args.env_dict['name'] == 'YPPROD' else self._args.env_dict['name']

        # model create and deploy
        self.metadata = {}
        if self._args.custom_model: # don't add env to model name if this is a custom model
            self.metadata['model_name'] = self.name
        else:
            self.metadata['model_name'] = self.name + env_name
        
        if "Challenger" not in self.name:
            # Checking for spark version support based on environment
            model_meta_filename = "{}/{}".format(WML_SPARK_VERSION_SUPPORT_MAPPING[self._args.environment], Model.MODEL_META_FILENAME)
            model_content_filename = "{}/{}".format(WML_SPARK_VERSION_SUPPORT_MAPPING[self._args.environment], Model.MODEL_CONTENT_FILENAME)
        else:
            # Checking for Python version support based on environment
            model_meta_filename = "{}/{}".format(WML_CHALLENGER_ENVIRONMENT_MAPPING[self._args.environment], Model.MODEL_META_FILENAME)
            model_content_filename = "{}/{}".format(WML_CHALLENGER_ENVIRONMENT_MAPPING[self._args.environment], Model.MODEL_CONTENT_FILENAME)
        
        self.metadata['model_metadata_file'] = self._get_file_path(model_meta_filename)
        self.metadata['model_file'] = self._get_file_path(model_content_filename)
        self.metadata['pipeline_metadata_file'] = self._get_file_path(Model.PIPELINE_META_FILENAME)
        self.metadata['pipeline_file'] = self._get_file_path(Model.PIPELINE_CONTENT_FILENAME)
        if self._args.deployment_name: # if this is an existing deployment use the name provided
            self.metadata['deployment_name'] = self._args.deployment_name
        elif self._args.custom_model: # don't add env to deployment name if this is a custom model
            self.metadata['deployment_name'] = self.name
        else:
            self.metadata['deployment_name'] = self.name + env_name
        self.metadata['deployment_description'] = 'Created by Watson OpenScale Express Path.'

        # configuration
        configuration_file = self._get_file_path(Model.CONFIGURATION_FILENAME)
        if configuration_file:
            self.configuration_data = jsonFileToDict(configuration_file)
        else:
            error_msg = 'ERROR: Unable to find configuration file for this model: {}'.format(Model.CONFIGURATION_FILENAME)
            logger.log_error(error_msg)
            raise Exception(error_msg)

        # training data
        training_data_statistics_file = self._get_file_path(Model.TRAINING_DATA_STATISTICS_FILENAME)
        self.training_data_csv_file = self._get_file_path(Model.TRAINING_DATA_CSV_FILENAME)
        training_data_type = self._get_training_data_type()
        self.training_data_reference = None
        self.training_data = None
        self.training_data_statistics = None
        self.is_unstructured_text = False
        self.is_unstructured_image = False
        if 'training_data_reference' in self.configuration_data:
            logger.log_info('Read model training data from IBM Cloud Object Storage')
            self.training_data_reference = self.configuration_data['training_data_reference']
            first_line_header = True if self.training_data_reference['firstlineheader'] == 'true' else False
            self.training_data_reference['cos_storage_reference'] = BluemixCloudObjectStorageReference(
                self.training_data_reference['credentials'],
                self.training_data_reference['path'],
                first_line_header=first_line_header)
            cos = CloudObjectStorage(self.training_data_reference['credentials'])
            training_data_csv = cos.get_file(self.training_data_reference['path'])
            self.training_data = pd.read_csv(StringIO(training_data_csv), dtype=training_data_type)
        elif training_data_statistics_file:
            self.training_data_statistics = jsonFileToDict(training_data_statistics_file)
            if self.training_data_csv_file:
                self.training_data = pd.read_csv(self.training_data_csv_file, dtype=training_data_type)
            else:
                error_msg = 'ERROR: training_data.csv required with training_data_statistics.json'
                logger.log_error(error_msg)
                raise Exception(error_msg)
        elif self.training_data_csv_file:
            if self.configuration_data['asset_metadata']['input_data_type'] == 'UNSTRUCTURED_TEXT':
                self.is_unstructured_text = True
                pickle_file_path = self._get_file_path(Model.TOKENIZER_PICKLE_FILENAME)
                self.tokenizer = load_pickle_file(pickle_file_path)
                data, labels = split_lines(read_lines(self.training_data_csv_file))
                self.training_data = [data, labels]
            elif self.configuration_data['asset_metadata']['input_data_type'] == 'UNSTRUCTURED_IMAGE':
                self.is_unstructured_image = True
                self.training_data = pd.read_csv(self.training_data_csv_file, dtype=training_data_type)
            else:
                error_msg='ERROR: training_data.csv required for image models'
                logger.log_error(error_msg)
                raise Exception(error_msg)
        else:
            error_msg='ERROR: Unable to find training data'
            logger.log_error(error_msg)
            raise Exception(error_msg)

        # scoring data - uses same dtype as training data
        self.scoring_data = None
        scoring_data_file = self._get_file_path(Model.SCORING_DATA_CSV_FILENAME)
        if scoring_data_file and not self._args.skip_scoring_data:
            self.scoring_data = pd.read_csv(scoring_data_file, dtype=training_data_type)
        else:
            self.scoring_data = self.training_data

        # refactor scoring data for use by online scoring
        self.scoring_data_columns = {}
        if self.is_unstructured_text:
            pass
        else:
            for column_name in self.scoring_data.columns:
                column = []
                for values in self.scoring_data[column_name]:
                    column.append(values)
                self.scoring_data_columns[column_name] = column

        # feedback history - uses same dtype as training data
        self.feedback_history = None
        feedback_history_file = self._get_file_path(Model.FEEDBACK_HISTORY_CSV_FILENAME)
        if feedback_history_file:
            self.feedback_history = pd.read_csv(feedback_history_file, dtype=training_data_type).to_dict('records') # make a list-style DICT

        # feedback data - uses same dtype as training data
        self.feedback_data = None
        feedback_file = self._get_file_path(Model.FEEDBACK_CSV_FILENAME)
        if feedback_file:
            if self.is_unstructured_text:
                self.feedback_data = []
                with open(feedback_file) as f:
                    lines = f.read().splitlines()
                data, labels = split_lines(lines)
                data_list = format_scoring_input(data, self.tokenizer)
                for i in range(0, len(data_list)):
                    self.feedback_data.append([data_list[i], [int(labels[i])]])
            else:
                self.feedback_data = pd.read_csv(feedback_file, dtype=training_data_type).to_dict('records') # make a list-style DICT

        # MRM evaluation data
        self.mrm_evaluation_data = None
        mrm_evaluation_data_file = self._get_file_path(Model.MRM_EVALUATION_CSV_FILENAME)
        if self._args.mrm and mrm_evaluation_data_file:
            with open(mrm_evaluation_data_file) as file:
                f = file.read()
                self.mrm_evaluation_data = bytes(bytearray(f, 'utf-8'))

        # initialize count of historical payload table rows
        self.historical_payload_row_count = 0
        self.expected_payload_row_count = 'unknown'

    def _get_training_data_type(self):
        training_data_type = None
        if 'training_data_type' in self.configuration_data:
            training_data_type = {}
            for key in self.configuration_data['training_data_type'].keys():
                if self.configuration_data['training_data_type'][key] == 'int':
                    training_data_type[key] = int
                elif self.configuration_data['training_data_type'][key] == 'float':
                    training_data_type[key] = float
        return training_data_type

    def _get_bkpi_payload_data_type(self):
        bkpi_payload_data_type = None
        if 'businesskpi_configuration' in self.configuration_data and 'bkpi_payload_data_type' in self.configuration_data['businesskpi_configuration']:
            config_bkpi_payload_data_type = self.configuration_data['businesskpi_configuration']['bkpi_payload_data_type']
            bkpi_payload_data_type = {}
            for key in config_bkpi_payload_data_type.keys():
                if config_bkpi_payload_data_type[key] == 'int':
                    bkpi_payload_data_type[key] = int
                elif config_bkpi_payload_data_type[key] == 'float':
                    bkpi_payload_data_type[key] = float
        return bkpi_payload_data_type

    def _get_file_path(self, filename):
        """
        Returns the path for the file for the current serve engine, else the common file
        Eg. /path/to/sagemaker/training_data_statistics.json OR /path/to/training_data_statistics.json OR None
        """
        if self._args.mrm and 'Challenger' in self.name:
            engine_specific_path = get_path(self._model_dir, [self._model_dir, self._args.ml_engine_type.name.lower(), 'mrm', filename])
            if Path(engine_specific_path).is_file():
                return engine_specific_path
            else:
                return None

        engine_specific_path = get_path(self._model_dir, [self._model_dir, self._args.ml_engine_type.name.lower()])
        if self._args.ml_engine_type is MLEngineType.WML:
            api_version = 'v4' if self._args.v4 else 'v3'
            engine_specific_path = get_path(engine_specific_path, [engine_specific_path, api_version, filename])
        if Path(engine_specific_path).is_file():
            return engine_specific_path
        else:
            engine_specific_path = get_path(self._model_dir, [self._model_dir, self._args.ml_engine_type.name.lower(), filename])
        if Path(engine_specific_path).is_file():
            return engine_specific_path
        else:
            path = get_path(self._model_dir, [self._model_dir, filename])
            if Path(path).is_file():
                return path
        return None

    def _get_score_time(self, day, hour):
        return datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1)))

    # return an array of tuples with datestamp, response_time, and records
    def get_performance_history(self, num_day):
        """
        Retrieves performance history from a json file.
        """
        full_records_list = []
        history_file = self._get_file_path(Model.PERFORMANCE_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                performance_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(performance_values) # wrap around and reuse values if needed
                performance_values[index]["timestamp"] = score_time
                full_records_list.append(performance_values[index])
        return full_records_list

    def get_fairness_history(self, num_day):
        """ Retrieves fairness history from a json file"""
        full_records_list = []
        history_file = self._get_file_path(Model.FAIRNESS_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                fairness_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(fairness_values) # wrap around and reuse values if needed
                fairness_values[index]["timestamp"] = score_time

                fairness_value = fairness_values[index]
                metrics_list = fairness_value["metrics"]
                sources = fairness_value["sources"]
                sources_list = []
                for source in sources:
                    source_id = source["id"]
                    source_type = source["type"]
                    source_data = source["data"]
                    if source_id == "bias_detection_summary":
                        source_data["evaluated_at"] = score_time
                        source_data["favourable_class"] = self.configuration_data["fairness_configuration"]["favourable_classes"]
                        source_data["unfavourable_class"] = self.configuration_data["fairness_configuration"]["unfavourable_classes"]
                        source_data["score_type"] = "disparate impact"
                    sources_list.append(
                        Source(
                            id=source_id,
                            type=source_type,
                            data=source_data
                        )
                    )
                full_records_list.append(MonitorMeasurementRequest(metrics=metrics_list, sources=sources_list, timestamp=score_time))
        return full_records_list

    def get_debias_history(self, num_day):
        """ Retrieves debias history from a json file"""
        full_records_list = []
        history_file = self._get_file_path(Model.DEBIAS_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                debias_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(debias_values) # wrap around and reuse values if needed
                debias_values[index]["timestamp"] = score_time

                debias_value = debias_values[index]
                metrics_list = debias_value["metrics"]
                sources = debias_value["sources"]
                sources_list = []
                for source in sources:
                    sources_list.append(
                        Source(
                            id=source["id"],
                            type=source["type"],
                            data=source["data"]
                        )
                    )
                full_records_list.append(MonitorMeasurementRequest(metrics=metrics_list, sources=sources_list, timestamp=score_time))
        return full_records_list

    def get_quality_monitor_history(self, num_day):
        full_records_list = []
        history_file = self._get_file_path(Model.QUALITY_MONITOR_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                quality_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(quality_values) # wrap around and reuse values if needed
                quality_value = quality_values[index]
                metrics_list = [quality_value["metrics"]]
                source = quality_value["sources"]
                sources_list = [
                    Source(
                        id=source["id"],
                        type=source["type"],
                        data=source["data"]
                    )
                ]
                full_records_list.append(MonitorMeasurementRequest(metrics=metrics_list, sources=sources_list, timestamp=score_time))
        return full_records_list

    def get_manual_labeling_history(self, num_day):
        """
        Retrieves manual labeling history from a JSON file.
        Also returns the non-perturbed records separately for `is_individually_biased` annotation in PL table.
        """
        full_records_list = []
        original_records = [] # Non-perturbed records from PL table
        history_file = self._get_file_path(Model.MANUAL_LABELING_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                manual_labeling_records = json.load(f)
            for record in manual_labeling_records:
                # use fastpath_history_day value to check to see if this manual labeling history record is in the right range
                # if the value is -1, then the file is just one day's records, to be repeated each day
                if record['fastpath_history_day'] == num_day or record['fastpath_history_day'] == -1:
                    # generate the scoring_timestamp value and then remove the fastpath_history_day/hour values
                    hour = record['fastpath_history_hour']
                    record['scoring_timestamp'] = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                    del record['fastpath_history_day']
                    del record['fastpath_history_hour']
                    if not record["perturbed"]:
                        original_records.append(record)
                    full_records_list.append(record)
        return full_records_list, original_records

    def get_explain_history(self):
        full_records_list = []
        history_file = self._get_file_path(Model.EXPLAIN_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                full_records_list = json.load(f)
        return full_records_list

    def get_score_input(self, num_values=1):
        features = None
        values = []
        if self.is_unstructured_text:
            num_rows = len(self.scoring_data[0])
            random_row = random.randint(0, num_rows - 1)
            values = self.scoring_data[0][random_row]
            values = format_scoring_input([values], self.tokenizer)
        elif self.is_unstructured_image:
            num_rows = len(self.scoring_data)
            random_row = random.randint(0, num_rows - 1)
            values = json.loads(self.scoring_data.iloc[random_row].to_list()[0])
        else:
            num_rows = len(self.scoring_data)
            for value_num in range(num_values):
                value = []
                if self._args.score_sequential:
                    row_number = value_num % num_rows
                else:
                    row_number = random.randint(0, num_rows - 1)
                for field in self.configuration_data['asset_metadata']['feature_columns']:
                    if self._args.score_columns:  # pick from a different random row for each field
                        row_number = random.randint(0, num_rows - 1)
                    value.append(self.scoring_data_columns[field][row_number])
                values.append(value)
        if 'asset_metadata' in self.configuration_data:
            if 'feature_columns' in self.configuration_data['asset_metadata']:
                features = self.configuration_data['asset_metadata']['feature_columns']
        return features, values

    def count_payload_history_rows(self, resp):
        count = 0
        if 'values' in resp: # payload history format for WML, Sagemaker, and Custom engine
            count = len(resp['values'])
        elif 'Results' in resp and 'output1' in resp['Results']: # payload history format for Azure
            count = len(resp['Results']['output1'])
        elif 'rowValues' in resp: # payload history format for SPSS
            count = len(resp['rowValues'])
        self.historical_payload_row_count += count
        return count

    def get_payload_history(self, num_day):
        # There are 3 ways to specify payload history:
        # 1. a set of 'payload_history_N.json' files, each containing a full day of payloads specific to one specific day, to be evenly divided across 24 hours
        # 2. one 'payload_history_day.json' file contains one full day of payloads, to be divided across 24 hours and duplicated every day
        # 3. one 'payload_history.json' file contains one hour of payloads, to be duplicated for every hour of every day
        fullRecordsList = []

        # each 'payload_history_N.json' file contains a full day of payloads specific to this day, to be evenly divided across 24 hours
        history_file = self._get_file_path(Model.PAYLOAD_HISTORY_FILENAME.replace('.json', ('_' + str(num_day) + '.json')))
        if history_file:
            with open(history_file) as f:
                payloads = json.load(f)
                hourly_records = len(payloads) // 24
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        req = payloads[index]['request']
                        resp = payloads[index]['response']
                        count = self.count_payload_history_rows(resp)
                        scoring_id = None
                        if 'scoring_id' in payloads[index]:
                            scoring_id = payloads[index]['scoring_id']
                        response_time = None
                        if 'response_time' in payloads[index]:
                            response_time = payloads[index]['response_time']
                        score_time = str(self._get_score_time(num_day, hour))
                        fullRecordsList.append(PayloadRecord(scoring_id=scoring_id,request=req, response=resp, scoring_timestamp=score_time, response_time=response_time))
                        index += 1
            return fullRecordsList

        # the 'payload_history_day.json' file contains one full day of payloads, to be divided across 24 hours and duplicated every day
        history_file = self._get_file_path(Model.PAYLOAD_HISTORY_FILENAME.replace('.json', '_day.json'))
        if history_file:
            with open(history_file) as f:
                payloads = json.load(f)
                hourly_records = len(payloads) // 24
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        req = payloads[index]['request']
                        resp = payloads[index]['response']
                        self.count_payload_history_rows(resp)
                        scoring_id = None
                        if 'scoring_id' in payloads[index]:
                            scoring_id = payloads[index]['scoring_id']
                        response_time = None
                        if 'response_time' in payloads[index]:
                            response_time = payloads[index]['response_time']
                        score_time = str(self._get_score_time(num_day, hour))
                        fullRecordsList.append(PayloadRecord(scoring_id=scoring_id,request=req, response=resp, scoring_timestamp=score_time, response_time=response_time))
                        index += 1
            return fullRecordsList

        # the 'payload_history.json' file contains one hour of payloads, to be duplicated for every hour of every day
        history_file = self._get_file_path(Model.PAYLOAD_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                payloads = json.load(f)
            for hour in range(24):
                for payload in payloads:
                    req = payload['request']
                    resp = payload['response']
                    self.count_payload_history_rows(resp)
                    scoring_id = None
                    if 'scoring_id' in payload:
                        scoring_id = payload['scoring_id']
                    response_time = None
                    if 'response_time' in payload:
                        response_time = payload['response_time']
                    score_time = str(self._get_score_time(num_day, hour))
                    fullRecordsList.append(PayloadRecord(scoring_id=scoring_id,request=req, response=resp, scoring_timestamp=score_time, response_time=response_time))
            return fullRecordsList

        # no payload history provided
        return fullRecordsList

    def get_debiased_payload_history(self, num_day):
        # each 'history_debiased_payloads_N.json' file contains a full day of payloads specific to this day
        fullRecordsList = []
        history_file = self._get_file_path(Model.DEBIASED_PAYLOAD_HISTORY_FILENAME.replace('.json', ('_' + str(num_day) + '.json')))
        if history_file:
            with open(history_file) as f:
                fullRecordsList = json.load(f)
        return fullRecordsList

    def get_drift_metrics_history(self, num_day):
        # each 'history_drift_annotations_N.json' file contains a full day (8 windows) of drift annotations specific to this day
        drift_annotations = None
        history_file = self._get_file_path(Model.DRIFT_ANNOTATIONS_HISTORY_FILENAME.replace('.json', ('_' + str(num_day) + '.json')))
        if history_file:
            with open(history_file) as f:
                drift_annotations = json.load(f)

        # each 'history_drift_measurement_N.json' file contains a full day (8 windows) of drift measurement specific to this day
        drift_measurement = None
        history_file = self._get_file_path(Model.DRIFT_MEASUREMENT_HISTORY_FILENAME.replace('.json', ('_' + str(num_day) + '.json')))
        if history_file:
            with open(history_file) as f:
                drift_measurement = json.load(f)

        if drift_annotations and drift_measurement:
            return [{ 'drift_annotations': drift_annotations, 'drift_measurement': drift_measurement }]
        else:
            return [] # both files are required for a complete drift history
