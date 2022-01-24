import sys
from os import getenv

from traceback import print_exc
from multiprocessing import Pool, cpu_count, get_context
from functools import partial
from tqdm import tqdm
from gitlab_ps_utils.json_utils import json_pretty
from gitlab_ps_utils.logger import myLogger
from gitlab_ps_utils.process import NoDaemonProcess


class MultiProcessing():
    tanuki = "#e24329"
    _func = None
    def __init__(self):
        self.log = myLogger(__name__, app_path=getenv('APP_PATH', '.'), log_name=getenv('APP_NAME', 'application'))

    def worker_init(self, func):
        global _func
        _func = func


    def worker(self, x):
        return _func(x)


    def start_multi_process(self, function, iterable, processes=None, nestable=False):
        """
            Wrapper function to handle multiprocessing a function with a list of data

            This function leverages map to handle multiprocessing. This function will return a list of data from the function so use this function if your function returns necessary data

            :param: function: (func) The function processesing the elements of the list
            :param: iterable: (list) A list of data to be passed into the function to process
            :param: processes: (int) Explicit number of processes to split the function across. If processes is not set, number of processes will default to total number of physical cores of CPU
            :param: nestable: (bool) Allow this multiprocessed function to create nested multiprocessed functions

            :return: A list of the data returned from the process map
        """
        ctx = get_context("spawn")
        if nestable:
            ctx.Process = NoDaemonProcess
        p = ctx.Pool(processes=self.get_no_of_processes(processes),
                    initializer=self.worker_init, initargs=(function,))
        try:
            for i in tqdm(p.imap_unordered(self.worker, iterable),
                        total=len(iterable), colour=self.tanuki):
                yield i
        except Exception as e:
            self.log.critical("Migration pool failed with error:\n{}".format(e))
            self.log.critical(print_exc())
        finally:
            p.close()
            p.join()


    def start_multi_process_with_args(
            self, function, iterable, *args, processes=None, nestable=False, **kwargs):
        """
            Wrapper function to handle multiprocessing a function with multiple arguments with a list of data

            example function signature:

            def func(*args, iterable, **kwargs)

            The iterable must be the last argument in the handler function signature

            This function leverages map to handle multiprocessing. This function will return a list of data from the function so use this function if your function returns necessary data

            :param: function: (func) The function processesing the elements of the list
            :param: iterable: (list) A list of data to be passed into the function to process
            :param: *args: (args) Any additional arguments the function needs passed in
            :params processes: (int) Explicit number of processes to split the function across. If processes is not set, number of processes will default to total number of physical cores of CPU
            :param: nestable: (bool) Allow this multiprocessed function to create nested multiprocessed functions

            :return: A list of the data returned from the process map
        """
        ctx = get_context("spawn")
        if nestable:
            ctx.Process = NoDaemonProcess
        p = ctx.Pool(processes=self.get_no_of_processes(processes),
                    initializer=self.worker_init, initargs=(partial(function, *args, **kwargs),))
        try:
            for i in tqdm(p.imap_unordered(self.worker, iterable),
                        total=len(iterable), colour=self.tanuki):
                yield i
        except Exception as e:
            self.log.critical("Migration pool failed with error:\n{}".format(e))
            self.log.critical(print_exc())
        finally:
            p.close()
            p.join()


    def start_multi_process_stream(self, function, iterable, processes=None, nestable=False):
        """
            Wrapper function to handle multiprocessing a function with a list of data

            This function leverages imap_unordered to handle processing a stream of data of unknown length, like from a generator

            :param: function: (func) The function processesing the elements of the list
            :param: iterable: (list) A list of data to be passed into the function to process
            :param: processes: (int) Explicit number of processes to split the function across. If processes is not set, number of processes will default to total number of physical cores of CPU
            :param: nestable: (bool) Allow this multiprocessed function to create nested multiprocessed functions

            :return: An imap_unordered object. Assume no useful data will be returned with this function
        """
        ctx = get_context("spawn")
        if nestable:
            ctx.Process = NoDaemonProcess
        p = ctx.Pool(processes=self.get_no_of_processes(processes),
                    initializer=self.worker_init, initargs=(function,))
        try:
            return p.imap_unordered(self.worker, iterable)
        except Exception as e:
            self.log.critical("Migration pool failed with error:\n{}".format(e))
            self.log.critical(print_exc())
        finally:
            p.close()
            p.join()


    def start_multi_process_stream_with_args(
            self, function, iterable, *args, processes=None, nestable=False, **kwargs):
        """
            Wrapper function to handle multiprocessing a function with multiple arguments with a list of data

            example function signature:

            def func(*args, iterable, **kwargs)

            The iterable must be the last argument in the handler function signature

            This function leverages imap_unordered to handle processing a stream of data of unknown length, like from a generator

            :param: function: (func) The function processesing the elements of the list
            :param: iterable: (list) A list of data to be passed into the function to process
            :param: *args: (args) Any additional arguments the function needs passed in
            :param: processes: (int) Explicit number of processes to split the function across. If processes is not set, number of processes will default to total number of physical cores of CPU
            :param: nestable: (bool) Allow this multiprocessed function to create nested multiprocessed functions

            :return: An imap_unordered object. Assume no useful data will be returned with this function
        """
        ctx = get_context("spawn")
        if nestable:
            ctx.Process = NoDaemonProcess
        p = ctx.Pool(processes=self.get_no_of_processes(processes),
                    initializer=self.worker_init, initargs=(partial(function, *args, **kwargs),))
        try:
            return p.imap_unordered(self.worker, iterable)
        except Exception as e:
            self.log.critical("Migration pool failed with error:\n{}".format(e))
            self.log.critical(print_exc())
        finally:
            p.close()
            p.join()


    def handle_multi_process_write_to_file_and_return_results(
            self, function, results_function, iterable, path, processes=None):
        with open(path, 'w') as f:
            f.write("[\n")
            try:
                p = Pool(processes=self.get_no_of_processes(processes),
                        initializer=self.worker_init, initargs=(function,))
                for result in tqdm(p.imap_unordered(
                        self.worker, iterable), total=len(iterable), colour=self.tanuki):
                    f.write(json_pretty(result))
                    yield results_function(result)
            except TypeError as te:
                print_exc()
                print("Found None ({}). Stopping write to file".format(te))
            except Exception as e:
                self.log.critical(
                    "Migration processes failed with error:\n{}".format(e))
                self.log.critical(print_exc())
            else:
                f.write("\n]")
            finally:
                p.close()
                p.join()


    def get_no_of_processes(self, processes):
        try:
            proc = int(processes) if processes else 4
            self.log.info(
                f"Running command with {proc} parallel processes on {cpu_count()} CPU")
            return proc
        except ValueError:
            self.log.error(f"Input for # of processes is not an integer: {processes}")
            sys.exit()
