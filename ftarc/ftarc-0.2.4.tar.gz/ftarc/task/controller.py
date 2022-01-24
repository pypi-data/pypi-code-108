#!/usr/bin/env python

import re
import sys
from pathlib import Path
from socket import gethostname

import luigi
from luigi.util import requires

from .bwa import AlignReads
from .core import FtarcTask
from .fastqc import CollectFqMetricsWithFastqc
from .gatk import ApplyBqsr, MarkDuplicates
from .picard import CollectSamMetricsWithPicard, ValidateSamFile
from .resource import FetchKnownSitesVcfs, FetchReferenceFasta
from .samtools import CollectSamMetricsWithSamtools, RemoveDuplicates
from .trimgalore import LocateFastqs, TrimAdapters


class PrintEnvVersions(FtarcTask):
    command_paths = luigi.ListParameter(default=list())
    run_id = luigi.Parameter(default=gethostname())
    sh_config = luigi.DictParameter(default=dict())
    __is_completed = False

    def complete(self):
        return self.__is_completed

    def run(self):
        self.print_log(f'Print environment versions:\t{self.run_id}')
        self.setup_shell(
            run_id=self.run_id, commands=self.command_paths, **self.sh_config
        )
        self.print_env_versions()
        self.__is_completed = True


class PrepareFastqs(luigi.WrapperTask):
    fq_paths = luigi.ListParameter()
    sample_name = luigi.Parameter()
    trim_dir_path = luigi.Parameter(default='.')
    align_dir_path = luigi.Parameter(default='.')
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    trim_galore = luigi.Parameter(default='trim_galore')
    cutadapt = luigi.Parameter(default='cutadapt')
    fastqc = luigi.Parameter(default='fastqc')
    adapter_removal = luigi.BoolParameter(default=True)
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 50

    def requires(self):
        if self.adapter_removal:
            return TrimAdapters(
                fq_paths=self.fq_paths,
                dest_dir_path=str(
                    Path(self.trim_dir_path).joinpath(self.sample_name)
                ),
                sample_name=self.sample_name, pigz=self.pigz,
                pbzip2=self.pbzip2, trim_galore=self.trim_galore,
                cutadapt=self.cutadapt, fastqc=self.fastqc, n_cpu=self.n_cpu,
                memory_mb=self.memory_mb, sh_config=self.sh_config
            )
        else:
            return LocateFastqs(
                fq_paths=self.fq_paths,
                dest_dir_path=str(
                    Path(self.align_dir_path).joinpath(self.sample_name)
                ),
                sample_name=self.sample_name, pigz=self.pigz,
                pbzip2=self.pbzip2, n_cpu=self.n_cpu, sh_config=self.sh_config
            )

    def output(self):
        return self.input()


@requires(PrepareFastqs, FetchReferenceFasta, FetchKnownSitesVcfs)
class PrepareAnalysisReadyCram(luigi.Task):
    sample_name = luigi.Parameter()
    read_group = luigi.DictParameter()
    align_dir_path = luigi.Parameter(default='.')
    bwa = luigi.Parameter(default='bwa')
    samtools = luigi.Parameter(default='samtools')
    gatk = luigi.Parameter(default='gatk')
    reference_name = luigi.Parameter(default='')
    adapter_removal = luigi.BoolParameter(default=True)
    use_bwa_mem2 = luigi.BoolParameter(default=False)
    use_spark = luigi.BoolParameter(default=False)
    save_memory = luigi.BoolParameter(default=False)
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        dest_dir = Path(self.align_dir_path).resolve().joinpath(
            self.sample_name
        )
        output_stem = (
            self.sample_name
            + ('.trim.' if self.adapter_removal else '.')
            + (self.reference_name or Path(self.input()[1][0].path).stem)
            + '.markdup.bqsr'
        )
        return [
            luigi.LocalTarget(dest_dir.joinpath(f'{output_stem}.{s}'))
            for s in [
                'cram', 'cram.crai', 'cram.ValidateSamFile.txt', 'dedup.cram',
                'dedup.cram.crai'
            ]
        ]

    def run(self):
        fa_path = self.input()[1][0].path
        output_cram = Path(self.output()[0].path)
        dest_dir_path = str(output_cram.parent)
        align_target = yield AlignReads(
            fq_paths=[i.path for i in self.input()[0]], fa_path=fa_path,
            dest_dir_path=dest_dir_path, sample_name=self.sample_name,
            read_group=self.read_group,
            output_stem=Path(Path(output_cram.stem).stem).stem,
            bwa=self.bwa, samtools=self.samtools,
            use_bwa_mem2=self.use_bwa_mem2, n_cpu=self.n_cpu,
            memory_mb=self.memory_mb, sh_config=self.sh_config
        )
        markdup_target = yield MarkDuplicates(
            input_sam_path=align_target[0].path, fa_path=fa_path,
            dest_dir_path=dest_dir_path, gatk=self.gatk,
            samtools=self.samtools, use_spark=self.use_spark,
            n_cpu=self.n_cpu, memory_mb=self.memory_mb,
            sh_config=self.sh_config
        )
        bqsr_target = yield ApplyBqsr(
            input_sam_path=markdup_target[0].path, fa_path=fa_path,
            known_sites_vcf_paths=[i[0].path for i in self.input()[2]],
            dest_dir_path=dest_dir_path, gatk=self.gatk,
            samtools=self.samtools, use_spark=self.use_spark,
            save_memory=self.save_memory, n_cpu=self.n_cpu,
            memory_mb=self.memory_mb, sh_config=self.sh_config
        )
        yield [
            RemoveDuplicates(
                input_sam_path=bqsr_target[0].path, fa_path=self.fa_path,
                dest_dir_path=dest_dir_path, samtools=self.samtools,
                n_cpu=self.n_cpu, sh_config=self.sh_config
            ),
            ValidateSamFile(
                sam_path=bqsr_target[0].path, fa_path=self.fa_path,
                dest_dir_path=dest_dir_path, picard=self.gatk,
                n_cpu=self.n_cpu, memory_mb=self.memory_mb,
                sh_config=self.sh_config
            )
        ]


@requires(PrepareAnalysisReadyCram, FetchReferenceFasta,
          PrepareFastqs)
class RunPreprocessingPipeline(luigi.Task):
    sample_name = luigi.Parameter()
    qc_dir_path = luigi.Parameter(default='.')
    fastqc = luigi.Parameter(default='fastqc')
    gatk = luigi.Parameter(default='gatk')
    samtools = luigi.Parameter(default='samtools')
    plot_bamstats = luigi.Parameter(default='plot_bamstats')
    gnuplot = luigi.Parameter(default='gnuplot')
    metrics_collectors = luigi.ListParameter(
        default=['fastqc', 'picard', 'samtools']
    )
    picard_qc_commands = luigi.ListParameter(
        default=[
            'CollectRawWgsMetrics', 'CollectAlignmentSummaryMetrics',
            'CollectInsertSizeMetrics', 'QualityScoreDistribution',
            'MeanQualityByCycle', 'CollectBaseDistributionByCycle',
            'CollectGcBiasMetrics'
        ]
    )
    samtools_qc_commands = luigi.ListParameter(
        default=['coverage', 'flagstat', 'idxstats', 'stats']
    )
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = luigi.IntParameter(default=sys.maxsize)

    def output(self):
        cram = Path(self.input()[0][0].path)
        qc_dir = Path(self.qc_dir_path)
        return (
            self.input()[0] + [
                luigi.LocalTarget(
                    qc_dir.joinpath('fastqc').joinpath(
                        self.sample_name
                    ).joinpath(
                        re.sub(r'\.(fq|fastq)$', '', s) + '_fastqc.html'
                    )
                ) for s in (
                    [Path(i.path).stem for i in self.input()[2]]
                    if 'fastqc' in self.metrics_collectors else list()
                )
            ] + [
                luigi.LocalTarget(
                    qc_dir.joinpath('picard').joinpath(
                        self.sample_name
                    ).joinpath(f'{cram.stem}.{c}.txt')
                ) for c in (
                    self.picard_qc_commands
                    if 'picard' in self.metrics_collectors else list()
                )
            ] + [
                luigi.LocalTarget(
                    qc_dir.joinpath('samtools').joinpath(
                        self.sample_name
                    ).joinpath(f'{cram.stem}.{c}.txt')
                ) for c in (
                    self.samtools_qc_commands
                    if 'samtools' in self.metrics_collectors else list()
                )
            ]
        )

    def run(self):
        qc_dir = Path(self.qc_dir_path)
        if 'fastqc' in self.metrics_collectors:
            yield CollectFqMetricsWithFastqc(
                fq_paths=[i.path for i in self.input()[2]],
                dest_dir_path=str(
                    qc_dir.joinpath('fastqc').joinpath(self.sample_name)
                ),
                fastqc=self.fastqc, n_cpu=self.n_cpu,
                memory_mb=self.memory_mb, sh_config=self.sh_config
            )
        if {'picard', 'samtools'} & set(self.metrics_collectors):
            yield [
                CollectMultipleSamMetrics(
                    sam_path=self.input()[0][0].path,
                    fa_path=self.input()[1][0].path,
                    dest_dir_path=str(
                        qc_dir.joinpath(m).joinpath(self.sample_name)
                    ),
                    metrics_collectors=[m],
                    picard_qc_commands=self.picard_qc_commands,
                    samtools_qc_commands=self.samtools_qc_commands,
                    picard=self.gatk, samtools=self.samtools,
                    plot_bamstats=self.plot_bamstats, gnuplot=self.gnuplot,
                    n_cpu=self.n_cpu, memory_mb=self.memory_mb,
                    sh_config=self.sh_config
                ) for m in self.metrics_collectors
            ]


class CollectMultipleSamMetrics(luigi.WrapperTask):
    sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    metrics_collectors = luigi.ListParameter(default=['picard', 'samtools'])
    picard_qc_commands = luigi.ListParameter(
        default=[
            'CollectRawWgsMetrics', 'CollectAlignmentSummaryMetrics',
            'CollectInsertSizeMetrics', 'QualityScoreDistribution',
            'MeanQualityByCycle', 'CollectBaseDistributionByCycle',
            'CollectGcBiasMetrics'
        ]
    )
    samtools_qc_commands = luigi.ListParameter(
        default=['coverage', 'flagstat', 'idxstats', 'stats']
    )
    picard = luigi.Parameter(default='picard')
    samtools = luigi.Parameter(default='samtools')
    plot_bamstats = luigi.Parameter(default='plot-bamstats')
    gnuplot = luigi.Parameter(default='gnuplot')
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def requires(self):
        return (
            [
                CollectSamMetricsWithPicard(
                    sam_path=self.sam_path, fa_path=self.fa_path,
                    dest_dir_path=self.dest_dir_path, picard_commands=[c],
                    picard=self.picard, n_cpu=self.n_cpu,
                    memory_mb=self.memory_mb, sh_config=self.sh_config
                ) for c in (
                    self.picard_qc_commands
                    if 'picard' in self.metrics_collectors else list()
                )
            ] + [
                CollectSamMetricsWithSamtools(
                    sam_path=self.sam_path, fa_path=self.fa_path,
                    dest_dir_path=self.dest_dir_path, samtools_commands=[c],
                    samtools=self.samtools, plot_bamstats=self.plot_bamstats,
                    gnuplot=self.gnuplot, n_cpu=self.n_cpu,
                    sh_config=self.sh_config
                ) for c in (
                    self.samtools_qc_commands
                    if 'samtools' in self.metrics_collectors else list()
                )
            ]
        )

    def output(self):
        return self.input()


if __name__ == '__main__':
    luigi.run()
