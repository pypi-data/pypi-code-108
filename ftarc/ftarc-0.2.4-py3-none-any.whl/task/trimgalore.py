#!/usr/bin/env python

import re
from itertools import product
from pathlib import Path

import luigi

from .core import FtarcTask


class TrimAdapters(FtarcTask):
    fq_paths = luigi.ListParameter()
    dest_dir_path = luigi.Parameter(default='.')
    sample_name = luigi.Parameter(default='')
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    trim_galore = luigi.Parameter(default='trim_galore')
    cutadapt = luigi.Parameter(default='cutadapt')
    fastqc = luigi.Parameter(default='fastqc')
    add_trim_galore_args = luigi.ListParameter(default=list())
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 50

    def output(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        standard_suffixes = tuple(
            ''.join(t) for t in product(['.fastq', '.fq'], ['.gz', ''])
        )
        return [
            luigi.LocalTarget(
                dest_dir.joinpath(
                    (
                        re.sub(r'\.(fastq|fq)$', '', Path(p).stem)
                        if p.endswith(standard_suffixes) else Path(p).name
                    ) + f'_val_{i + 1}.fq.gz'
                )
            ) for i, p in enumerate(self.fq_paths)
        ]

    def run(self):
        run_id = (
            self.sample_name
            or Path(Path(Path(self.fq_paths[0]).stem).stem).stem
        )
        self.print_log(f'Trim adapters:\t{run_id}')
        output_fq_paths = [o.path for o in self.output()]
        run_dir = Path(output_fq_paths[0]).parent
        work_fq_paths = [
            (
                str(run_dir.joinpath(Path(p).stem + '.gz'))
                if p.endswith('.bz2') else p
            ) for p in self.fq_paths
        ]
        self.setup_shell(
            run_id=run_id,
            commands=[
                self.pigz, self.pbzip2, self.trim_galore, self.cutadapt,
                self.fastqc
            ],
            cwd=run_dir, **self.sh_config,
            env={'JAVA_TOOL_OPTIONS': '-Xmx{}m'.format(int(self.memory_mb))}
        )
        for i, o in zip(self.fq_paths, work_fq_paths):
            if i.endswith('.bz2'):
                self.bzip2_to_gzip(
                    src_bz2_path=i, dest_gz_path=o, pbzip2=self.pbzip2,
                    pigz=self.pigz, n_cpu=self.n_cpu
                )
        self.run_shell(
            args=(
                f'set -e && {self.trim_galore}'
                + f' --path_to_cutadapt {self.cutadapt}'
                + f' --cores {self.n_cpu}'
                + (' --paired' if len(work_fq_paths) > 1 else '')
                + ''.join(f' {a}' for a in self.add_trim_galore_args)
                + f' --output_dir {run_dir}'
                + ''.join(f' {p}' for p in work_fq_paths)
            ),
            input_files_or_dirs=work_fq_paths,
            output_files_or_dirs=[*output_fq_paths, run_dir]
        )


class LocateFastqs(FtarcTask):
    fq_paths = luigi.Parameter()
    dest_dir_path = luigi.Parameter(default='.')
    sample_name = luigi.Parameter(default='')
    pigz = luigi.Parameter(default='pigz')
    pbzip2 = luigi.Parameter(default='pbzip2')
    n_cpu = luigi.IntParameter(default=1)
    sh_config = luigi.DictParameter(default=dict())
    priority = 50

    def output(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        return [
            luigi.LocalTarget(
                dest_dir.joinpath(Path(p).stem + '.gz')
                if p.endswith('.bz2') else Path(p)
            ) for p in self.fq_paths
        ]

    def run(self):
        run_id = Path(Path(Path(self.fq_paths[0]).stem).stem).stem
        self.print_log(f'Bunzip2 and Gzip a file:\t{run_id}')
        self.setup_shell(
            run_id=run_id, commands=[self.pigz, self.pbzip2],
            cwd=self.dest_dir_path, **self.sh_config
        )
        for p, o in zip(self.fq_paths, self.output()):
            if p != o.path:
                self.bzip2_to_gzip(
                    src_bz2_path=p, dest_gz_path=o.path, pbzip2=self.pbzip2,
                    pigz=self.pigz, n_cpu=self.n_cpu
                )


if __name__ == '__main__':
    luigi.run()
