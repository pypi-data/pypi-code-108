#!/usr/bin/env python

import re
from pathlib import Path

import luigi

from .core import FtarcTask
from .picard import CreateSequenceDictionary
from .samtools import SamtoolsFaidx


class FetchReferenceFasta(luigi.Task):
    fa_path = luigi.Parameter()
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    samtools = luigi.Parameter(default='samtools')
    gatk = luigi.Parameter(default='gatk')
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 100

    def requires(self):
        return FetchResourceFile(
            src_path=self.fa_path, pigz=self.pigz, pbzip2=self.pbzip2,
            n_cpu=self.n_cpu, sh_config=self.sh_config
        )

    def output(self):
        fa = Path(self.input().path)
        return [
            luigi.LocalTarget(fa),
            luigi.LocalTarget(f'{fa}.fai'),
            luigi.LocalTarget(fa.parent.joinpath(f'{fa.stem}.dict'))
        ]

    def run(self):
        fa_path = self.input().path
        yield [
            SamtoolsFaidx(
                fa_path=fa_path, samtools=self.samtools,
                sh_config=self.sh_config
            ),
            CreateSequenceDictionary(
                fa_path=fa_path, gatk=self.gatk, n_cpu=self.n_cpu,
                memory_mb=self.memory_mb, sh_config=self.sh_config
            )
        ]


class FetchResourceFile(FtarcTask):
    src_path = luigi.Parameter()
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        return luigi.LocalTarget(
            Path(self.src_path).parent.joinpath(
                re.sub(r'\.(gz|bz2)$', '', Path(self.src_path).name)
            )
        )

    def run(self):
        dest_file = Path(self.output().path)
        run_id = dest_file.stem
        self.print_log(f'Create a resource:\t{run_id}')
        self.setup_shell(
            run_id=run_id, commands=[self.pigz, self.pbzip2],
            cwd=dest_file.parent, **self.sh_config
        )
        if self.src_path.endswith('.gz'):
            a = (
                f'set -e && {self.pigz} -p {self.n_cpu} -dc {self.src_path}'
                + f' > {dest_file}'
            )
        elif self.src_path.endswith('.bz2'):
            a = (
                f'set -e && {self.pbzip2} -p{self.n_cpu} -dc {self.src_path}'
                + f' > {dest_file}'
            )
        else:
            a = f'set -e && cp {self.src_path} {dest_file}'
        self.run_shell(
            args=a, input_files_or_dirs=self.src_path,
            output_files_or_dirs=dest_file
        )


class FetchResourceVcf(FtarcTask):
    src_path = luigi.Parameter()
    bgzip = luigi.Parameter(default='bgzip')
    tabix = luigi.Parameter(default='tabix')
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def output(self):
        dest_vcf = Path(self.src_path).parent.joinpath(
            re.sub(r'\.(gz|bgz)$', '.gz', Path(self.src_path).name)
        )
        return [luigi.LocalTarget(f'{dest_vcf}{s}') for s in ['', '.tbi']]

    def run(self):
        dest_vcf = Path(self.output()[0].path)
        run_id = Path(dest_vcf.stem).stem
        self.print_log(f'Create a VCF:\t{run_id}')
        self.setup_shell(
            run_id=run_id, commands=[self.bgzip, self.tabix],
            cwd=dest_vcf.parent, **self.sh_config
        )
        self.run_shell(
            args=(
                f'set -e && cp {self.src_path} {dest_vcf}'
                if self.src_path.endswith(('.gz', '.bgz')) else (
                    f'set -e && {self.bgzip} -@ {self.n_cpu}'
                    + f' -c {self.src_path} > {dest_vcf}'
                )
            ),
            input_files_or_dirs=self.src_path, output_files_or_dirs=dest_vcf
        )
        self.run_shell(
            args=f'set -e && {self.tabix} --preset vcf {dest_vcf}',
            input_files_or_dirs=dest_vcf,
            output_files_or_dirs=f'{dest_vcf}.tbi'
        )


class FetchKnownSitesVcfs(luigi.WrapperTask):
    known_sites_vcf_paths = luigi.ListParameter()
    bgzip = luigi.Parameter(default='bgzip')
    tabix = luigi.Parameter(default='tabix')
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 70

    def requires(self):
        return [
            FetchResourceVcf(
                src_path=p, bgzip=self.bgzip, tabix=self.tabix,
                n_cpu=self.n_cpu, sh_config=self.sh_config
            ) for p in self.known_sites_vcf_paths
        ]

    def output(self):
        return self.input()


if __name__ == '__main__':
    luigi.run()
