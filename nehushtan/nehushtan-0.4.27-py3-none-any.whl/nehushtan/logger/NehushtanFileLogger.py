import json
import math
import os
import sys
import threading
import time
import traceback
from datetime import datetime

import psutil

from nehushtan.helper.CommonHelper import CommonHelper
from nehushtan.logger.NehushtanLogging import NehushtanLogging


class NehushtanFileLogger:
    """
    @since 0.1.25
    Another solution for logging, just use raw writing method to target file.
    """

    def __init__(
            self,
            title='default',
            log_dir: str = None,
            log_level=NehushtanLogging.DEBUG,
            categorize: bool = True,
            date_rotate: bool = True,
            print_higher_than_this_level=NehushtanLogging.CRITICAL,
            record_millisecond=False,
            file_encoding='utf-8'
    ):
        self.categorize = categorize
        self.log_dir = log_dir
        self.title = title

        # This logic is since 0.4.19
        if self.categorize:
            x = title.split('/')
            last_title = None
            y = []
            for xx in x:
                if xx:
                    if last_title:
                        y.append(last_title)
                    last_title = xx
            if y and self.log_dir:
                self.log_dir = self.log_dir + '/' + ('/'.join(y))
            if last_title:
                self.title = last_title

        self.log_level = log_level

        self.date_rotate = date_rotate
        self.record_millisecond = record_millisecond
        # self.print_as_well = print_as_well <-- should use print_higher_than_this_level=NehushtanLogging.NOTSET
        # If all, use NOTSET; if none, use FATAL
        if print_higher_than_this_level is True:
            self.print_higher_than_this_level = NehushtanLogging.NOTSET
        elif print_higher_than_this_level is False:
            self.print_higher_than_this_level = NehushtanLogging.CRITICAL
        else:
            self.print_higher_than_this_level = print_higher_than_this_level

        # Since 0.4.20 CACHED FILE HANDLER
        self.keep_file_open = True
        self.opened_files = {}
        # Since 0.4.20 TARGET FILE ENCODING
        self.file_encoding = file_encoding

    def __del__(self):
        if len(self.opened_files.items()) > 0:
            for name, file in self.opened_files.items():
                file.close()
                # print(name, 'closed')

    def get_target_file(self):
        if self.log_dir is None:
            return ''

        category_dir = self.log_dir

        # a -> a/a-DATE.log
        # a/b -> a/b-DATE.log
        # a/b/c -> a/b/c-DATE.log

        if self.categorize:
            category_dir = os.path.join(self.log_dir, self.title)

        today = ''
        if self.date_rotate:
            today = time.strftime("%Y%m%d", time.localtime())
            today = f'-{today}'

        target_file = os.path.join(category_dir, f'{self.title}{today}.log')

        final_dir = os.path.dirname(target_file)
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)

        return target_file

    def get_target_file_hander(self, target_file_path: str):
        if not target_file_path:
            return None

        if self.keep_file_open:
            file = self.opened_files.get(target_file_path)
            if not file:
                file = open(target_file_path, 'a', encoding=self.file_encoding)
                self.opened_files[target_file_path] = file
        else:
            file = open(target_file_path, 'a', encoding=self.file_encoding)

        return file

    def write_raw_line_to_log(self, text: str, level: int = NehushtanLogging.INFO, end=os.linesep):
        """
        Parameter `level` is only used to determine stdout or stderr when file empty.
        Since 0.2.8, Parameter `end` added.
        """
        target_file = self.get_target_file()

        if target_file != '':
            file = self.get_target_file_hander(target_file)
            file.write(text + end)
            file.flush()

            if not self.keep_file_open:
                file.close()

        if target_file == '' or level > self.print_higher_than_this_level:
            if level >= NehushtanLogging.WARNING:
                print(text, file=sys.stderr, end=end)
            else:
                print(text, end=end)

        return self

    @staticmethod
    def get_level_label(level: int):
        return NehushtanLogging.get_label_of_level(level)

    def write_formatted_line_to_log(self, level: int, message: str, extra=None, hide_extra: bool = False):
        """
        Since 0.3.7 add `hide_extra`
        """
        if level < self.log_level:
            return self
        time_format_string = "%Y-%m-%d %H:%M:%S"
        if self.record_millisecond:
            time_format_string += '.%f'
        # now = time.strftime(time_format_string, time.localtime())
        now = datetime.now().strftime(time_format_string)
        level_label = NehushtanFileLogger.get_level_label(level)
        pid = os.getpid()
        thread = threading.currentThread()
        line = f'{now} <{self.title}> [{level_label}] <{pid}:{thread.getName()}> {message}'
        if not hide_extra:
            extra_json = self.ensure_extra_as_dict(extra)
            line += f' | {extra_json}'
        return self.write_raw_line_to_log(line, level)

    def debug(self, message: str, extra=None):
        return self.write_formatted_line_to_log(NehushtanLogging.DEBUG, message, extra)

    def info(self, message: str, extra=None):
        return self.write_formatted_line_to_log(NehushtanLogging.INFO, message, extra)

    def notice(self, message: str, extra=None):
        return self.write_formatted_line_to_log(NehushtanLogging.NOTICE, message, extra)

    def warning(self, message: str, extra=None):
        return self.write_formatted_line_to_log(NehushtanLogging.WARNING, message, extra)

    def error(self, message: str, extra=None):
        return self.write_formatted_line_to_log(NehushtanLogging.ERROR, message, extra)

    def exception(self, message: str, exception: BaseException):
        just_the_string = self.get_traceback_info_from_exception(exception)
        return self.write_formatted_line_to_log(NehushtanLogging.ERROR, message, f'{type(exception).__name__}') \
            .write_raw_line_to_log(just_the_string, NehushtanLogging.ERROR)

    def critical(self, message: str, extra=None):
        return self.write_formatted_line_to_log(NehushtanLogging.CRITICAL, message, extra)

    def log_progress(
            self,
            title: str,
            done_task_count: int,
            total_task_count: int = 100,
            progress_bar_length: int = 20,
            desc: str = None,
            level: int = NehushtanLogging.NOTICE
    ):
        """
        Since 0.3.7
        """
        percent = 100.0 * done_task_count / total_task_count
        bar = ''
        done_bar_chars = math.floor(progress_bar_length * percent / 100.0)
        for i in range(done_bar_chars):
            bar += '='
        for j in range(progress_bar_length - done_bar_chars):
            bar += '-'

        content = f'{title}: {percent:2.2f}% ({done_task_count}/{total_task_count}) [{bar}]'
        if desc is not None:
            content += f' {desc}'
        return self.write_formatted_line_to_log(
            level,
            content,
            hide_extra=True
        )

    def log_current_memory_usage_of_process(self, pid: int = None, level: int = NehushtanLogging.INFO):
        """
        Since 0.2.10
        Filed `pid` would use os.getpid() for None.
        """
        memory_usage = psutil.Process(pid=pid).memory_info()
        self.write_formatted_line_to_log(
            level,
            'Current Memory Usage Snapshot (in MB)',
            {'rss': memory_usage.rss / 1024.0 / 1024.0, 'vms': memory_usage.vms / 1024.0 / 1024.0}
        )

    def log_current_memory_usage_of_object(self, target_name: str, target, level: int = NehushtanLogging.INFO):
        """
        Since 0.2.10
        """
        memory_usage = sys.getsizeof(target)
        self.write_formatted_line_to_log(
            level,
            f'Current Memory Usage used by {target_name} (in MB)',
            memory_usage / 1024.0 / 1024.0
        )

    @staticmethod
    def ensure_extra_as_dict(extra):
        """
        Since 0.1.25, add ensure_ascii as False to allow unicode chars
        """
        return json.dumps(extra, default=lambda inner_x: inner_x.__str__(), ensure_ascii=False)

    def get_args_json_to_clone(self):
        """
        Since 0.2.15
        """
        return json.dumps([
            self.title,
            self.log_dir,
            self.log_level,
            self.categorize,
            self.date_rotate,
            self.print_higher_than_this_level,
            self.record_millisecond,
        ])

    @staticmethod
    def build_instance_from_args_json(args_json: str):
        """
        Since 0.2.15
        """
        args = json.loads(args_json)
        if type(args) is not list and type(args) is not tuple:
            raise ValueError('String `args_json` should be an array in JSON format')
        return NehushtanFileLogger(*args)

    @staticmethod
    def get_traceback_info_from_exception(exception: BaseException) -> str:
        """
        Since 0.4.4
        Since 0.4.26 -> try to make it compitable with 3.10
        """
        if CommonHelper.is_python_version_at_least(3, 10):
            return ''.join(traceback.format_exception(exception))
        else:
            return ''.join(
                traceback.format_exception(
                    etype=type(exception),
                    value=exception,
                    tb=exception.__traceback__
                )
            )
