#!/usr/bin/env python

from pathlib import Path

import luigi
from luigi.util import requires

from .core import FtarcTask
from .picard import CreateSequenceDictionary
from .samtools import SamtoolsFaidx


@requires(SamtoolsFaidx, CreateSequenceDictionary)
class MarkDuplicates(FtarcTask):
    input_sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    gatk = luigi.Parameter(default='gatk')
    samtools = luigi.Parameter(default='samtools')
    use_spark = luigi.BoolParameter(default=False)
    add_markduplicatesspark_args = luigi.ListParameter(
        default=[
            '--create-output-bam-index', 'false',
            '--create-output-bam-splitting-index', 'false'
        ]
    )
    add_markduplicates_args = luigi.ListParameter(
        default=['--ASSUME_SORT_ORDER', 'coordinate']
    )
    add_setnmmdanduqtags_args = luigi.ListParameter(default=list())
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        output_stem = Path(self.input_sam_path).stem + '.markdup'
        return [
            luigi.LocalTarget(dest_dir.joinpath(f'{output_stem}.{s}'))
            for s in ['cram', 'cram.crai', 'metrics.txt']
        ]

    def run(self):
        target_sam = Path(self.input_sam_path)
        run_id = target_sam.stem
        self.print_log(f'Mark duplicates:\t{run_id}')
        input_sam = target_sam.resolve()
        fa = Path(self.fa_path).resolve()
        fa_dict = fa.parent.joinpath(f'{fa.stem}.dict')
        output_cram = Path(self.output()[0].path)
        markdup_metrics_txt = Path(self.output()[2].path)
        dest_dir = output_cram.parent
        tmp_bams = [
            dest_dir.joinpath(f'{output_cram.stem}{s}.bam')
            for s in ['.unfixed', '']
        ]
        memory_mb_per_thread = int(self.memory_mb / self.n_cpu / 8)
        self.setup_shell(
            run_id=run_id, commands=[self.gatk, self.samtools], cwd=dest_dir,
            **self.sh_config,
            env={
                'REF_CACHE': str(dest_dir.joinpath('.ref_cache')),
                'JAVA_TOOL_OPTIONS': self.generate_gatk_java_options(
                    n_cpu=self.n_cpu, memory_mb=self.memory_mb
                )
            }
        )
        if self.use_spark:
            self.run_shell(
                args=(
                    f'set -e && {self.gatk} MarkDuplicatesSpark'
                    + f' --spark-master local[{self.n_cpu}]'
                    + f' --input {input_sam}'
                    + f' --reference {fa}'
                    + ''.join(
                        f' {a}' for a in self.add_markduplicatesspark_args
                    )
                    + f' --metrics-file {markdup_metrics_txt}'
                    + f' --output {tmp_bams[0]}'
                ),
                input_files_or_dirs=[input_sam, fa, fa_dict],
                output_files_or_dirs=[tmp_bams[0], markdup_metrics_txt]
            )
            self.run_shell(
                args=(
                    f'set -e && {self.gatk} SetNmMdAndUqTags'
                    + f' --INPUT {tmp_bams[0]}'
                    + f' --REFERENCE_SEQUENCE {fa}'
                    + ''.join(f' {a}' for a in self.add_setnmmdanduqtags_args)
                    + f' --OUTPUT {tmp_bams[1]}'
                ),
                input_files_or_dirs=[tmp_bams[0], fa, fa_dict],
                output_files_or_dirs=tmp_bams[1]
            )
        else:
            self.run_shell(
                args=(
                    f'set -e && {self.gatk} MarkDuplicates'
                    + f' --INPUT {input_sam}'
                    + f' --REFERENCE_SEQUENCE {fa}'
                    + ''.join(f' {a}' for a in self.add_markduplicates_args)
                    + f' --METRICS_FILE {markdup_metrics_txt}'
                    + f' --OUTPUT {tmp_bams[0]}'
                ),
                input_files_or_dirs=[input_sam, fa, fa_dict],
                output_files_or_dirs=[tmp_bams[0], markdup_metrics_txt]
            )
            self.run_shell(
                args=(
                    f'set -eo pipefail && {self.samtools} sort -@ {self.n_cpu}'
                    + f' -m {memory_mb_per_thread}M -O BAM -l 0'
                    + f' -T {output_cram}.sort {tmp_bams[0]}'
                    + f' | {self.gatk} SetNmMdAndUqTags'
                    + ' --INPUT /dev/stdin'
                    + f' --REFERENCE_SEQUENCE {fa}'
                    + ''.join(f' {a}' for a in self.add_setnmmdanduqtags_args)
                    + f' --OUTPUT {tmp_bams[1]}'
                ),
                input_files_or_dirs=[tmp_bams[0], fa, fa_dict],
                output_files_or_dirs=tmp_bams[1]
            )
        self.remove_files_and_dirs(tmp_bams[0])
        self.samtools_view(
            input_sam_path=tmp_bams[1], fa_path=fa,
            output_sam_path=output_cram, samtools=self.samtools,
            n_cpu=self.n_cpu, index_sam=True, remove_input=True
        )


@requires(SamtoolsFaidx, CreateSequenceDictionary)
class ApplyBqsr(FtarcTask):
    input_sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    known_sites_vcf_paths = luigi.ListParameter()
    interval_list_path = luigi.Parameter(default='')
    dest_dir_path = luigi.Parameter(default='.')
    gatk = luigi.Parameter(default='gatk')
    samtools = luigi.Parameter(default='samtools')
    use_spark = luigi.BoolParameter(default=False)
    add_bqsrpipelinespark_args = luigi.ListParameter(
        default=[
            '--static-quantized-quals', '10', '--static-quantized-quals', '20',
            '--static-quantized-quals', '30', '--use-original-qualities',
            'true', '--create-output-bam-index', 'false',
            '--create-output-bam-splitting-index', 'false'
        ]
    )
    add_baserecalibrator_args = luigi.ListParameter(
        default=['--use-original-qualities', 'true']
    )
    add_applybqsr_args = luigi.ListParameter(
        default=[
            '--static-quantized-quals', '10', '--static-quantized-quals', '20',
            '--static-quantized-quals', '30', '--use-original-qualities',
            'true', '--add-output-sam-program-record', 'true',
            '--create-output-bam-index', 'false'
        ]
    )
    save_memory = luigi.BoolParameter(default=False)
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        output_stem = Path(self.input_sam_path).stem + '.bqsr'
        return [
            luigi.LocalTarget(dest_dir.joinpath(f'{output_stem}.{s}'))
            for s in ['cram', 'cram.crai']
        ]

    def run(self):
        target_sam = Path(self.input_sam_path)
        run_id = target_sam.stem
        self.print_log(f'Apply base quality score recalibration:\t{run_id}')
        input_sam = target_sam.resolve()
        fa = Path(self.fa_path).resolve()
        fa_dict = fa.parent.joinpath(f'{fa.stem}.dict')
        known_sites_vcfs = [
            Path(p).resolve() for p in self.known_sites_vcf_paths
        ]
        interval_list = (
            Path(self.interval_list_path).resolve()
            if self.interval_list_path else None
        )
        output_cram = Path(self.output()[0].path)
        dest_dir = output_cram.parent
        tmp_bam = dest_dir.joinpath(f'{output_cram.stem}.bam')
        self.setup_shell(
            run_id=run_id, commands=[self.gatk, self.samtools],
            cwd=dest_dir, **self.sh_config,
            env={
                'REF_CACHE': str(dest_dir.joinpath('.ref_cache')),
                'JAVA_TOOL_OPTIONS': self.generate_gatk_java_options(
                    n_cpu=self.n_cpu, memory_mb=self.memory_mb
                )
            }
        )
        if self.use_spark:
            self.run_shell(
                args=(
                    f'set -e && {self.gatk} BQSRPipelineSpark'
                    + f' --spark-master local[{self.n_cpu}]'
                    + f' --input {input_sam}'
                    + f' --reference {fa}'
                    + ''.join(f' --known-sites {p}' for p in known_sites_vcfs)
                    + (
                        f' --intervals {interval_list}'
                        if interval_list else ''
                    )
                    + ''.join(f' {a}' for a in self.add_bqsrpipelinespark_args)
                    + f' --output {tmp_bam}'
                ),
                input_files_or_dirs=[
                    input_sam, fa, fa_dict, *known_sites_vcfs,
                    *([interval_list] if interval_list else list())
                ],
                output_files_or_dirs=tmp_bam
            )
        else:
            bqsr_txt = output_cram.parent.joinpath(
                f'{output_cram.stem}.data.txt'
            )
            save_memory_args = (
                ['--disable-bam-index-caching', 'true']
                if self.save_memory else list()
            )
            self.run_shell(
                args=(
                    f'set -e && {self.gatk} BaseRecalibrator'
                    + f' --input {input_sam}'
                    + f' --reference {fa}'
                    + ''.join(f' --known-sites {p}' for p in known_sites_vcfs)
                    + (
                        f' --intervals {interval_list}'
                        if interval_list else ''
                    )
                    + ''.join(
                        f' {a}' for a
                        in [*self.add_baserecalibrator_args, *save_memory_args]
                    )
                    + f' --output {bqsr_txt}'
                ),
                input_files_or_dirs=[
                    input_sam, fa, fa_dict, *known_sites_vcfs,
                    *([interval_list] if interval_list else list())
                ],
                output_files_or_dirs=bqsr_txt
            )
            self.run_shell(
                args=(
                    f'set -e && {self.gatk} ApplyBQSR'
                    + f' --input {input_sam}'
                    + f' --reference {fa}'
                    + f' --bqsr-recal-file {bqsr_txt}'
                    + (
                        f' --intervals {interval_list}'
                        if interval_list else ''
                    )
                    + ''.join(
                        f' {a}'
                        for a in [*self.add_applybqsr_args, *save_memory_args]
                    )
                    + f' --output {tmp_bam}'
                ),
                input_files_or_dirs=[
                    input_sam, fa, fa_dict, bqsr_txt,
                    *([interval_list] if interval_list else list())
                ],
                output_files_or_dirs=tmp_bam
            )
        self.samtools_view(
            input_sam_path=tmp_bam, fa_path=fa, output_sam_path=output_cram,
            samtools=self.samtools, n_cpu=self.n_cpu, index_sam=True,
            remove_input=True
        )


if __name__ == '__main__':
    luigi.run()
