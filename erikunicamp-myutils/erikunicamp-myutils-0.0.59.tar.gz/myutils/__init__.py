import sys, os
from datetime import datetime

def info(*args):
    pref = datetime.now().strftime('[%H:%M:%S]')
    print(pref, *args, file=sys.stdout, flush=True)

def create_readme(argv, outdir):
    readmepath = os.path.join(outdir, 'README.txt')
    os.system('printf "git commit: " >> "{}"'.format(readmepath))
    os.system('git rev-parse  HEAD >> "{}"'.format(readmepath))
    os.system('echo "python {}" >> "{}"'.format(' '.join(argv), readmepath))
    os.system('date +"%Y-%m-%d %H:%M:%S" >> "{}"'.format(readmepath))
    return readmepath

def append_to_file(file, text):
    info('{}'.format(text))
    os.system('echo "{}" >> "{}"'.format(text, file))
