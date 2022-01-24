#!/usr/bin/env python

import logging
import os
import re
import shutil
from math import floor
from pathlib import Path
from pprint import pformat

from psutil import cpu_count, virtual_memory

from ..cli.util import (build_luigi_tasks, fetch_executable, load_default_dict,
                        parse_fq_id, print_log, print_yml, read_yml,
                        render_luigi_log_cfg)
from ..task.controller import PrintEnvVersions, RunPreprocessingPipeline


def run_processing_pipeline(config_yml_path, dest_dir_path=None,
                            max_n_cpu=None, max_n_worker=None,
                            skip_cleaning=False, print_subprocesses=False,
                            console_log_level='WARNING',
                            file_log_level='DEBUG', use_spark=False,
                            use_bwa_mem2=True):
    logger = logging.getLogger(__name__)
    logger.info(f'config_yml_path:\t{config_yml_path}')
    config = _read_config_yml(path=config_yml_path)
    runs = config.get('runs')
    logger.info(f'dest_dir_path:\t{dest_dir_path}')
    dest_dir = Path(dest_dir_path).resolve()
    log_dir = dest_dir.joinpath('log')

    adapter_removal = (
        config['adapter_removal'] if 'adapter_removal' in config else True
    )
    logger.debug(f'adapter_removal:\t{adapter_removal}')

    default_dict = load_default_dict(stem='example_ftarc')
    metrics_collectors = (
        [
            k for k in default_dict['metrics_collectors']
            if config['metrics_collectors'].get(k)
        ] if 'metrics_collectors' in config else list()
    )
    logger.debug(
        'metrics_collectors:' + os.linesep + pformat(metrics_collectors)
    )

    command_dict = {
        'bwa': fetch_executable('bwa-mem2' if use_bwa_mem2 else 'bwa'),
        **{
            c: fetch_executable(c) for c in {
                'bgzip', 'gatk', 'java', 'pbzip2', 'pigz', 'samtools', 'tabix',
                *(['gnuplot'] if 'samtools' in metrics_collectors else list()),
                *(
                    {'cutadapt', 'fastqc', 'trim_galore'}
                    if adapter_removal else set()
                )
            }
        }
    }
    logger.debug('command_dict:' + os.linesep + pformat(command_dict))

    n_cpu = cpu_count()
    n_worker = min(int(max_n_worker or max_n_cpu or n_cpu), (len(runs) or 1))
    n_cpu_per_worker = max(1, floor(int(max_n_cpu or n_cpu) / n_worker))
    memory_mb = virtual_memory().total / 1024 / 1024 / 2
    memory_mb_per_worker = int(memory_mb / n_worker)
    cf_dict = {
        'reference_name': (config.get('reference_name') or ''),
        'use_bwa_mem2': use_bwa_mem2, 'use_spark': use_spark,
        'adapter_removal': adapter_removal,
        'plot_bamstats': (
            fetch_executable('plot-bamstats')
            if 'samtools' in metrics_collectors else ''
        ),
        'metrics_collectors': metrics_collectors,
        'save_memory': (memory_mb_per_worker < 8192),
        **{
            f'{k}_dir_path': str(dest_dir.joinpath(k))
            for k in {'trim', 'align', 'qc'}
        },
        **{k: v for k, v in command_dict.items() if k != 'java'}
    }
    logger.debug('cf_dict:' + os.linesep + pformat(cf_dict))

    sh_config = {
        'log_dir_path': str(log_dir), 'remove_if_failed': (not skip_cleaning),
        'quiet': (not print_subprocesses),
        'executable': fetch_executable('bash')
    }
    logger.debug('sh_config:' + os.linesep + pformat(sh_config))

    resource_path_dict = _resolve_input_file_paths(
        path_dict={
            'fa': config['resources']['reference_fa'],
            'known_sites_vcf': config['resources']['known_sites_vcf']
        }
    )
    logger.debug(
        'resource_path_dict:' + os.linesep + pformat(resource_path_dict)
    )

    sample_dict_list = (
        [
            {**_determine_input_samples(run_dict=r), 'priority': p} for p, r
            in zip([i * 1000 for i in range(1, (len(runs) + 1))[::-1]], runs)
        ] if runs else list()
    )
    logger.debug('sample_dict_list:' + os.linesep + pformat(sample_dict_list))

    print_log(f'Prepare analysis-ready CRAM files:\t{dest_dir}')
    print_yml([
        {
            'config': [
                {'adapter_removal': adapter_removal},
                {'metrics_collectors': metrics_collectors},
                {'n_worker': n_worker}, {'n_cpu': n_cpu},
                {'memory_mb': memory_mb}
            ]
        },
        {
            'input': [
                {'n_sample': len(runs)},
                {'samples': [d['sample_name'] for d in sample_dict_list]}
            ]
        }
    ])
    log_cfg_path = str(log_dir.joinpath('luigi.log.cfg'))
    render_luigi_log_cfg(
        log_cfg_path=log_cfg_path, console_log_level=console_log_level,
        file_log_level=file_log_level
    )

    build_luigi_tasks(
        tasks=[
            PrintEnvVersions(
                command_paths=list(command_dict.values()), sh_config=sh_config
            )
        ],
        workers=1, log_level=console_log_level, logging_conf_file=log_cfg_path,
        hide_summary=True
    )
    build_luigi_tasks(
        tasks=[
            RunPreprocessingPipeline(
                **d, **resource_path_dict, **cf_dict, n_cpu=n_cpu_per_worker,
                memory_mb=memory_mb_per_worker, sh_config=sh_config
            ) for d in sample_dict_list
        ],
        workers=n_worker, log_level=console_log_level,
        logging_conf_file=log_cfg_path
    )
    if not skip_cleaning:
        for a in Path(cf_dict['align_dir_path']).iterdir():
            c = a.joinpath('.ref_cache')
            if c.is_dir():
                print_log(f'Remove a cache directory:\t{c}')
                shutil.rmtree(str(c))


def _read_config_yml(path):
    config = read_yml(path=Path(path).resolve())
    assert (isinstance(config, dict) and config.get('resources')), config
    assert isinstance(config['resources'], dict), config['resources']
    for k in ['reference_fa', 'known_sites_vcf']:
        v = config['resources'].get(k)
        if k == 'known_sites_vcf':
            assert isinstance(v, list), k
            assert len(v) > 0, k
            assert _has_unique_elements(v), k
            for s in v:
                assert isinstance(s, str), k
        else:
            assert isinstance(v, str), k
    assert config.get('runs'), config
    assert isinstance(config['runs'], list), config['runs']
    for r in config['runs']:
        assert isinstance(r, dict), r
        assert r.get('fq'), r
        assert isinstance(r['fq'], list), r
        assert _has_unique_elements(r['fq']), r
        assert (len(r['fq']) <= 2), r
        for p in r['fq']:
            assert p.endswith(('.gz', '.bz2')), p
        if r.get('read_group'):
            assert isinstance(r['read_group'], dict), r
            for k, v in r['read_group'].items():
                assert re.fullmatch(r'[A-Z]{2}', k), k
                assert isinstance(v, str), k
    return config


def _has_unique_elements(elements):
    return len(set(elements)) == len(tuple(elements))


def _resolve_file_path(path):
    p = Path(path).resolve()
    assert p.is_file(), f'file not found: {p}'
    return str(p)


def _resolve_input_file_paths(path_list=None, path_dict=None):
    if path_list:
        return [_resolve_file_path(s) for s in path_list]
    elif path_dict:
        new_dict = dict()
        for k, v in path_dict.items():
            if isinstance(v, str):
                new_dict[f'{k}_path'] = _resolve_file_path(v)
            elif v:
                new_dict[f'{k}_paths'] = [
                    _resolve_file_path(s) for s in v
                ]
        return new_dict


def _determine_input_samples(run_dict):
    g = run_dict.get('read_group') or dict()
    return {
        'fq_paths': _resolve_input_file_paths(path_list=run_dict['fq']),
        'read_group': g,
        'sample_name': (g.get('SM') or parse_fq_id(fq_path=run_dict['fq'][0]))
    }
