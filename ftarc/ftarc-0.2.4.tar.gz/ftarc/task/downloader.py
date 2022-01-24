#!/usr/bin/env python

import re
from itertools import product
from pathlib import Path
from socket import gethostname

import luigi
from luigi.util import requires

from .bwa import CreateBwaIndices
from .core import FtarcTask
from .picard import CreateSequenceDictionary
from .resource import FetchResourceVcf
from .samtools import SamtoolsFaidx


class DownloadResourceFiles(FtarcTask):
    src_urls = luigi.ListParameter()
    dest_dir_path = luigi.Parameter(default='.')
    run_id = luigi.Parameter(default=gethostname())
    wget = luigi.Parameter(default='wget')
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    bgzip = luigi.Parameter(default='bgzip')
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def output(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        target_paths = list()
        for u in self.src_urls:
            p = str(dest_dir.joinpath(Path(u).name))
            if u.endswith(tuple([f'.{a}.{b}' for a, b
                                 in product(('fa', 'fna', 'fasta', 'txt'),
                                            ('gz', 'bz2'))])):
                target_paths.append(re.sub(r'\.(gz|bz2)$', '', p))
            elif u.endswith('.bgz'):
                target_paths.append(re.sub(r'\.bgz$', '.gz', p))
            elif u.endswith(('.vcf', '.bed')):
                target_paths.append(f'{p}.gz')
            else:
                target_paths.append(p)
        return [luigi.LocalTarget(p) for p in target_paths]

    def run(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        self.print_log(f'Download resource files:\t{dest_dir}')
        self.setup_shell(
            run_id=self.run_id,
            commands=[self.wget, self.bgzip, self.pigz, self.pbzip2],
            cwd=dest_dir, **self.sh_config
        )
        for u, o in zip(self.src_urls, self.output()):
            t = dest_dir.joinpath(
                (Path(u).stem + '.gz') if u.endswith('.bgz') else Path(u).name
            )
            self.run_shell(
                args=f'set -e && {self.wget} -qSL -O {t} {u}',
                output_files_or_dirs=t
            )
            if str(t) == o.path:
                pass
            elif t.suffix != '.gz' and o.path.endswith('.gz'):
                self.run_shell(
                    args=f'set -e && {self.bgzip} -@ {self.n_cpu} {t}',
                    input_files_or_dirs=t, output_files_or_dirs=o.path
                )
            elif o.path.endswith(('.fa', '.fna', '.fasta', '.txt')):
                self.run_shell(
                    args=(
                        f'set -e && {self.pbzip2} -p{self.n_cpu} -d {t}'
                        if t.suffix == '.bz2' else
                        f'set -e && {self.pigz} -p {self.n_cpu} -d {t}'
                    ),
                    input_files_or_dirs=t, output_files_or_dirs=o.path
                )


@requires(DownloadResourceFiles)
class DownloadAndIndexReferenceFasta(luigi.Task):
    samtools = luigi.Parameter(default='samtools')
    gatk = luigi.Parameter(default='gatk')
    bwa = luigi.Parameter(default='bwa')
    use_bwa_mem2 = luigi.BoolParameter(default=False)
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def output(self):
        bwa_suffixes = (
            ['0123', 'amb', 'ann', 'pac', 'bwt.2bit.64']
            if self.use_bwa_mem2 else ['pac', 'bwt', 'ann', 'amb', 'sa']
        )
        fa = [
            Path(i.path) for i in self.input()
            if i.path.endswith(('.fa', '.fna', '.fasta'))
        ][0]
        return (
            self.input() + [
                luigi.LocalTarget(p) for p in [
                    f'{fa}.fai', fa.parent.joinpath(f'{fa.stem}.dict'),
                    *[f'{fa}.{s}' for s in bwa_suffixes]
                ]
            ]
        )

    def run(self):
        fa_path = self.input()[0].path
        yield [
            SamtoolsFaidx(
                fa_path=fa_path, samtools=self.samtools,
                sh_config=self.sh_config
            ),
            CreateSequenceDictionary(
                fa_path=fa_path, gatk=self.gatk, n_cpu=self.n_cpu,
                memory_mb=self.memory_mb, sh_config=self.sh_config
            ),
            CreateBwaIndices(
                fa_path=fa_path, bwa=self.bwa, use_bwa_mem2=self.use_bwa_mem2,
                sh_config=self.sh_config
            )
        ]


@requires(DownloadResourceFiles)
class DownloadAndIndexResourceVcfs(luigi.Task):
    bgzip = luigi.Parameter(default='bgzip')
    tabix = luigi.Parameter(default='tabix')
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def output(self):
        return (
            self.input() + [
                luigi.LocalTarget(f'{i.path}.tbi') for i in self.input()
                if i.path.endswith('.vcf.gz')
            ]
        )

    def run(self):
        yield [
            FetchResourceVcf(
                src_path=i.path, bgzip=self.bgzip, tabix=self.tabix,
                n_cpu=self.n_cpu, sh_config=self.sh_config
            ) for i in self.input() if i.path.endswith('.vcf.gz')
        ]


class DownloadAndProcessResourceFiles(luigi.WrapperTask):
    src_url_dict = luigi.DictParameter()
    dest_dir_path = luigi.Parameter(default='.')
    wget = luigi.Parameter(default='wget')
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    bgzip = luigi.Parameter(default='bgzip')
    tabix = luigi.Parameter(default='tabix')
    samtools = luigi.Parameter(default='samtools')
    gatk = luigi.Parameter(default='gatk')
    bwa = luigi.Parameter(default='bwa')
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    use_bwa_mem2 = luigi.BoolParameter(default=False)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def requires(self):
        return [
            DownloadAndIndexReferenceFasta(
                src_urls=[
                    self.src_url_dict['reference_fa'],
                    self.src_url_dict['reference_fa_alt']
                ],
                dest_dir_path=self.dest_dir_path,
                run_id=Path(self.src_url_dict['reference_fa']).stem,
                wget=self.wget, pigz=self.pigz, pbzip2=self.pbzip2,
                bgzip=self.bgzip, samtools=self.samtools, gatk=self.gatk,
                bwa=self.bwa, use_bwa_mem2=self.use_bwa_mem2, n_cpu=self.n_cpu,
                memory_mb=self.memory_mb, sh_config=self.sh_config
            ),
            DownloadAndIndexResourceVcfs(
                src_urls=[
                    v for k, v in self.src_url_dict.items()
                    if k not in {'reference_fa', 'reference_fa_alt'}
                ],
                dest_dir_path=self.dest_dir_path, run_id='others',
                wget=self.wget, pigz=self.pigz, pbzip2=self.pbzip2,
                bgzip=self.bgzip, tabix=self.tabix, n_cpu=self.n_cpu,
                sh_config=self.sh_config
            )
        ]

    def output(self):
        return self.input()


if __name__ == '__main__':
    luigi.run()
