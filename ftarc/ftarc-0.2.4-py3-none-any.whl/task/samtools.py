#!/usr/bin/env python

import re
from pathlib import Path

import luigi
from luigi.util import requires

from .core import FtarcTask


class SamtoolsFaidx(FtarcTask):
    fa_path = luigi.Parameter()
    samtools = luigi.Parameter(default='samtools')
    add_faidx_args = luigi.ListParameter(default=list())
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        fa = Path(self.fa_path).resolve()
        return luigi.LocalTarget(f'{fa}.fai')

    def run(self):
        run_id = Path(self.fa_path).stem
        self.print_log(f'Index FASTA:\t{run_id}')
        fa = Path(self.fa_path).resolve()
        self.setup_shell(
            run_id=run_id, commands=self.samtools, cwd=fa.parent,
            **self.sh_config
        )
        self.run_shell(
            args=(
                f'set -e && {self.samtools} faidx'
                + ''.join(f' {a}' for a in self.add_faidx_args)
                + f' {fa}'
            ),
            input_files_or_dirs=fa, output_files_or_dirs=f'{fa}.fai'
        )


@requires(SamtoolsFaidx)
class SamtoolsView(FtarcTask):
    input_sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    output_sam_path = luigi.Parameter()
    samtools = luigi.Parameter(default='samtools')
    n_cpu = luigi.IntParameter(default=1)
    add_view_args = luigi.ListParameter(default=list())
    message = luigi.Parameter(default='')
    remove_input = luigi.BoolParameter(default=True)
    index_sam = luigi.BoolParameter(default=False)
    sh_config = luigi.DictParameter(default=dict())
    priority = 90

    def output(self):
        output_sam = Path(self.output_sam_path).resolve()
        return [
            luigi.LocalTarget(output_sam),
            *(
                [
                    luigi.LocalTarget(
                        re.sub(r'\.(cr|b)am$', '.\\1am.\\1ai', str(output_sam))
                    )
                ] if self.index_sam else list()
            )
        ]

    def run(self):
        target_sam = Path(self.input_sam_path)
        run_id = target_sam.stem
        input_sam = target_sam.resolve()
        fa = Path(self.fa_path).resolve()
        output_sam = Path(self.output_sam_path).resolve()
        only_index = (
            self.input_sam_path == self.output_sam_path and self.index_sam
        )
        if self.message:
            message = self.message
        elif only_index:
            message = 'Index {}'.format(input_sam.suffix[1:].upper())
        elif input_sam.suffix == output_sam.suffix:
            message = None
        else:
            message = 'Convert {0} to {1}'.format(
                *[s.suffix[1:].upper() for s in [input_sam, output_sam]]
            )
        if message:
            self.print_log(f'{message}:\t{run_id}')
        dest_dir = output_sam.parent
        self.setup_shell(
            run_id=run_id, commands=self.samtools, cwd=dest_dir,
            **self.sh_config,
            env={'REF_CACHE': str(dest_dir.joinpath('.ref_cache'))}
        )
        if only_index:
            self.samtools_index(
                sam_path=input_sam, samtools=self.samtools, n_cpu=self.n_cpu
            )
        else:
            self.samtools_view(
                input_sam_path=input_sam, fa_path=fa,
                output_sam_path=output_sam, samtools=self.samtools,
                n_cpu=self.n_cpu, add_args=self.add_view_args,
                index_sam=self.index_sam, remove_input=self.remove_input
            )


class RemoveDuplicates(luigi.WrapperTask):
    input_sam_path = luigi.Parameter()
    fa_path = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    samtools = luigi.Parameter(default='samtools')
    add_view_args = luigi.ListParameter(default=['-F', '1024'])
    n_cpu = luigi.IntParameter(default=1)
    remove_input = luigi.BoolParameter(default=False)
    index_sam = luigi.BoolParameter(default=True)
    sh_config = luigi.DictParameter(default=dict())
    priority = 90

    def requires(self):
        return SamtoolsView(
            input_sam_path=str(Path(self.input_sam_path).resolve()),
            fa_path=str(Path(self.fa_path).resolve()),
            output_sam_path=str(
                Path(self.dest_dir_path).resolve().joinpath(
                    Path(self.input_sam_path).stem + '.dedup.cram'
                )
            ),
            samtools=self.samtools, n_cpu=self.n_cpu,
            add_view_args=self.add_view_args, message='Remove duplicates',
            remove_input=self.remove_input, index_sam=self.index_sam,
            sh_config=self.sh_config
        )

    def output(self):
        return self.input()


class CollectSamMetricsWithSamtools(FtarcTask):
    sam_path = luigi.Parameter()
    fa_path = luigi.Parameter(default='')
    dest_dir_path = luigi.Parameter(default='.')
    samtools_commands = luigi.ListParameter(
        default=['coverage', 'flagstat', 'idxstats', 'stats']
    )
    samtools = luigi.Parameter(default='samtools')
    plot_bamstats = luigi.Parameter(default='plot-bamstats')
    gnuplot = luigi.Parameter(default='gnuplot')
    add_samtools_command_args = luigi.DictParameter(default={'depth': ['-a']})
    add_faidx_args = luigi.ListParameter(default=list())
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def requires(self):
        if self.fa_path:
            return SamtoolsView(
                fa_path=self.fa_path, samtools=self.samtools,
                add_faidx_args=self.add_faidx_args, sh_config=self.sh_config
            )
        else:
            return super().requires()

    def output(self):
        sam_name = Path(self.sam_path).name
        dest_dir = Path(self.dest_dir_path).resolve()
        return (
            [
                luigi.LocalTarget(dest_dir.joinpath(f'{sam_name}.{c}.txt'))
                for c in self.samtools_commands
            ] + (
                [luigi.LocalTarget(dest_dir.joinpath(f'{sam_name}.stats'))]
                if 'stats' in self.samtools_commands else list()
            )
        )

    def run(self):
        run_id = Path(self.sam_path).name
        self.print_log(f'Collect SAM metrics using Samtools:\t{run_id}')
        sam = Path(self.sam_path).resolve()
        fa = (Path(self.fa_path).resolve() if self.fa_path else None)
        dest_dir = Path(self.dest_dir_path).resolve()
        ref_cache = str(sam.parent.joinpath('.ref_cache'))
        for c in self.samtools_commands:
            output_txt = dest_dir.joinpath(
                Path(self.sam_path).name + f'.{c}.txt'
            )
            self.setup_shell(
                run_id=f'{run_id}.{c}',
                commands=(
                    [self.samtools, self.gnuplot]
                    if c == 'stats' else self.samtools
                ),
                cwd=dest_dir, **self.sh_config, env={'REF_CACHE': ref_cache}
            )
            self.run_shell(
                args=(
                    f'set -eo pipefail && {self.samtools} {c}'
                    + (
                        f' --reference {fa}' if (
                            fa is not None
                            and c in {'coverage', 'depth', 'stats'}
                        ) else ''
                    )
                    + (
                        f' -@ {self.n_cpu}'
                        if c in {'flagstat', 'idxstats', 'stats'} else ''
                    )
                    + ''.join(
                        f' {a}' for a
                        in (self.add_samtools_command_args.get(c) or list())
                    )
                    + f' {sam} | tee {output_txt}'
                ),
                input_files_or_dirs=sam, output_files_or_dirs=output_txt
            )
            if c == 'stats':
                plot_dir = dest_dir.joinpath(output_txt.stem)
                self.run_shell(
                    args=(
                        f'set -e && {self.plot_bamstats}'
                        + ''.join(
                            f' {a}' for a in (
                                self.add_samtools_command_args.get(
                                    'plot-bamstats'
                                ) or list()
                            )
                        )
                        + f' --prefix {plot_dir}/index {output_txt}'
                    ),
                    input_files_or_dirs=output_txt,
                    output_files_or_dirs=[
                        plot_dir, plot_dir.joinpath('index.html')
                    ]
                )


if __name__ == '__main__':
    luigi.run()
