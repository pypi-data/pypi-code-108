#!/usr/bin/env python

from pathlib import Path

import luigi
from luigi.util import requires

from .core import FtarcTask


class CreateSequenceDictionary(FtarcTask):
    fa_path = luigi.Parameter()
    gatk = luigi.Parameter(default='gatk')
    add_createsequencedictionary_args = luigi.ListParameter(default=list())
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        fa = Path(self.fa_path).resolve()
        return luigi.LocalTarget(fa.parent.joinpath(f'{fa.stem}.dict'))

    def run(self):
        run_id = Path(self.fa_path).stem
        self.print_log(f'Create a sequence dictionary:\t{run_id}')
        fa = Path(self.fa_path).resolve()
        seq_dict_path = self.output().path
        self.setup_shell(
            run_id=run_id, commands=self.gatk, cwd=fa.parent, **self.sh_config,
            env={
                'JAVA_TOOL_OPTIONS': self.generate_gatk_java_options(
                    n_cpu=self.n_cpu, memory_mb=self.memory_mb
                )
            }
        )
        self.run_shell(
            args=(
                f'set -e && {self.gatk} CreateSequenceDictionary'
                + f' --REFERENCE {fa}'
                + ''.join(
                    f' {a}' for a in self.add_createsequencedictionary_args
                )
                + f' --OUTPUT {seq_dict_path}'
            ),
            input_files_or_dirs=fa, output_files_or_dirs=seq_dict_path
        )


@requires(CreateSequenceDictionary)
class ValidateSamFile(FtarcTask):
    sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    picard = luigi.Parameter(default='picard')
    add_validatesamfile_args = luigi.ListParameter(
        default=['--MODE', 'VERBOSE', '--IGNORE', 'MISSING_TAG_NM']
    )
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = luigi.IntParameter(default=100)

    def output(self):
        return luigi.LocalTarget(
            Path(self.dest_dir_path).resolve().joinpath(
                Path(self.sam_path).name + '.ValidateSamFile.txt'
            )
        )

    def run(self):
        run_id = Path(self.sam_path).name
        self.print_log(f'Validate a SAM file:\t{run_id}')
        sam = Path(self.sam_path).resolve()
        fa = Path(self.fa_path).resolve()
        fa_dict = fa.parent.joinpath(f'{fa.stem}.dict')
        dest_dir = Path(self.dest_dir_path).resolve()
        output_txt = Path(self.output().path)
        self.setup_shell(
            run_id=run_id, commands=self.picard, cwd=dest_dir,
            **self.sh_config,
            env={
                'JAVA_TOOL_OPTIONS': self.generate_gatk_java_options(
                    n_cpu=self.n_cpu, memory_mb=self.memory_mb
                )
            }
        )
        self.run_shell(
            args=(
                f'set -e && {self.picard} ValidateSamFile'
                + f' --INPUT {sam}'
                + f' --REFERENCE_SEQUENCE {fa}'
                + ''.join(f' {a}' for a in self.add_validatesamfile_args)
                + f' --OUTPUT {output_txt}'
            ),
            input_files_or_dirs=[sam, fa, fa_dict],
            output_files_or_dirs=output_txt
        )


@requires(CreateSequenceDictionary)
class CollectSamMetricsWithPicard(FtarcTask):
    sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    picard_commands = luigi.ListParameter(
        default=[
            'CollectRawWgsMetrics', 'CollectAlignmentSummaryMetrics',
            'CollectInsertSizeMetrics', 'QualityScoreDistribution',
            'MeanQualityByCycle', 'CollectBaseDistributionByCycle',
            'CollectGcBiasMetrics'
        ]
    )
    picard = luigi.Parameter(default='picard')
    add_picard_command_args = luigi.DictParameter(
        default={'CollectRawWgsMetrics': ['--INCLUDE_BQ_HISTOGRAM', 'true']}
    )
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 100

    def output(self):
        sam_name = Path(self.sam_path).name
        dest_dir = Path(self.dest_dir_path).resolve()
        return (
            [
                luigi.LocalTarget(dest_dir.joinpath(f'{sam_name}.{c}.txt'))
                for c in self.picard_commands
            ] + [
                luigi.LocalTarget(
                    dest_dir.joinpath(f'{sam_name}.{c}.summary.txt')
                ) for c in self.picard_commands
                if c in {'CollectGcBiasMetrics'}
            ] + [
                luigi.LocalTarget(dest_dir.joinpath(f'{sam_name}.{c}.pdf'))
                for c in self.picard_commands if c in {
                    'MeanQualityByCycle', 'QualityScoreDistribution',
                    'CollectBaseDistributionByCycle',
                    'CollectInsertSizeMetrics'
                }
            ]
        )

    def run(self):
        run_id = Path(self.sam_path).name
        self.print_log(f'Collect SAM metrics using Picard:\t{run_id}')
        sam = Path(self.sam_path).resolve()
        fa = Path(self.fa_path).resolve()
        fa_dict = fa.parent.joinpath(f'{fa.stem}.dict')
        for c, o in zip(self.picard_commands, self.output()):
            output_txt = Path(o.path)
            self.setup_shell(
                run_id=f'{run_id}.{c}', commands=f'{self.picard} {c}',
                cwd=output_txt.parent, **self.sh_config,
                env={
                    'JAVA_TOOL_OPTIONS': self.generate_gatk_java_options(
                        n_cpu=self.n_cpu, memory_mb=self.memory_mb
                    )
                }
            )
            prefix = str(output_txt.parent.joinpath(output_txt.stem))
            if c in {'MeanQualityByCycle', 'QualityScoreDistribution',
                     'CollectBaseDistributionByCycle'}:
                output_args = [
                    '--CHART_OUTPUT', f'{prefix}.pdf',
                    '--OUTPUT', f'{prefix}.txt'
                ]
            elif c == 'CollectInsertSizeMetrics':
                output_args = [
                    '--Histogram_FILE', f'{prefix}.pdf',
                    '--OUTPUT', f'{prefix}.txt'
                ]
            elif c == 'CollectGcBiasMetrics':
                output_args = [
                    '--CHART_OUTPUT', f'{prefix}.pdf',
                    '--SUMMARY_OUTPUT', f'{prefix}.summary.txt',
                    '--OUTPUT', f'{prefix}.txt'
                ]
            else:
                output_args = ['--OUTPUT', f'{prefix}.txt']
            self.run_shell(
                args=(
                    f'set -e && {self.picard} {c}'
                    + f' --INPUT {sam}'
                    + f' --REFERENCE_SEQUENCE {fa}'
                    + ''.join(
                        f' {a}' for a in [
                            *(self.add_picard_command_args.get(c) or list()),
                            *output_args
                        ]
                    )
                ),
                input_files_or_dirs=[sam, fa, fa_dict],
                output_files_or_dirs=[
                    a for a in output_args if a.endswith(('.txt', '.pdf'))
                ]
            )


if __name__ == '__main__':
    luigi.run()
