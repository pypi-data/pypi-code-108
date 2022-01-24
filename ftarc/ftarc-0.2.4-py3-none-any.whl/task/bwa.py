#!/usr/bin/env python

from pathlib import Path

import luigi
from luigi.util import requires

from .core import FtarcTask
from .samtools import SamtoolsFaidx


class CreateBwaIndices(FtarcTask):
    fa_path = luigi.Parameter()
    bwa = luigi.Parameter(default='bwa')
    use_bwa_mem2 = luigi.BoolParameter(default=False)
    add_index_args = luigi.ListParameter(default=list())
    sh_config = luigi.DictParameter(default=dict())
    priority = 100

    def output(self):
        return [
            luigi.LocalTarget(f'{self.fa_path}.{s}') for s in (
                ['0123', 'amb', 'ann', 'pac', 'bwt.2bit.64']
                if self.use_bwa_mem2 else ['pac', 'bwt', 'ann', 'amb', 'sa']
            )
        ]

    def run(self):
        fa = Path(self.fa_path)
        run_id = fa.stem
        self.print_log(f'Create BWA indices:\t{run_id}')
        self.setup_shell(
            run_id=run_id, commands=self.bwa, cwd=fa.parent, **self.sh_config
        )
        self.run_shell(
            args=(
                f'set -e && {self.bwa} index'
                + ''.join(f' {a}' for a in self.add_index_args)
                + f' {fa}'
            ),
            input_files_or_dirs=fa,
            output_files_or_dirs=[o.path for o in self.output()]
        )


@requires(SamtoolsFaidx, CreateBwaIndices)
class AlignReads(FtarcTask):
    fq_paths = luigi.ListParameter()
    fa_path = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    sample_name = luigi.Parameter()
    read_group = luigi.DictParameter(default=dict())
    output_stem = luigi.Parameter(default='')
    bwa = luigi.Parameter(default='bwa')
    samtools = luigi.Parameter(default='samtools')
    use_bwa_mem2 = luigi.BoolParameter(default=False)
    add_mem_args = luigi.ListParameter(default=['-P', '-T', '0'])
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        output_cram_name = '{}.cram'.format(
            self.output_stem if self.output_stem else
            (self.sample_name + '.' + Path(self.fa_path).stem)
        )
        return [
            luigi.LocalTarget(dest_dir.joinpath(output_cram_name)),
            luigi.LocalTarget(dest_dir.joinpath(output_cram_name + '.crai'))
        ]

    def run(self):
        output_cram = Path(self.output()[0].path)
        run_id = output_cram.stem
        self.print_log(f'Align reads:\t{run_id}')
        memory_mb_per_thread = int(self.memory_mb / self.n_cpu / 8)
        fqs = [Path(p).resolve() for p in self.fq_paths]
        rg = '\\t'.join(
            [
                '@RG',
                'ID:{}'.format(self.read_group.get('ID') or 0),
                'PU:{}'.format(self.read_group.get('PU') or 'UNIT-0'),
                'SM:{}'.format(
                    self.read_group.get('SM') or self.sample_name or 'SAMPLE'
                ),
                'PL:{}'.format(self.read_group.get('PL') or 'ILLUMINA'),
                'LB:{}'.format(self.read_group.get('LB') or 'LIBRARY-0')
            ] + [
                f'{k}:{v}' for k, v in self.read_group.items()
                if k not in ['ID', 'PU', 'SM', 'PL', 'LB']
            ]
        )
        fa = Path(self.fa_path).resolve()
        bwa_indices = [
            Path(f'{fa}.{s}') for s in (
                ['0123', 'amb', 'ann', 'pac', 'bwt.2bit.64']
                if self.use_bwa_mem2 else ['pac', 'bwt', 'ann', 'amb', 'sa']
            )
        ]
        dest_dir = output_cram.parent
        self.setup_shell(
            run_id=run_id, commands=[self.bwa, self.samtools], cwd=dest_dir,
            **self.sh_config,
            env={'REF_CACHE': str(dest_dir.joinpath('.ref_cache'))}
        )
        self.run_shell(
            args=(
                f'set -eo pipefail && {self.bwa} mem'
                + f' -t {self.n_cpu}'
                + ''.join(f' {a}' for a in self.add_mem_args)
                + f' -R \'{rg}\''
                + f' {fa}'
                + ''.join(f' {a}' for a in fqs)
                + f' | {self.samtools} view -T {fa} -CS -o - -'
                + f' | {self.samtools} sort -@ {self.n_cpu}'
                + f' -m {memory_mb_per_thread}M -O CRAM'
                + f' -T {output_cram}.sort -o {output_cram} -'
            ),
            input_files_or_dirs=[*fqs, fa, *bwa_indices],
            output_files_or_dirs=[output_cram, dest_dir]
        )
        self.samtools_index(
            sam_path=output_cram, samtools=self.samtools, n_cpu=self.n_cpu
        )


if __name__ == '__main__':
    luigi.run()
