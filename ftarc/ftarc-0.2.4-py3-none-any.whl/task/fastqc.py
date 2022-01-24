#!/usr/bin/env python

import re
from pathlib import Path

import luigi

from .core import FtarcTask


class CollectFqMetricsWithFastqc(FtarcTask):
    fq_paths = luigi.ListParameter()
    dest_dir_path = luigi.Parameter(default='.')
    fastqc = luigi.Parameter(default='fastqc')
    add_fastqc_args = luigi.ListParameter(default=['--nogroup'])
    n_cpu = luigi.IntParameter(default=1)
    memory_mb = luigi.FloatParameter(default=4096)
    sh_config = luigi.DictParameter(default=dict())
    priority = 10

    def output(self):
        return [
            luigi.LocalTarget(o)
            for o in self._generate_output_files(*self.fq_paths)
        ]

    def run(self):
        dest_dir = Path(self.dest_dir_path).resolve()
        for p in self.fq_paths:
            fq = Path(p).resolve()
            run_id = fq.stem
            self.print_log(f'Collect FASTQ metrics using FastQC:\t{run_id}')
            self.setup_shell(
                run_id=run_id, commands=self.fastqc, cwd=dest_dir,
                **self.sh_config,
                env={
                    'JAVA_TOOL_OPTIONS': '-Xmx{}m'.format(int(self.memory_mb))
                }
            )
            self.run_shell(
                args=(
                    f'set -e && {self.fastqc}'
                    + f' --threads {self.n_cpu}'
                    + ''.join(f' {a}' for a in self.add_fastqc_args)
                    + f' --outdir {dest_dir} {p}'
                ),
                input_files_or_dirs=p,
                output_files_or_dirs=list(self._generate_output_files(p))
            )
        tmp_dir = dest_dir.joinpath('?')
        self.remove_files_and_dirs(tmp_dir)

    def _generate_output_files(self, *paths):
        dest_dir = Path(self.dest_dir_path).resolve()
        for p in paths:
            stem = re.sub(r'\.(fq|fastq)$', '', Path(str(p)).stem)
            for e in ['html', 'zip']:
                yield dest_dir.joinpath(f'{stem}_fastqc.{e}')


if __name__ == '__main__':
    luigi.run()
