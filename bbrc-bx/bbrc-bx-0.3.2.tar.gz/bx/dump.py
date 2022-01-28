import os

commands = ['archiving tests',
            'ashs volumes',
            'ashs tests',
            'bamos stats',
            'bamos tests',
            'donsurf aparc',
            'donsurf tests',
            'dtifist tests',
            'freesurfer6hires aparc',
            'freesurfer6hires aseg',
            'freesurfer6hires tests',
            'freesurfer6hires hippoSfVolumes',
            'freesurfer7 aparc',
            'freesurfer7 aseg',
            'freesurfer7 tests',
            'freesurfer7 amygNucVolumes',
            'freesurfer7 hippoSfVolumes',
            'freesurfer7 hypothalamus',
            'freesurfer7 thalamus',
            'freesurfer7 brainstem',
            'fdg landau',
            'fdg tests',
            'ftm centiloids',
            'ftm tests',
            'basil aal',
            'basil stats',
            'basil perfusion',
            'basil tests',
            'braak volumes',
            'braak thickness',
            'braak fdg',
            'signature jack',
            'signature dickerson',
            'scandates']


def dump(wd, interpreter='python', bash_command='/usr/bin/bash', debug=False):
    """ Call every command among those which return numeric endpoints
    (FreeSurfer thickness, volumes, hippocampal subfields, centiloids,
    signatures, Braak regions, etc). This results in a collection of
    spreadsheets to be served by dashboards."""

    alfa_projects = ['VBM_ALFA_PLUS_AAIC2020_20201202', 'ALFA_20201001']
    import tempfile
    fh, fp = tempfile.mkstemp(suffix='.sh')
    print(fp)
    os.close(fh)
    w = open(fp, 'w')
    cmd = 'mkdir %s/bx.new' % wd
    import bx
    import os.path as op
    bx_fp = op.join(op.dirname(op.dirname(bx.__file__)), 'bin', 'bx')
    w.write(cmd + '\n')
    for c in commands:
        if 'fdg' in c:
            projects = ['ALFA_PET_FDG_20210421']
        elif 'ftm' in c:
            projects = ['ALFA_PET_FTM_20210421']
        elif 'basil' in c:
            projects = ['ALFA_PLUS2']
        else:
            projects = alfa_projects
        for p in projects:
            cmd = ' '.join([interpreter, bx_fp, c, p, '--dest', op.join(wd, 'bx.new')])
            print(cmd)
            w.write(cmd + '\n')

    last_commands = ['rm -rf %s/bx.bak' % wd,
                     'mv %s/bx %s/bx.bak' % (wd, wd),
                     'mv %s/bx.new %s/bx' % (wd, wd)]
    for cmd in last_commands:
        w.write(cmd + '\n')

    w.close()
    print(fp)

    if not debug:
        os.system('%s %s' % (bash_command, fp))

    # convert excel to csv
    from glob import glob
    import os.path as op
    import subprocess
    xlsx = glob(op.join(wd, 'bx', '*.xlsx'))
    for each in xlsx:
        fn = each.split('.xlsx')[0]
        call = [op.join(op.dirname(interpreter), 'xlsx2csv'), each, op.join(wd, 'bx', fn + '.csv')]
        print(' '.join(call))
        if not debug:
            subprocess.call(call)
