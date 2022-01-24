#!/usr/bin/env python

import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from pprint import pformat

import luigi
import yaml
from jinja2 import Environment, FileSystemLoader


def write_config_yml(path, src_yml='example_ftarc.yml'):
    if Path(path).is_file():
        print_log(f'The file exists:\t{path}')
    else:
        print_log(f'Create a config YAML:\t{path}')
        shutil.copyfile(
            str(Path(__file__).parent.joinpath('../static').joinpath(src_yml)),
            Path(path).resolve()
        )


def print_log(message):
    logger = logging.getLogger(__name__)
    logger.debug(message)
    print(f'>>\t{message}', flush=True)


def fetch_executable(cmd, ignore_errors=False):
    executables = [
        cp for cp in [
            str(Path(p).joinpath(cmd))
            for p in os.environ['PATH'].split(os.pathsep)
        ] if os.access(cp, os.X_OK)
    ]
    if executables:
        return executables[0]
    elif ignore_errors:
        return None
    else:
        raise RuntimeError(f'command not found: {cmd}')


def read_yml(path):
    logger = logging.getLogger(__name__)
    with open(str(path), 'r') as f:
        d = yaml.load(f, Loader=yaml.FullLoader)
    logger.debug('YAML data:' + os.linesep + pformat(d))
    return d


def print_yml(data):
    print(yaml.dump(data))


def render_luigi_log_cfg(log_cfg_path, log_dir_path=None,
                         console_log_level='WARNING', file_log_level='DEBUG'):
    log_cfg = Path(str(log_cfg_path)).resolve()
    cfg_dir = log_cfg.parent
    log_dir = (Path(str(log_dir_path)).resolve() if log_dir_path else cfg_dir)
    log_txt = log_dir.joinpath(
        'luigi.{0}.{1}.log.txt'.format(
            file_log_level, datetime.now().strftime('%Y%m%d_%H%M%S')
        )
    )
    for d in {cfg_dir, log_dir}:
        if not d.is_dir():
            print_log(f'Make a directory:\t{d}')
            d.mkdir(parents=True, exist_ok=True)
    print_log(
        '{0} a file:\t{1}'.format(
            ('Overwrite' if log_cfg.exists() else 'Render'), log_cfg
        )
    )
    with log_cfg.open(mode='w') as f:
        f.write(
            Environment(
                loader=FileSystemLoader(
                    str(Path(__file__).parent.joinpath('../template')),
                    encoding='utf8'
                )
            ).get_template('luigi.log.cfg.j2').render({
                'console_log_level': console_log_level,
                'file_log_level': file_log_level, 'log_txt_path': str(log_txt)
            })
            + os.linesep
        )


def load_default_dict(stem):
    return read_yml(
        path=Path(__file__).parent.parent.joinpath(f'static/{stem}.yml')
    )


def build_luigi_tasks(check_scheduling_succeeded=True, hide_summary=False,
                      **kwargs):
    r = luigi.build(local_scheduler=True, detailed_summary=True, **kwargs)
    if not hide_summary:
        print(
            os.linesep
            + os.linesep.join(['Execution summary:', r.summary_text, str(r)])
        )
    if check_scheduling_succeeded:
        assert r.scheduling_succeeded, r.one_line_summary


def parse_fq_id(fq_path):
    fq_stem = Path(fq_path).name
    for _ in range(3):
        if fq_stem.endswith(('fq', 'fastq')):
            fq_stem = Path(fq_stem).stem
            break
        else:
            fq_stem = Path(fq_stem).stem
    return (
        re.sub(
            r'[\._](read[12]|r[12]|[12]|[a-z0-9]+_val_[12]|r[12]_[0-9]+)$', '',
            fq_stem, flags=re.IGNORECASE
        ) or fq_stem
    )
