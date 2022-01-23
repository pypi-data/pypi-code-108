import asyncio
import json
import logging
import signal
import sys
import threading
import unittest

import click
import emoji
import pysher
from badook_tests.config import get_config
from badook_tests.util import Halo

from badook_tests.context import global_context
from badook_tests.context.context import BadookContext

logger = logging.getLogger(__name__)
logger.disabled = True


# Exception classes
class TestFailedError(Exception):
    """Raised when a test execution fails"""
    pass


# classes
class DataTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = get_config()
        DataTestCase.context = BadookContext(
            config.client_id, config.client_secret, running_in_data_cluster=config.running_in_data_cluster)
        #signal.signal(signal.SIGINT, cls.signal_handler)
        loop = asyncio.get_event_loop()

        # run customer's set_up function to create project/dataset summaries
        cls.set_up()

        # try:
        run_mgr = cls.init_run()
        cls.context.run_mgr = run_mgr

        # check if sumarries hase identical display names - get the first one found
        duplicate_names = cls.get_summaries_name_duplication(
            cls.context.dataset_summaries.items())

        if not bool(duplicate_names):
            cls.handle_summaries(run_mgr, loop)
        else:
            names = ', '.join(duplicate_names)
            err_message = f"Summary name/s: {names}, has been found in multiple summaries.\nPlease change to a unique name for each summary and try again."
            logger.error(err_message)
            raise Exception({'message': err_message})

        # except Exception as e:
        #     terminate = cls.handle_exception(e.args[0])

        #     if terminate:
        #         # send "run failed" to mgmt API
        #         cls.send_fail_to_api()
        #         assert False, ""

    @classmethod
    def init_run(cls):
        proj = cls.context.project_name

        # registering a new test run with the badook mgmt API.
        # if this is a rerun-by-id request, then the mgmt API has to "redo" an existing run and delete all data ("RerunFull")
        if global_context.rerun:

            # send request to service manager to update the run with 'rerun'
            response = cls.context.api_client.send_json_post_request(
                {'projectId': proj, 'runType': 'RerunFull',
                 'runId': global_context.run_id}, "runhistory/run")

            if response['error']:
                error_msg = f"Re-Run - {response['error']['message']}"
                logger.error(error_msg)
                raise Exception(error_msg)

            cls.run_id = global_context.run_id

        # not a rerun - the mgmt API returns our new RunID which we'll use for all DS summaries
        else:
            # send request to service manager to create a new "run"
            response = cls.start_run(proj)

            if response['error']:
                error_msg = f"Run - {response['error']['message']}"
                logger.error(error_msg)
                raise Exception(error_msg)

            cls.run_id = response['data']['runId']  # pylint: disable=E1136

        cls.context.set_run_id(cls.run_id)
        cls.channel_id = response['data']['orgId']  # pylint: disable=E1136

        click.secho(
            f'\nrunning project - {proj}, run id: {cls.run_id}', fg='magenta', bold=True)

        res = RunManager(cls.channel_id, cls.run_id)
        return res

    @classmethod
    def start_run(cls, proj):
        '''
        This is a utility method for starting a run with the management API.
        Its main use is to be mocked in tests. You can patch the methods as follows:

        @patch('badook_tests.data_test_case.DataTestCase.start_run', return_value=[the value you want to be returned])
        '''
        return cls.context.api_client.send_json_post_request(
            {'projectId': proj}, "runhistory/run")

    @classmethod
    def set_up(self):
        "Hook method for setting up the test fixture before exercising it."
        pass

    def setUp(self):
        self.context = self.__class__.context
        self.context.test_name = self._testMethodName

        self.__dict__.update(self.context.dataset_summaries)
        self.run_id = self.__class__.run_id
        self.org_id = self.__class__.channel_id

    @classmethod
    def handle_summaries(cls, run_mgr, loop):

        futures = []
        for name, item in cls.context.dataset_summaries.items():
            display_name = item['display_name']
            ds = item['dataset_summary']

            if global_context.rerun:
                # this means we want to rerun a specific batch that's already run with this run_id for this dataset.

                # get batch data correspondence to main dataset and join-on if exists by run id
                response = cls.get_batch_data_by_run_id(
                    ds, global_context.run_id)

                request_data = {
                    'rerun': True,
                    'project_id': cls.context.project_name,
                    'run_id': [global_context.run_id]
                }
                del_response = cls.context.client.send_json_delete_request(
                    request_data, path=f'run')

                if del_response['error']:
                    raise Exception(del_response['error']['message'])

            else:
                # get latest batched data correspondence to main dataset and join-on if exists
                response = cls.get_next_unexecuted_batch_data(ds)

            if not response['error']:
                main_ds_batch = cls.handle_get_batch_data_response(
                    ds, response)
                text = f'{display_name} on batch {main_ds_batch}' if main_ds_batch else display_name

                if global_context.rerun:
                    batch_name = f' {main_ds_batch}' if main_ds_batch else 'es'
                    print(f're-running batch{batch_name}\n')

                futures.append(asyncio.ensure_future(
                    run_mgr.add_execution(f'collecting dataset: {text}', name)))

                if global_context.force_pull:
                    ds.force_pull = True
            else:
                err_message = f"Batches - {response['error']['message']}"
                logger.error(err_message)
                raise Exception({'message': err_message})

            ds.set_project_id(cls.context.project_name)
            ds.set_run_id(cls.run_id)
            ds.collect()

        # this gathers all the dataset futures into a *concurrent* future so they'd run at the same time
        dataset_futures = asyncio.gather(*futures)

        # this calls the runloop with a function that waits on the parallel futures and the error future for the first to complete
        loop.run_until_complete(run_mgr.run_summaries([asyncio.ensure_future(
            run_mgr.add_error_execution()), dataset_futures]))

        super().run

    @classmethod
    def get_summaries_name_duplication(cls, summaryList):
        def get_display_name(obj):
            (_, item) = obj
            return item['display_name']

        duplicate_names = []
        display_name_list = list(
            map(lambda obj: get_display_name(obj), summaryList))

        for display_name in display_name_list:
            if (display_name_list.count(display_name) > 1) and not (duplicate_names.__contains__(display_name)):
                duplicate_names.append(display_name)

        return_list = list(map(lambda name: f'"{name}"', duplicate_names))
        return return_list

    @classmethod
    def get_next_unexecuted_batch_data(cls, ds):
        # this service will get last batch file for each dataset (in case there also join-on datasets)
        """
        example:
        ret_response = {
            error: {'message': '', 'user': False}
            data = {
                dataset : {
                    name: <dataset>,
                    batch_value: <batch>,
                }
                join-on : [{
                    name: <dataset1>,
                    batch_value: <batch>
                },{
                    name: <dataset2>,
                    batch_value: <batch>
                }]
                ...
            }
        }
        """
        data = {}
        project_id = cls.context.project_name

        # get all dataset names that need to extract their batches list
        dataset_ids = [ds.dataset]  # main dataset

        # add additional datasets if exist in join-on
        if len(ds.joined_datasets) > 0:
            for key in ds.joined_datasets:
                dataset_ids.append(key)

        # get batches list for each dataset
        for dataset_id in dataset_ids:
            path = f'batch/{cls.channel_id}/{dataset_id}/{project_id}'
            response = cls.context.client.send_get_request(path=path)

            if not response['error']:
                batch = None
                if response['data'] is not None:
                    batch = cls.get_latest_batch(response['data'])
                data[dataset_id] = {'batch_value': batch}
            else:
                # stop the loop and return with the current error response
                return response

        return {'data': cls.convert_batch_data_to_response_data(data), 'error': False}

    @classmethod
    def get_batch_data_by_run_id(cls, ds, run_id):
        # this service will get specific run batch file for each dataset (in case there also join-on datasets)
        """
        example:
        ret_response = {
            error: {'message': '', 'user': False}
            data = {
                dataset : {
                    name: <dataset>,
                    batch_value: <batch>,
                }
                join-on : [{
                    name: <dataset1>,
                    batch_value: <batch>
                },{
                    name: <dataset2>,
                    batch_value: <batch>
                }]
                ...
            }
        }
        """
        data = {}
        project_id = cls.context.project_name

        # get all dataset names that need to extract their batches list
        dataset_ids = [ds.dataset]  # main dataset

        # add additional datasets if exist in join-on
        if len(ds.joined_datasets) > 0:
            for key in ds.joined_datasets:
                dataset_ids.append(key)

        # get batches list for each dataset
        for dataset_id in dataset_ids:

            # dig up the batch name by run id
            path = f'batch/{cls.channel_id}/{dataset_id}/{project_id}/{run_id}'
            response = cls.context.client.send_get_request(path=path)

            if not response['error']:
                batch = None

                # if readBatch flag is False the response will return False (which doesn't have 'get')
                if isinstance(response['data'], dict):
                    batch = response['data'].get('batch_value', None)
                data[dataset_id] = {'batch_value': batch}
            else:
                # stop the loop and return with the current error response
                err_message = f"Batch by run id - {response['error']['message']}"
                raise Exception(err_message)
                # return response

        return {'data': cls.convert_batch_data_to_response_data(data), 'error': False}

    @classmethod
    def handle_get_batch_data_response(cls, ds, response):

        data = response['data']
        main_ds_batch = data['dataset']['batch_value']  # main dataset batch

        # if there is a batch to run, add "batch_value" field in ds
        if main_ds_batch:
            ds.set_batch(main_ds_batch)

        if data['join_on']:
            for item_data in data['join_on']:
                item_data_name = item_data['name']
                item_data_batch = item_data['batch_value']

                # if there is a batch to run, add "batch_value" field in ds
                if item_data_batch:
                    ds.joined_datasets[item_data_name]['batch_value'] = item_data['batch_value']

        return main_ds_batch

    @classmethod
    def get_latest_batch(cls, data):

        # sort batches by created date
        content = sorted(data, key=lambda item: item['created_date'])

        batches = [b for b in content if b['batch_value']]
        batch = batches.pop(0)['batch_value'] if batches else None
        return batch

    @classmethod
    def convert_batch_data_to_response_data(self, data):
        """
        data:
            dataset1: {batch_value} -> main batch
            dataset2: {batch_value} -> join-on batch
            dataset3: {batch_value} -> join-on batch
            ....

        response_data:{
              data = {
                dataset : {
                    name: <dataset>,
                    batch_value: <batch>,
                }
                join-on : [{
                    name: <dataset1>,
                    batch_value: <batch>
                },{
                    name: <dataset2>,
                    batch_value: <batch>
                }]
                ...
            }
        }
        """
        response_data = {}
        if len(data) > 0:
            response_data['join_on'] = []

        for index, key in enumerate(data, start=0):
            data_item = {'name': key, 'batch_value': data[key]['batch_value']}

            # main dataset
            if index == 0:
                response_data['dataset'] = data_item

            # join-on datasets
            else:
                response_data['join_on'].append(data_item)

        return response_data

    @classmethod
    def tearDownClass(cls):
        data = {"orgId": cls.channel_id,
                "projectId": cls.context.project_name, "runId": cls.run_id}
        cls.context.api_client.send_json_post_request(
            data, "runhistory/run/end")

    # @classmethod
    # def signal_handler(cls, sig, frame):
    #     click.secho(emoji.emojize(
    #         '\n\nOh, no! You have aborted the tests! :scream:', use_aliases=True), fg='red', bold=True)

    #     cls.send_fail_to_api()
    #     sys.exit(0)

    @classmethod
    def send_fail_to_api(cls):
        data = {"orgId": cls.channel_id, "projectId": cls.context.project_name,
                "runId": cls.run_id, "status": "Failure"}
        cls.context.api_client.send_json_post_request(
            data, "runhistory/run/end")

    @classmethod
    def handle_exception(cls, error):
        # exception can be either plain text or a dict {'message': text}
        # plain text will be displayed with the generic error notice, and
        # the dict's message will be displayed on it's own.
        generic = True
        terminate = True
        msg = error

        # check if argument is a dict type
        if isinstance(error, dict):
            # check if it has a 'message' element
            msg = error.get('message', None)
            terminate = error.get('terminate', True)
            if msg is not None:
                generic = False

        if (generic):
            click.secho(
                f'\nUh Oh! Something bad happened while trying to run the test. Please contact Badook support.\n({msg})',
                fg='red', bold=True)
        else:
            click.secho(
                f'\n{msg}\n', fg='red', bold=True)

        return terminate


class RunManager(object):

    def __init__(self, channel_id, run_id) -> None:
        root = logging.getLogger('pysher.connection')
        root.disabled = True

        self._channel_id = channel_id
        self._run_id = run_id
        self.pusher = pysher.Pusher('515d671ab968b85e463a', cluster='ap1')
        self.pusher.connection.bind(
            'pusher:connection_established', self.pysher_connection)

        self.pusher.connect()

        self._lock = threading.Lock()
        self.loop = asyncio.get_event_loop()
        self._events = {}
        self._error_event = {}

    # waits for the first future to complete and then goes over the result to make sure exceptions are thrown
    async def run_summaries(self, futures):
        (done, _) = await asyncio.wait(futures, return_when='FIRST_COMPLETED')
        for t in done:
            t.result()

    def summary_event_handler(self, data):
        event_data = json.loads(data)
        dataset_name = event_data['dataset_summary']
        result = event_data['status']
        error = event_data.get('error', False)

        if dataset_name:
            event = self._events.get(dataset_name, False)
            if event:
                event['result'] = result
                event['error'] = event_data.get('error', False)
                event['warning'] = event_data.get('warning', False)
                self.loop.call_soon_threadsafe(event['event'].set)

        elif result == 'Failure' and error and not dataset_name:
            # meaning the error occured before could identify which dataset it is
            # therefore, terminate the whole process
            raise Exception(error)

    def test_event_handler(self, data):
        check_data = json.loads(data)

        # in case the event hasn't been added to self._events yet
        check_id = check_data['check_id']
        event = self._events.get(check_id, False)

        if event:
            event['result'] = check_data['status']
            event['error_message'] = check_data['error_message']
            self.loop.call_soon_threadsafe(event['event'].set)

    def error_event_handler(self, data):
        # This error event is called to close the whole run proccess
        error_data = json.loads(data)

        # get list of all running datasets events
        running_datasets = self._events.keys()

        # loop on all current events and set to close them with Failure
        for dataset in running_datasets:
            event = self._events[dataset]
            event['result'] = 'Failure'
            self.loop.call_soon_threadsafe(event['event'].set)

        # set error event with error message
        error_message = 'Badook backend error'

        if error_data['error_message']:
            error_message = error_data['error_message']

        self._error_event['error_message'] = error_message
        self.loop.call_soon_threadsafe(self._error_event['event'].set)

    def get_error_in_event(self, error):
        error_message = 'Badook backend error'
        error_type = error['error_type']

        if error_type and error_type.lower() == 'user':
            error_message = {'message': error['error_message']}
            error_message['terminate'] = error['terminate']

        return error_message

    def pysher_connection(self, data):
        channel = self.pusher.subscribe(f'badook-{self._channel_id}')
        channel.bind(f'{self._run_id}-summary', self.summary_event_handler)
        channel.bind(f'{self._run_id}-test', self.test_event_handler)
        channel.bind(f'{self._run_id}-error', self.error_event_handler)

    async def add_execution(self, msg: str, id: str) -> None:
        ev = self.create_event(id)
        await self.print_summary_execution(msg, ev)

    async def add_error_execution(self) -> None:
        self._error_event['event'] = asyncio.Event()
        await self._error_event['event'].wait()
        raise Exception(self._error_event['error_message'])

    def add_waiting_execution(self, msg: str, id: str, spinner='circleQuarters', color='cyan') -> None:
        ev = self.create_event(f'{id}')
        self.loop.run_until_complete(self.print_test_execution(msg, ev))

    async def print_test_execution(self, msg: str, ev, spinner='circleQuarters', color="cyan",
                                   text_color="cyan") -> None:
        with Halo(text=msg, spinner=spinner, color=color, text_color=text_color) as spinner:
            await ev['event'].wait()
            if ev['result'].lower() == 'success':
                spinner.succeed()  # "✔"
            else:
                spinner.fail()  # "✖"
                raise TestFailedError(ev['error_message'])

    async def print_summary_execution(self, msg: str, ev, spinner='dots', color="green", text_color="green") -> None:
        with Halo(text=msg, spinner=spinner, color=color, text_color=text_color) as spinner:
            await ev['event'].wait()
            error = False

            # handle spinner's icons
            if ev['result'].lower() == 'success':
                spinner.succeed()  # "✔"

            else:
                spinner.fail()  # "✖"
                error = ev.get('error', False)

            # if the run has a warning, display it
            if ev['warning']:
                click.secho(
                    f'\nWarnings:\n{ev["warning"]}', fg='yellow', bold=True)

            # if the run has an error, raise an exception
            if error:
                raise Exception(self.get_error_in_event(error))

    def create_event(self, id: str):
        with self._lock:
            self._events[id] = {'event': asyncio.Event()}
            return self._events[id]
