#!/usr/bin/env python

import logging
import os
import re
import sys
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path

import luigi
from shoper.shelloperator import ShellOperator


class ShellTask(luigi.Task, metaclass=ABCMeta):
    retry_count = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_shell()

    @luigi.Task.event_handler(luigi.Event.PROCESSING_TIME)
    def print_execution_time(self, processing_time):
        logger = logging.getLogger('task-timer')
        message = '{0}.{1} - total elapsed time:\t{2}'.format(
            self.__class__.__module__, self.__class__.__name__,
            timedelta(seconds=processing_time)
        )
        logger.info(message)
        print(message, flush=True)

    @classmethod
    def print_log(cls, message, new_line=True):
        logger = logging.getLogger(cls.__name__)
        logger.info(message)
        print((os.linesep if new_line else '') + f'>>\t{message}', flush=True)

    @classmethod
    def initialize_shell(cls):
        cls.__log_txt_path = None
        cls.__sh = None
        cls.__run_kwargs = None

    @classmethod
    def setup_shell(cls, run_id=None, log_dir_path=None, commands=None,
                    cwd=None, remove_if_failed=True, clear_log_txt=False,
                    print_command=True, quiet=True, executable='/bin/bash',
                    env=None, **kwargs):
        cls.__log_txt_path = (
            str(
                Path(log_dir_path).joinpath(
                    f'{cls.__module__}.{cls.__name__}.{run_id}.sh.log.txt'
                ).resolve()
            ) if log_dir_path and run_id else None
        )
        cls.__sh = ShellOperator(
            log_txt=cls.__log_txt_path, quiet=quiet,
            clear_log_txt=clear_log_txt,
            logger=logging.getLogger(cls.__name__),
            print_command=print_command, executable=executable
        )
        cls.__run_kwargs = {
            'cwd': cwd, 'remove_if_failed': remove_if_failed,
            'env': (
                {
                    **env,
                    **{k: v for k, v in os.environ.items() if k not in env}
                } if env else dict(os.environ)
            ),
            **kwargs
        }
        cls.make_dirs(log_dir_path, cwd)
        if commands:
            cls.run_shell(args=list(cls.generate_version_commands(commands)))

    @classmethod
    def make_dirs(cls, *paths):
        for p in paths:
            if p:
                d = Path(str(p)).resolve()
                if not d.is_dir():
                    cls.print_log(f'Make a directory:\t{d}', new_line=False)
                    d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def run_shell(cls, *args, **kwargs):
        logger = logging.getLogger(cls.__name__)
        start_datetime = datetime.now()
        cls.__sh.run(
            *args, **kwargs,
            **{k: v for k, v in cls.__run_kwargs.items() if k not in kwargs}
        )
        if 'asynchronous' in kwargs:
            cls.__sh.wait()
        elapsed_timedelta = datetime.now() - start_datetime
        message = f'shell elapsed time:\t{elapsed_timedelta}'
        logger.info(message)
        if cls.__log_txt_path:
            with open(cls.__log_txt_path, 'a') as f:
                f.write(f'### {message}{os.linesep}')

    @classmethod
    def remove_files_and_dirs(cls, *paths):
        targets = [Path(str(p)) for p in paths if Path(str(p)).exists()]
        if targets:
            cls.run_shell(
                args=' '.join([
                    'rm',
                    ('-rf' if [t for t in targets if t.is_dir()] else '-f'),
                    *[str(t) for t in targets]
                ])
            )

    @classmethod
    def print_env_versions(cls):
        python = sys.executable
        version_files = [
            Path('/proc/version'),
            *[
                o for o in Path('/etc').iterdir()
                if o.name.endswith(('-release', '_version'))
            ]
        ]
        cls.run_shell(
            args=[
                f'{python} --version',
                f'{python} -m pip --version',
                f'{python} -m pip freeze --no-cache-dir',
                'uname -a',
                *[f'cat {o}' for o in version_files if o.is_file()]
            ]
        )

    @staticmethod
    @abstractmethod
    def generate_version_commands(commands):
        pass


class FtarcTask(ShellTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def generate_version_commands(commands):
        for c in ([commands] if isinstance(commands, str) else commands):
            n = Path(c).name
            if n == 'java' or n.endswith('.jar'):
                yield f'{c} -version'
            elif n == 'bwa':
                yield f'{c} 2>&1 | grep -e "Program:" -e "Version:"'
            elif n == 'wget':
                yield f'{c} --version | head -1'
            elif n == 'bwa-mem2':
                yield f'{c} version'
            elif n == 'picard':
                yield f'{c} CreateSequenceDictionary --version'
            else:
                yield f'{c} --version'

    @classmethod
    def bzip2_to_gzip(cls, src_bz2_path, dest_gz_path, pbzip2='pbzip2',
                      pigz='pigz', n_cpu=1):
        cls.run_shell(
            args=(
                f'set -eo pipefail && {pbzip2} -p{n_cpu} -dc {src_bz2_path}'
                + f' | {pigz} -p {n_cpu} -c - > {dest_gz_path}'
            ),
            input_files_or_dirs=src_bz2_path, output_files_or_dirs=dest_gz_path
        )

    @staticmethod
    def generate_gatk_java_options(n_cpu=1, memory_mb=4096):
        return ' '.join([
            '-Dsamjdk.compression_level=5',
            '-Dsamjdk.use_async_io_read_samtools=true',
            '-Dsamjdk.use_async_io_write_samtools=true',
            '-Dsamjdk.use_async_io_write_tribble=false',
            '-Xmx{}m'.format(int(memory_mb)), '-XX:+UseParallelGC',
            '-XX:ParallelGCThreads={}'.format(int(n_cpu))
        ])

    @classmethod
    def samtools_index(cls, sam_path, samtools='samtools', n_cpu=1):
        cls.run_shell(
            args=(
                f'set -e && {samtools} quickcheck -v {sam_path}'
                + f' && {samtools} index -@ {n_cpu} {sam_path}'
            ),
            input_files_or_dirs=sam_path,
            output_files_or_dirs=re.sub(
                r'\.(cr|b)am$', '.\\1am.\\1ai', str(sam_path)
            )
        )

    @classmethod
    def samtools_view(cls, input_sam_path, fa_path, output_sam_path,
                      samtools='samtools', n_cpu=1, add_args=None,
                      index_sam=False, remove_input=False):
        cls.run_shell(
            args=(
                f'set -e && {samtools} quickcheck -v {input_sam_path}'
                + f' && {samtools} view -@ {n_cpu} -T {fa_path}'
                + ' -{}S'.format(
                    'C' if str(output_sam_path).endswith('.cram') else 'b'
                )
                + (
                    ''.join(
                        f' {a}' for a in
                        ([add_args] if isinstance(add_args, str) else add_args)
                    ) if add_args else ''
                )
                + f' -o {output_sam_path} {input_sam_path}'
            ),
            input_files_or_dirs=[
                input_sam_path, fa_path, f'{fa_path}.fai'
            ],
            output_files_or_dirs=output_sam_path
        )
        if index_sam:
            cls.samtools_index(
                sam_path=output_sam_path, samtools=samtools, n_cpu=n_cpu
            )
        if remove_input:
            cls.remove_files_and_dirs(input_sam_path)
