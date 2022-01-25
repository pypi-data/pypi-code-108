# Copyright (c) 2022 Ed Harry, Wellcome Sanger Institute, Genome Research Limited
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import sys
from subprocess import PIPE, Popen
from itertools import chain

import click
import pysam

pysam.set_verbosity(0)


@click.command()
@click.argument("sam_input", type=click.File("rb"))
@click.argument("juicer_output", type=click.File("w"))
@click.option("--threads", "-t", default=1, show_default=True)
@click.option("--memory", "-m", default="1G", show_default=True)
@click.version_option()
def cli(sam_input, juicer_output, threads, memory):
    try:

        def Pairs(it):
            while True:
                a = next(it, None)
                b = next(it, None)
                if a is not None and b is not None:
                    yield a, b
                else:
                    break

        def SAMPairs(file_name):
            for r1, r2 in Pairs(pysam.AlignmentFile(file_name, "rb")):
                if r1.query_name != r2.query_name or r1.is_read2 or r2.is_read1:
                    raise Exception("Read collation error")
                yield r1, r2

        fifo_name = ".HiLineToJuicer." + str(os.getpid()) + ".fifo"
        os.mkfifo(fifo_name)
        read, write = os.pipe()

        with os.fdopen(
            write, "w", encoding="utf-8", errors="replace"
        ) as f_write, os.fdopen(
            read, "r", encoding="utf-8", errors="replace"
        ) as f_read:

            in_process = Popen(
                f"samtools view -u@ {threads} -F 0xF0C -f 1 -o {fifo_name} -".split(),
                stdin=Popen(
                    f"samtools collate -Ouf@ {threads} -".split(),
                    stdin=Popen(
                        f"samtools view -u@ {threads} -F 0xF0C -f 1 -".split(),
                        stdin=sam_input,
                        stdout=PIPE,
                        stderr=sys.stderr,
                    ).stdout,
                    stdout=PIPE,
                    stderr=sys.stderr,
                ).stdout,
                stderr=sys.stderr,
            )
            out_process = Popen(
                "cut -f 2-".split(),
                stdin=Popen(
                    f"sort -S {memory} --parallel={threads} -k 1n,1n -k 4n,4n".split(),
                    stdin=f_read,
                    stderr=sys.stderr,
                    stdout=PIPE,
                ).stdout,
                stderr=sys.stderr,
                stdout=juicer_output,
            )

            reads = SAMPairs(fifo_name)
            for r1_tmp, r2_tmp in reads:
                has_rf = r1_tmp.has_tag("rf") and r2_tmp.has_tag("rf")
                if not has_rf:
                    print(
                        "No 'rf' tag found in first read pair, assuming no restriction-fragment information (i.e. DNASE data-set)."
                    )

                for r1, r2 in chain(((r1_tmp, r2_tmp),), reads):
                    r1.query_name += "/1"
                    r2.query_name += "/2"

                    r1, r2 = (
                        (r2, r1)
                        if r1.reference_id > r2.reference_id
                        or (
                            r1.reference_id == r2.reference_id
                            and r1.reference_start > r2.reference_start
                        )
                        else (r1, r2)
                    )

                    print(
                        r1.reference_id,
                        1 if r1.is_reverse else 0,
                        r1.reference_name,
                        r1.reference_start + 1,
                        r1.get_tag("rf")[0] if has_rf else r1.reference_start + 1,
                        1 if r2.is_reverse else 0,
                        r2.reference_name,
                        r2.reference_start + 1,
                        r2.get_tag("rf")[0] if has_rf else r2.reference_start + 1,
                        r1.mapping_quality,
                        r1.cigarstring,
                        r1.query_sequence,
                        r2.mapping_quality,
                        r2.cigarstring,
                        r2.query_sequence,
                        r1.query_name,
                        r2.query_name,
                        sep="\t",
                        file=f_write,
                    )


        with in_process as in_proc, out_process as out_proc:
            in_ret = in_proc.wait()
            out_ret = out_proc.wait()

        if in_ret != 0:
            raise Exception("Input process error")
        if out_ret != 0:
            raise Exception("Output process error")
    finally:
        os.unlink(fifo_name)
