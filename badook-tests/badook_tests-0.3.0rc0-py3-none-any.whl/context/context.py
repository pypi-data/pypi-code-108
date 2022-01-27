from badook_tests.dsl.summary import DatasetSummary, Summary
import base64
import json
import logging
import urllib.parse

import click
import cloudpickle

from badook_tests.config import get_config
from badook_tests.context.client import Client
from badook_tests.dsl.checks import Check
from badook_tests.dsl.enums import ComparisonPoint
from badook_tests.dsl.summary import DatasetSummary, Summary

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class BadookContext(object):

    client = None

    def __init__(self, client_id: str, client_secret: str, *, running_in_data_cluster: bool = False):
        config = get_config()
        if running_in_data_cluster:
            base_uri = config.data_cluster_url
        else:
            base_uri = urllib.parse.urljoin(
                config.data_cluster_url, 'orchestrator/')
        self.client = Client(client_id, client_secret, base_uri)
        self.api_client = Client(
            client_id, client_secret, config.management_cluster_url)
        self.dataset_summaries = {}

    def collect(self, data, path=''):
        request_data = json.dumps(data, cls=RequestEncoder)
        logger.debug('Summary data: {}'.format(request_data))
        response = self.client.send_post_request(request_data, path)

        if response['error']:
            raise Exception(
                f"collect summaries - {response['error']['message']}")

    def create_summary(self, name, dataset) -> DatasetSummary:

        dataset_id = self._validate_dataset(dataset)
        dataset_summary = DatasetSummary(self)
        dataset_summary.set_dataset(dataset_id)
        dataset_summary.set_name(name)
        self.dataset_summaries[dataset_summary.name] = {
            'display_name': dataset_summary.display_name,
            'dataset_summary': dataset_summary
        }

        return dataset_summary

    def assert_check(self, check):
        check_data = json.dumps(check, cls=CheckEncoder)
        logger.debug('check data: %s', check_data)
        response = self.client.send_post_request(check_data, 'tests')
        if response['error']:
            raise Exception(f"assert check - {response['error']['message']}")

    def set_project_name(self, name):
        self.project_name = name

    def set_run_id(self, run_id):
        self.run_id = run_id
        for ds in self.dataset_summaries.values():
            ds['dataset_summary'].set_run_id(run_id)
            for summ in ds['dataset_summary'].summaries.values():
                summ.set_run_id(run_id)

    def _validate_dataset(self, dataset):
        response = self.api_client.send_json_post_request(
            {'datasetName': dataset}, 'dataset/validate/name')
        error = response.get('error', False)
        if error:
            click.secho(f"Error: {error['message']}", fg='red', bold=True)
            raise Exception()

        return response['data']['id']  # pylint: disable=E1136


class RequestEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, DatasetSummary):
            x = obj.__dict__.copy()
            x['summaries'] = [self.ser_summaries(
                summ, obj.summaries[summ]) for summ in obj.summaries]
            del x["_ctx"]

            # serializing the user feature functions
            if bool(obj.user_features):
                features = {}
                for feature in obj.user_features:
                    features.update(self.ser_udcs(
                        feature, obj.user_features[feature]))
                x['user_features'] = features

            return x

        if isinstance(obj, ComparisonPoint):
            return str(obj).split(".")[1]
        else:
            return

    def ser_summaries(self, name: str, summ: Summary):
        res = summ.__dict__.copy()
        del res["_ctx"]

        # removing the claculation attribute before serialization
        for clac in summ.user_calculations:
            del res[clac]

        # serializing the user calculation functions
        if bool(summ.user_calculations):
            calcs = {}
            for fn in summ.user_calculations:
                calcs.update(self.ser_udcs(fn, summ.user_calculations[fn]))
            res['user_calculations'] = calcs
        return res

    def ser_udcs(self, name: str, udc):
        res = {}
        res[name] = {'func': base64.encodebytes(
            cloudpickle.dumps(udc['func'], protocol=4)).decode('utf-8'),
            'input_columns': udc['input_columns']
        }
        return res


class CheckEncoder (json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Check):

            # copy.deepcopy(obj.__dict__)
            result = {key: value for key,
                      value in obj.__dict__.items() if key != "_ctx"}
            fn = base64.encodebytes(cloudpickle.dumps(
                obj.check_fn, protocol=4)).decode('utf-8')

            result['from_dataset'] = obj.from_dataset.__dict__

            if hasattr(obj, 'to_dataset'):
                result['to_dataset'] = obj.to_dataset.__dict__

            result['check_fn'] = fn
            return result
        else:
            return
