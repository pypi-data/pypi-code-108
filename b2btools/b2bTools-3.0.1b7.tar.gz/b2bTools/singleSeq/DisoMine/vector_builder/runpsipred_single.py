# -*- coding: utf-8 -*-
import os
import tempfile
import subprocess, sys

cwd = os.path.dirname(os.path.abspath(__file__))

DATADIR = cwd + '/psipred/data/'
TEMPDIR = cwd + '/psipred/tmp/'

if sys.platform == 'linux':
    SEQ2MTX = cwd + '/psipred/bin/linux/seq2mtx'
    PSIPRED = cwd + '/psipred/bin/linux/psipred'
    PSIPASS2 = cwd + '/psipred/bin/linux/psipass2'
elif sys.platform == 'darwin': # MacOS hosts
    SEQ2MTX = cwd + '/psipred/bin/osx/seq2mtx'
    PSIPRED = cwd + '/psipred/bin/osx/psipred'
    PSIPASS2 = cwd + '/psipred/bin/osx/psipass2'

for exec_path in [SEQ2MTX, PSIPRED, PSIPASS2]:
    if os.path.exists(exec_path):
        os.chmod(exec_path, int('777', 8))

def run(input):
    fasta = os.path.basename(input)
    name = fasta.split('.')[-2]

    print('Psipred Running... processing: ' + name)

    with open(TEMPDIR + name + ".mtx", "w") as mtx_file:
        seq2mtx = subprocess.run([SEQ2MTX, input], stdout=mtx_file)

    with open(TEMPDIR + name + ".ss", "w") as ss_file:
        psipred = subprocess.run( [PSIPRED, TEMPDIR+name+".mtx", DATADIR+'weights.dat', DATADIR+'weights.dat2', DATADIR+'weights.dat3'], stdout=ss_file)

    with open(TEMPDIR + name + ".horiz", "w") as horiz_file:
        psipass2 = subprocess.run( [PSIPASS2, DATADIR+'weights_p2.dat', '1', '1.0', '1.0', TEMPDIR+name+".ss2", TEMPDIR+name+".ss"], stdout=horiz_file)
