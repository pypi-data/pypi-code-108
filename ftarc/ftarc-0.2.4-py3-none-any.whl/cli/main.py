#!/usr/bin/env python
"""
FASTQ-to-analysis-ready-CRAM Workflow Executor for Human Genome Sequencing

Usage:
    ftarc download [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--use-bwa-mem2]
        [--dest-dir=<path>] [--log-dir=<path>]
    ftarc init [--debug|--info] [--yml=<path>]
    ftarc pipeline [--debug|--info] [--yml=<path>] [--cpus=<int>]
        [--workers=<int>] [--skip-cleaning] [--print-subprocesses]
        [--use-bwa-mem2] [--use-spark] [--dest-dir=<path>]
    ftarc trim [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses]
        [--dest-dir=<path>] [--log-dir=<path>] <fq_path_prefix>...
    ftarc align [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--use-bwa-mem2]
        [--dest-dir=<path>] [--log-dir=<path>] <fa_path> <fq_path_prefix>...
    ftarc markdup [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--use-spark]
        [--dest-dir=<path>] [--log-dir=<path>] <fa_path> <sam_path>...
    ftarc bqsr [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--use-spark]
        [--dest-dir=<path>] [--log-dir=<path>] (--known-sites-vcf=<path>)...
        [--interval-list=<path>] <fa_path> <sam_path>...
    ftarc dedup [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--dest-dir=<path>]
        [--log-dir=<path>] <fa_path> <sam_path>...
    ftarc validate [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--summary]
        [--dest-dir=<path>] [--log-dir=<path>] <fa_path> <sam_path>...
    ftarc fastqc [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--dest-dir=<path>]
        [--log-dir=<path>] <fq_path>...
    ftarc samqc [--debug|--info] [--cpus=<int>] [--workers=<int>]
        [--skip-cleaning] [--print-subprocesses] [--dest-dir=<path>]
        [--log-dir=<path>] <fa_path> <sam_path>...
    ftarc -h|--help
    ftarc --version

Commands:
    download                Download and process GRCh38 resource data
    init                    Create a config YAML template
    run                     Create analysis-ready CRAM files from FASTQ files
                            (Trim adapters, align reads, mark duplicates, and
                             apply BQSR)
    trim                    Trim adapter sequences in FASTQ files
    align                   Align read sequences in FASTQ files
    markdup                 Mark duplicates in CRAM or BAM files using GATK
    bqsr                    Apply BQSR to CRAM or BAM files using GATK
    dedup                   Remove duplicates in marked CRAM or BAM files
    validate                Validate CRAM or BAM files using Picard
    fastqc                  Collect metrics from FASTQ files using FastQC
    samqc                   Collect metrics from CRAM or BAM files using Picard
                            and Samtools

Options:
    -h, --help              Print help and exit
    --version               Print version and exit
    --debug, --info         Execute a command with debug|info messages
    --yml=<path>            Specify a config YAML path [default: ftarc.yml]
    --cpus=<int>            Limit CPU cores used
    --workers=<int>         Specify the maximum number of workers [default: 1]
    --skip-cleaning         Skip incomlete file removal when a task fails
    --print-subprocesses    Print STDOUT/STDERR outputs from subprocesses
    --use-bwa-mem2          Use Bwa-mem2 for read alignment
    --use-spark             Use Spark-enabled GATK tools
    --dest-dir=<path>       Specify a destination directory path [default: .]
    --log-dir=<path>        Specify an output log directory path
    --summary               Set SUMMARY to the mode of output
    --known-sites-vcf=<path>
                            Specify paths of known polymorphic sites VCF files
    --interval-list=<path>  Specify a path to an interval_list BED file

Args:
    <fq_path_prefix>        Path prefix of FASTQ files
    <fa_path>               Path to an reference FASTA file
                            (The index and sequence dictionary are required.)
    <sam_path>              Path to a sorted CRAM or BAM file
    <fq_path>               Path to a FASTQ file
"""

import logging
import os
from itertools import product
from math import ceil, floor
from pathlib import Path

from docopt import docopt
from psutil import cpu_count, virtual_memory

from .. import __version__
from ..task.bwa import AlignReads
from ..task.controller import CollectMultipleSamMetrics
from ..task.downloader import DownloadAndProcessResourceFiles
from ..task.fastqc import CollectFqMetricsWithFastqc
from ..task.gatk import ApplyBqsr, MarkDuplicates
from ..task.picard import ValidateSamFile
from ..task.samtools import RemoveDuplicates
from ..task.trimgalore import TrimAdapters
from .pipeline import run_processing_pipeline
from .util import (build_luigi_tasks, fetch_executable, load_default_dict,
                   print_log, print_yml, write_config_yml)


def main():
    args = docopt(__doc__, version=__version__)
    if args['--debug']:
        log_level = 'DEBUG'
    elif args['--info']:
        log_level = 'INFO'
    else:
        log_level = 'WARNING'
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=log_level
    )
    logger = logging.getLogger(__name__)
    logger.debug(f'args:{os.linesep}{args}')
    print_log(f'Start the workflow of ftarc {__version__}')
    if args['init']:
        write_config_yml(path=args['--yml'])
    elif args['pipeline']:
        run_processing_pipeline(
            config_yml_path=args['--yml'], dest_dir_path=args['--dest-dir'],
            max_n_cpu=args['--cpus'], max_n_worker=args['--workers'],
            skip_cleaning=args['--skip-cleaning'],
            print_subprocesses=args['--print-subprocesses'],
            console_log_level=log_level, use_spark=args['--use-spark'],
            use_bwa_mem2=args['--use-bwa-mem2']
        )
    else:
        n_cpu = int(args['--cpus'] or cpu_count())
        n_worker = min(int(args['--workers'] or 1), n_cpu)
        n_cpu_per_worker = max(floor(n_cpu / n_worker), 1)
        memory_mb_per_worker = ceil(
            virtual_memory().total / 1024 / 1024 / 2 / n_worker
        )
        print_yml([
            {'n_worker': n_worker}, {'n_cpu_per_worker': n_cpu_per_worker},
            {'memory_mb_per_worker': memory_mb_per_worker}
        ])
        gatk_or_picard = (
            fetch_executable('gatk', ignore_errors=(not args['bqsr']))
            or fetch_executable('picard')
        )
        sh_config = {
            'log_dir_path': (args['--log-dir'] or args['--dest-dir']),
            'remove_if_failed': (not args['--skip-cleaning']),
            'quiet': (not args['--print-subprocesses']),
            'executable': fetch_executable('bash')
        }
        if args['download']:
            build_luigi_tasks(
                tasks=[
                    DownloadAndProcessResourceFiles(
                        src_url_dict=load_default_dict(stem='urls'),
                        dest_dir_path=args['--dest-dir'],
                        **{
                            c: fetch_executable(c) for c in [
                                'wget', 'pbzip2', 'bgzip', 'pigz', 'samtools',
                                'tabix'
                            ]
                        },
                        bwa=fetch_executable(
                            'bwa-mem2' if args['--use-bwa-mem2'] else 'bwa'
                        ),
                        gatk=gatk_or_picard, n_cpu=n_cpu_per_worker,
                        memory_mb=memory_mb_per_worker,
                        use_bwa_mem2=args['--use-bwa-mem2'],
                        sh_config=sh_config
                    )
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['trim']:
            kwargs = {
                'dest_dir_path': args['--dest-dir'], 'n_cpu': n_cpu_per_worker,
                'memory_mb': memory_mb_per_worker, 'sh_config': sh_config,
                **{
                    c: fetch_executable(c) for c
                    in ['pigz', 'pbzip2', 'trim_galore', 'cutadapt', 'fastqc']
                }
            }
            build_luigi_tasks(
                tasks=[
                    TrimAdapters(
                        fq_paths=_find_fq_paths(fq_path_prefix=p),
                        sample_name=Path(p).stem, **kwargs
                    ) for p in args['<fq_path_prefix>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['align']:
            kwargs = {
                'fa_path': args['<fa_path>'],
                'dest_dir_path': args['--dest-dir'],
                'bwa': fetch_executable(
                    'bwa-mem2' if args['--use-bwa-mem2'] else 'bwa'
                ),
                'samtools': fetch_executable('samtools'),
                'use_bwa_mem2': args['--use-bwa-mem2'],
                'n_cpu': n_cpu_per_worker, 'memory_mb': memory_mb_per_worker,
                'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    AlignReads(
                        fq_paths=_find_fq_paths(fq_path_prefix=p),
                        sample_name=Path(p).stem, **kwargs
                    ) for p in args['<fq_path_prefix>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['markdup']:
            kwargs = {
                'fa_path': args['<fa_path>'],
                'dest_dir_path': args['--dest-dir'], 'gatk': gatk_or_picard,
                'samtools': fetch_executable('samtools'),
                'use_spark': args['--use-spark'], 'n_cpu': n_cpu_per_worker,
                'memory_mb': memory_mb_per_worker, 'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    MarkDuplicates(input_sam_path=p, **kwargs)
                    for p in args['<sam_path>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['bqsr']:
            kwargs = {
                'fa_path': args['<fa_path>'],
                'known_sites_vcf_paths': args['--known-sites-vcf'],
                'interval_list_path': (args['--interval-list'] or ''),
                'dest_dir_path': args['--dest-dir'], 'gatk': gatk_or_picard,
                'samtools': fetch_executable('samtools'),
                'use_spark': args['--use-spark'], 'n_cpu': n_cpu_per_worker,
                'memory_mb': memory_mb_per_worker,
                'save_memory': (memory_mb_per_worker < 8192),
                'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    ApplyBqsr(input_sam_path=p, **kwargs)
                    for p in args['<sam_path>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['dedup']:
            kwargs = {
                'fa_path': args['<fa_path>'],
                'dest_dir_path': args['--dest-dir'],
                'samtools': fetch_executable('samtools'),
                'n_cpu': n_cpu_per_worker, 'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    RemoveDuplicates(input_sam_path=p, **kwargs)
                    for p in args['<sam_path>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['validate']:
            kwargs = {
                'fa_path': args['<fa_path>'],
                'dest_dir_path': args['--dest-dir'], 'picard': gatk_or_picard,
                'add_validatesamfile_args': [
                    '--MODE', ('SUMMARY' if args['--summary'] else 'VERBOSE'),
                    '--IGNORE', 'MISSING_TAG_NM'
                ],
                'n_cpu': n_cpu_per_worker, 'memory_mb': memory_mb_per_worker,
                'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    ValidateSamFile(sam_path=p, **kwargs)
                    for p in args['<sam_path>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['fastqc']:
            kwargs = {
                'dest_dir_path': args['--dest-dir'],
                'fastqc': fetch_executable('fastqc'),
                'n_cpu': n_cpu_per_worker, 'memory_mb': memory_mb_per_worker,
                'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    CollectFqMetricsWithFastqc(fq_paths=[p], **kwargs)
                    for p in args['<fq_path>']
                ],
                workers=n_worker, log_level=log_level
            )
        elif args['samqc']:
            kwargs = {
                'fa_path': args['<fa_path>'],
                'dest_dir_path': args['--dest-dir'],
                'samtools': fetch_executable('samtools'),
                'plot_bamstats': fetch_executable('plot-bamstats'),
                'picard': gatk_or_picard, 'n_cpu': n_cpu_per_worker,
                'memory_mb': memory_mb_per_worker, 'sh_config': sh_config
            }
            build_luigi_tasks(
                tasks=[
                    CollectMultipleSamMetrics(sam_path=p, **kwargs)
                    for p in args['<sam_path>']
                ],
                workers=n_worker, log_level=log_level
            )


def _find_fq_paths(fq_path_prefix):
    hits = sorted(
        o for o in Path(fq_path_prefix).resolve().parent.iterdir()
        if o.name.startswith(Path(fq_path_prefix).name) and (
            o.name.endswith(('.fq', '.fastq')) or o.name.endswith(
                tuple(
                    f'.{a}.{b}' for a, b
                    in product(['fq', 'fastq'], ['', 'gz', 'bz2'])
                )
            )
        )
    )
    assert bool(hits), f'FASTQ files not found: {hits}'
    if len(hits) == 1:
        pass
    else:
        for a, b in zip(hits[0].stem, hits[1].stem):
            assert a == b or (a == '1' and b == '2'), 'invalid path prefix'
    return [str(o) for o in hits[:2]]
