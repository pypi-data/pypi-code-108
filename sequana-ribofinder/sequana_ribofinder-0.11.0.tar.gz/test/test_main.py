import easydev
import os
import tempfile
import subprocess
import sys

from . import test_dir

sharedir = f"{test_dir}/data"

def test_standalone_subprocess():
    directory = tempfile.TemporaryDirectory()
    cmd = """sequana_ribofinder --input-directory {} 
            --working-directory {} --force""".format(sharedir, directory.name)
    subprocess.call(cmd.split())


def test_standalone_script():
    directory = tempfile.TemporaryDirectory()
    import sequana_pipelines.ribofinder.main as m
    sys.argv = ["test", "--input-directory", sharedir, 
            "--working-directory", directory.name, "--force", "--rRNA-file", sharedir+"feature.fasta"]
    m.main()


def test_full_rRNA_file():
    with tempfile.TemporaryDirectory() as directory:
        wk = directory
        cmd = f"sequana_ribofinder --input-directory {sharedir} "
        cmd += f"--working-directory {wk}  --force --rRNA-file {sharedir}/feature.fasta"
        subprocess.call(cmd.split())
        stat = subprocess.call("sh ribofinder.sh".split(), cwd=wk)
        assert os.path.exists(wk + "/summary.html")

def test_full_rRNA_extract():
    with tempfile.TemporaryDirectory() as directory:
        wk = directory
        cmd = f"sequana_ribofinder --input-directory {sharedir} "
        cmd += f"--working-directory {wk}  --force --reference-file {sharedir}/Lepto.fa --gff-file {sharedir}/Lepto.gff"
        subprocess.call(cmd.split())
        stat = subprocess.call("sh ribofinder.sh".split(), cwd=wk)
        assert os.path.exists(wk + "/summary.html")

def test_version():
    cmd = "sequana_ribofinder --version"
    subprocess.call(cmd.split())


