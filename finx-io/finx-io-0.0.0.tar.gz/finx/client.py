#! Python
"""
Author: Jake Mathai, Dick Mule
Purpose: Client classes for exposing the FinX API endpoints
"""
import os
import json
import types
import aiohttp
import asyncio
import requests
import functools
import pandas as pd

from lru import LRU
from uuid import uuid4
from gc import collect
from time import sleep
from io import StringIO
from sys import getsizeof
from threading import Thread
from traceback import format_exc
from urllib.parse import urlparse
from websocket import WebSocketApp, enableTrace


enableTrace(False)

DEFAULT_API_URL = 'https://sandbox.finx.io/api/'


"""
EXAMPLE OF CACHE:
CACHE = {
  # TIER 1 KEYS:
  API_METHOD_W/OUT_SECURITY_ID_PARAM_1: 
    LRU(MAX_SIZE_METHOD) -> {PARAMS_1: CACHED_RESULT_1, ..., PARAMS_MAX_SIZE_METHOD: CACHED_RESULT_MAX_SIZE_METHOD},
  MY_SECURITY_ID:
    SECURITY_REFERENCE:
      LRU(3) -> {
          PARAMS_1: PARAMS_1_REF_DATA,
          PARAMS_2: PARAMS_2_REF_DATA,
          PARAMS_3: PARAMS_3_REF_DATA
        }
    SECURITY_ANALYTICS:
      LRU(3) -> {
          PARAMS_1: PARAMS_1_ANALYTICS,
          PARAMS_2: PARAMS_2_ANALYTICS,
          PARAMS_3: PARAMS_3_ANALYTICS
        }
    SECURITY_CASH_FLOWS: 
      LRU(1) -> {
          LAST_PARAMS: LAST_CF_DATAFRAME
        }
}

f = _SyncFinXClient()
y = f.get_cache_keys('blah', {'security_id': 'hello', 'as_of_date': '20210101'})
f.recall_cache_value(y)

x = f.get_cache_keys('testme', {})
f.recall_cache_value(x)
"""


class Hybrid:

    def __init__(self, func):
        self._func = func
        self._func_name = func.__name__
        self._func_path = func.__name__
        self._func_class = None
        functools.update_wrapper(self, func)

    def __get__(self, obj, objtype):
        """Support instance methods."""
        self._func_class = obj
        return self

    def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return (loop.create_task if loop.is_running() else loop.run_until_complete)(self.run_func(*args, **kwargs))

    async def run_func(self, *args, **kwargs):
        if self._func_class is not None:
            args = (self._func_class,) + args
        return await self._func(*args, **kwargs)

    async def run_async(self, *args, **kwargs):
        return await self.run_func(*args, **kwargs)


class SessionManager:
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *err):
        await self._session.close()
        self._session = None

    async def fetch(self, url, **kwargs):
        async with self._session.post(url, data=kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()


class _FinXClient:

    def __init__(self, **kwargs):
        """
        Client constructor - supports keywords finx_api_key and finx_api_endpoint, or
        FINX_API_KEY and FINX_API_ENDPOINT environment variables
        """
        self.__api_key = kwargs.get('finx_api_key') or os.environ.get('FINX_API_KEY')
        if self.__api_key is None:
            raise Exception('API key not found - please include the keyword argument '
                            'finx_api_key or set the environment variable FINX_API_KEY')
        self.__api_url = kwargs.get('finx_api_endpoint') or os.environ.get('FINX_API_ENDPOINT') or DEFAULT_API_URL
        self.cache_size = kwargs.get('cache_size') or 100000
        self.cache = LRU(self.cache_size)
        self.cache_method_size = dict(security_analytics=3, cash_flows=1, reference_data=3)
        self.timeout = kwargs.get('timeout', 100)
        if not kwargs.get('no_init'):
            self._init_api_functions(**kwargs)

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *err):
        await self._session.close()
        self._session = None

    def get_api_key(self):
        return self.__api_key

    def get_api_url(self):
        return self.__api_url

    def clear_cache(self):
        self.cache.clear()
        collect()
        return None

    def check_cache(self, api_method, security_id=None, params=None):
        params = dict() if params is None else params
        as_of_date = params.get('as_of_date')
        cache_key = f'{f"{security_id}:{as_of_date}:" if security_id else ""}{api_method}'
        params_key = ','.join(
            [f'{key}:{params[key]}' for key in sorted(params.keys())
             if key not in ['security_id', 'as_of_date', 'api_method', 'input_file', 'output_file', 'block']])
        params_key = params_key if len(params_key) > 0 else 'NONE'
        cached_value = self.cache.get(cache_key, dict()).get(params_key)
        if cached_value is None:
            self.cache[cache_key] = LRU(1) if security_id is None else LRU(self.cache_method_size.get(api_method, 1))
            self.cache[cache_key][params_key] = None
        return cached_value, cache_key, params_key

    def _init_api_functions(self, **kwargs):
        """
        Add all valid API Methods to Class
        """
        all_functions = self._dispatch('list_api_functions', **kwargs)
        all_functions = all_functions['data'] if isinstance(all_functions, dict) else all_functions
        batch_inputs = 'batch_params=None, input_file=None, output_file=None, '
        batch_params = 'batch_params=batch_params, input_file=input_file, output_file=output_file, '
        for function in all_functions:
            name, required, optional = [function[k] for k in ["name", "required", "optional"]]
            required_str = (", ".join(required) + ", ") if len(required) > 0 else ""
            optional_str = (", ".join([f'{k}={v}' for k, v in optional.items()]) + ", ") if optional is not None else ""
            required_zip = (", ".join([f"{x}={x}" for x in required]) + ", ") if len(required) > 0 else ""
            optional_zip = (", ".join([f"{x}={x}" for x in optional.keys()]) + ", ") if optional is not None else ""
            for index, batch in enumerate(["batch_", ""]):
                inputs = [batch_inputs, f"{required_str}{optional_str}"][index]
                params = [batch_params, f"{required_zip}{optional_zip}"][index]
                # print(f'def {batch}{name}(self, {inputs}**kwargs):\n'
                #       f'    return self._{batch}dispatch("{f"{name}"}", {params}**kwargs)')
                exec(f'def {batch}{name}(self, {inputs}**kwargs):\n'
                     f'    return self._{batch}dispatch("{f"{name}"}", {params}**kwargs)',
                     locals())
                self.__dict__[f'{batch}{name}'] = types.MethodType(locals()[f'{batch}{name}'], self)

    @Hybrid
    async def _dispatch(self, api_method, **kwargs):
        """
        Abstract request dispatch function
        """
        request_body = {
            'finx_api_key': self.__api_key,
            'api_method': api_method,
        }
        if any(kwargs):
            request_body.update({
                key: value for key, value in kwargs.items()
                if key != 'finx_api_key' and key != 'api_method'
            })
        cached_response, cache_key, params_key = self.check_cache(api_method, kwargs.get('security_id'), request_body)
        if cached_response is not None:
            print('Found in cache')
            return cached_response
        async with SessionManager() as session:
            data = await session.fetch(self.__api_url, **request_body)
            error = data.get('error')
            if error is not None:
                print(f'API returned error: {error}')
                return error
            self.cache[cache_key] = data
            return data

    async def _dispatch_batch(self, api_method, security_params, **kwargs):
        """
        Abstract batch request dispatch function. Issues a request for each input
        """
        assert api_method != 'list_api_functions' \
               and type(security_params) is list \
               and len(security_params) < 100
        try:
            asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        tasks = [self._dispatch(api_method, **security_param, **kwargs) for security_param in security_params]
        return await asyncio.gather(*tasks)


class _WebSocket(WebSocketApp):

    def is_connected(self):
        return self.sock is not None and self.sock.connected


class _SocketFinXClient(_FinXClient):

    def __init__(self, **kwargs):
        """
        Client constructor - supports keywords finx_api_key and finx_api_endpoint,
        or FINX_API_KEY and FINX_API_ENDPOINT environment variables
        """
        super().__init__(**kwargs, no_init=True)
        self.__api_key = super().get_api_key()
        self.__api_url = super().get_api_url()
        self.ssl = kwargs.get('ssl', False)
        self.is_authenticated = False
        self.blocking = kwargs.get('blocking', True)
        self._init_socket()
        _FinXClient._init_api_functions(self, **kwargs)

    def authenticate(self):
        print('Authenticating...')
        self._socket.send(json.dumps({'finx_api_key': self.__api_key}))

    def _get_size(self, obj, seen=None):
        """Recursively finds size of objects"""
        size = getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self._get_size(v, seen) for v in obj.values()])
            size += sum([self._get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += self._get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self._get_size(i, seen) for i in obj])
        return size

    def _run_socket(self, url, on_message, on_error):
        """
        Spawn websocket connection in daemon thread
        """
        try:
            self._socket = _WebSocket(
                url,
                on_open=lambda s: self.authenticate(),
                on_message=on_message,
                on_error=on_error,
                on_close=lambda s: print('Socket closed'))
            self._socket_thread = Thread(
                target=self._socket.run_forever,
                daemon=True,
                kwargs={'skip_utf8_validation': True, 'sslopt': {'check_hostname': False}})
            self._socket_thread.start()
        except Exception as e:
            raise Exception(f'Failed to connect to {url}: {e}')

    def _init_socket(self):
        """
        Define websocket connection with callbacks and run as daemon process
        """
        self.is_authenticated = False

        def on_message(socket, message):
            try:
                # print(f'RECEIVED MESSAGE: {message}')
                message = json.loads(message)
                if message.get('is_authenticated'):
                    print('Successfully authenticated')
                    self.is_authenticated = True
                    return None
                error = message.get('error')
                if error is not None:
                    print(f'API returned error: {error}')
                    data = error
                else:
                    data = message.get('data', message.get('message', {}))
                if type(data) is not list and (type(data) is not dict or data.get('progress') is not None):
                    print(message)
                    return None
                cache_keys = message.get('cache_key')
                if cache_keys is None:
                    return None
                return_iterable = type(data) is list and type(data[0]) is dict
                for key in cache_keys:
                    value = next(
                        (item for item in data if item.get("security_id", '') in key[1]),
                        None) if return_iterable and key[0] is not None else data
                    self.cache[key[1]][key[2]] = value
            except:
                print(f'Socket on_message error: {format_exc()}, {message}')
            return None

        def on_error(socket, error):
            print(f'Socket on_error: {error}')
            if not socket.is_connected():
                self._init_socket()

        url = f'{"wss" if self.ssl else "ws"}://{urlparse(self.__api_url).netloc}/ws/api/'
        print(f'Connecting to {url}')
        self._run_socket(url, on_message, on_error)

    def _download_file(self, file_result):
        response = requests.get(
            self.__api_url + 'api/batch-download/',
            params={
                'filename': file_result['filename'],
                'bucket_name': file_result.get('bucket_name')}).content.decode('utf-8')
        if file_result.get('is_json'):
            response = json.loads(response)
        else:
            response = pd.read_csv(StringIO(response), engine='python')
        return response

    def _listen_for_results(self, cache_keys, callback=None, **kwargs):
        """
        Async threadpool process listening for result of a request and execute callback upon arrival. Only used
        if callback specified in a function call
        """
        try:
            remaining_keys = cache_keys
            while len(remaining_keys) != 0:
                sleep(0.01)
                remaining_results = [self.cache.get(key[1], dict()).get(key[2], None) for key in remaining_keys]
                remaining_keys = [remaining_keys[i] for i, value in enumerate(remaining_results) if value is None]
            file_results = []
            results = [self.cache.get(key[1], dict()).get(key[2], None) for key in cache_keys]
            for i, result in enumerate(results):
                if not isinstance(result, dict):
                    continue
                if result.get('filename'):
                    file_results += [[i, result]]
            if len(file_results) > 0:
                print('Downloading results...')
                files_to_download = [
                    dict(s) for s in set(
                        frozenset(d.items())
                        for d in list(map(lambda x: x[1], file_results)))]
                downloaded_files = dict()
                for file in files_to_download:
                    downloaded_files[file['filename']] = self._download_file(file)
                for index, file_result in file_results:
                    file_df = downloaded_files[file_result['filename']]
                    if 'cache_key' in file_df:
                        matched_result = file_df.loc[
                            file_df['cache_key'].map(lambda x: json.loads(x) == list(cache_keys[index]))
                        ].to_dict(orient='records')[0]
                    else:
                        matched_result = file_df
                    if 'filename' in matched_result:
                        matched_result['result'] = self._download_file(matched_result)
                        matched_result = {k: matched_result[k] for k in ['security_id', 'result', 'cache_key']}
                    self.cache[cache_keys[index][1]][cache_keys[index][2]] = matched_result
                    results[index] = matched_result
            output_file = kwargs.get('output_file')
            if output_file is not None and len(results) > 0 and type(results[0]) in [list, dict]:
                print(f'Writing data to {output_file}')
                pd.DataFrame(results).to_csv(output_file, index=False)
            if callable(callback):
                return callback(results, **kwargs, cache_keys=cache_keys)
            return results if len(results) > 1 else results[0] if len(results) > 0 else results
        except:
            print(f'Failed to find result/execute callback: {format_exc()}')

    def _parse_batch_input(self, batch_input, base_cache_payload):
        """
        Extract batch input data from either direct input or csv/txt file. Sends to server as a file if large
        """
        print('Parsing batch input...')
        batch_input_df = (pd.read_csv if type(batch_input) is str else pd.DataFrame)(batch_input)
        batch_input_df['cache_keys'] = [
            self.check_cache(
                base_cache_payload['api_method'],
                security_input.get('security_id'),
                {**base_cache_payload, **security_input})
            for security_input in batch_input_df.to_dict(orient='records')]
        batch_input_df['cached_responses'] = batch_input_df['cache_keys'].map(lambda x: x[0])
        cache_keys = batch_input_df['cache_keys'].tolist()
        cached_responses = batch_input_df.loc[
            batch_input_df['cached_responses'].notnull()]['cached_responses'].tolist()
        outstanding_requests = batch_input_df.loc[batch_input_df['cached_responses'].isnull()]
        return cache_keys, cached_responses, outstanding_requests.to_dict(orient='records')

    def _upload_batch_file(self, batch_input):
        """
        Send batch input file to server for later retrieval in dispatch on server side
        """
        print('Uploading batch file...')
        filename = f'{uuid4()}.csv'
        if type(batch_input) in [pd.DataFrame, pd.Series]:
            batch_input.to_csv(filename, index=False)
        elif type(batch_input) is list:
            if type(batch_input[0]) in [dict, list]:
                request_dicts = [x.get("request") for x in batch_input if type(x) == dict]
                request_dicts = [x for x in request_dicts if x]
                if request_dicts:
                    with open(filename, 'w+') as file:
                        file.write('\n'.join(request_dicts))
                    file.close()
                    print("MADE BATCH FILE")
                else:
                    pd.DataFrame(batch_input).to_csv(filename, index=False)
            elif type(batch_input[0]) is str:
                with open(filename, 'w+') as file:
                    file.write('\n'.join(batch_input))
        file = open(filename, 'rb')
        response = requests.post(  # Upload file to server and record filename
            self.__api_url + 'batch-upload/',
            data={'finx_api_key': self.__api_key, 'filename': filename},
            files={'file': file})
        try:
            response = response.json()
        except:
            response = dict(failed=response.text)
        file.close()
        os.remove(filename)
        if response.get('failed'):
            raise Exception(f'Failed to upload file: {response["message"]}')
        print('Batch file uploaded')
        return response.get('filename', filename)

    def _dispatch(self, api_method, **kwargs):
        """
        Abstract API dispatch function
        """
        if not self._socket.is_connected():
            print('Socket is not connected - reconnecting...')
            self._init_socket()
        if not self.is_authenticated:
            print('Awaiting authentication...')
            i = 5000
            while not self.is_authenticated and i >= 1:
                sleep(.001)
                i -= 1
            if not self.is_authenticated:
                raise Exception('Client not authenticated')
        payload = {'api_method': api_method}
        callback = kwargs.pop('callback', None)
        if any(kwargs):
            payload.update({
                key: value for key, value in kwargs.items()
                if key != 'finx_api_key' and key != 'api_method'
            })
        payload_size = self._get_size(payload)
        chunk_payload = payload_size > 1e5
        is_batch = kwargs.pop('is_batch', False)
        # print(f"payload size {payload_size}, need to chunk payload: {chunk_payload}")
        if is_batch or chunk_payload:
            batch_input = kwargs.pop('batch_input', None)
            base_cache_payload = kwargs.copy()
            base_cache_payload['api_method'] = api_method
            if not chunk_payload:
                cache_keys, cached_responses, outstanding_requests = self._parse_batch_input(
                    batch_input,
                    base_cache_payload)
            else:
                cache_keys, cached_responses, outstanding_requests =\
                    [self.check_cache(api_method, payload.get('security_id'), payload)], [], [payload]
                cache_keys[0] = list(cache_keys[0])[:-1] + ["None"]
            total_requests = len(cached_responses) + len(outstanding_requests)
            print(f'total requests = {total_requests}')
            if len(cached_responses) == total_requests:
                print(f'All {total_requests} requests found in cache')
                if callable(callback):
                    return callback(cached_responses, **kwargs, cache_keys=cache_keys)
                return cached_responses
            print(f'{len(cached_responses)} out of {total_requests} requests found in cache')
            if chunk_payload:
                payload['batch_input'] = self._upload_batch_file(outstanding_requests if batch_input else [payload])
            else:
                payload['batch_input'] = outstanding_requests
            payload['api_method'] = 'batch_' + api_method
            payload = {k: v for k, v in payload.items() if k in ['batch_input', 'api_method']}
            payload.update({k: v for k, v in kwargs.items() if k != 'request'})
            payload['run_batch'] = is_batch
        else:
            cache_keys = self.check_cache(
                api_method, payload.get('security_id'), payload)
            if cache_keys[0] is not None:
                print('Request found in cache')
                if callable(callback):
                    return callback(cache_keys[0], **kwargs, cache_keys=cache_keys)
                return cache_keys[0]
            cache_keys = [cache_keys]
        payload['cache_key'] = [x for x in cache_keys if x[0] is None]
        self._socket.send(json.dumps(payload))
        blocking = kwargs.get('blocking', self.blocking)
        if blocking:
            return self._listen_for_results(cache_keys, callback, **kwargs)
        if callable(callback):
            self._executor.submit(self._listen_for_results, cache_keys, callback, **kwargs)
        return cache_keys

    def _batch_dispatch(self, batch_method, batch_params=None, input_file=None, output_file=None, **kwargs):
        """
        Abstract batch request dispatch function. Issues a single request containing all inputs. Must either give the
        inputs directly in security_params or specify absolute path to input_file. Specify the parameters & keywords and
        invoke using the defined batch functions below

        :param security_params: list - List of dicts containing the security_id and keyword arguments for each security
                function invocation. Default None, optional
        :param input_file: string - path to csv/txt file containing parameters for each security, row-wise.
                Default None, optional
        :param output_file: string - path to csv/txt file to output results to, default None, optional
        :keyword callback: callable - function to execute on result once received. Function signature should be:

                        def callback(result, **kwargs): ...

                  If True or not null, uses the generic callback function _batch_callback() defined above.
                  Default None, optional
        :keyword blocking: bool - block main thread until result arrives and return the value.
                  Default is object's configured default, optional
        """
        assert batch_method != 'list_api_functions' and (batch_params or input_file)
        return self._dispatch(
            batch_method,
            batch_input=batch_params or input_file,
            **kwargs,
            input_file=input_file,
            output_file=output_file,
            is_batch=True)


def FinXClient(kind='sync', **kwargs):
    """
    Unified interface to spawn FinX client. Use keyword "kind" to specify the type of client

    :param kind: string - 'socket' for websocket client, 'async' for async client. Default 'sync', optional
    """
    return _SocketFinXClient(**kwargs) if kind == 'socket' else _FinXClient(**kwargs)
