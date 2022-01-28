import os, struct, logging

if os.name == 'nt':
    afs_home = '\/afs/ipp-garching.mpg.de/home'
else:
    afs_home = '/afs/ipp-garching.mpg.de/home'

logger = logging.getLogger('aug_sfutils.manage_ed')


def sf_path(nshot, diag, exp='AUGD', ed=0):
    """Path finder for shotfiles

    Input:
        nshot    int  Shotnumber
        diag     str  Diagnostic label
        exp(opt) str  Expriment label (default: 'AUGD')
        ed(opt)  int  Edition number (default: 0)

    Output:
        path_out   str   Full path of shotfile (None if not found)
        ed         int   Actual edition (non trivial if input ed=0)
    """

    sshot = str(nshot).zfill(5)
    exp = exp.lower()
    diag = diag.upper()

    if ed == 0:
        ed = ed_zero(diag, nshot, exp=exp)
    if ed is None:
        return None, None

    if exp == 'augd':
        sf_dir = '%s/a/augd/shots/%s' %(afs_home, sshot[:4])
        a = os.listdir(sf_dir)
        path_out = None
        for subdir in a:
            path1 = '%s/%s/%s' %(sf_dir, subdir, diag)
            if os.path.isdir(path1):
                if not os.path.isfile('%s/ed_cntl' %path1):
                    path_out = '%s/%d' %(path1, nshot)
                else:
                    path_out = '%s/%d.%d' %(path1, nshot, ed)
                break
    else:
        path1 = '%s/%s/%s/shotfiles/%s/%s' %(afs_home, exp[0], exp, diag, sshot[:2])
        if os.path.isdir(path1):
            if not os.path.isfile('%s/ed_cntl' %path1):
                path_out = '%s/%s' %(path1, sshot[2:])
            else:
                path_out = '%s/%s.%d' %(path1, sshot[2:], ed)

    return path_out, ed


def ed_zero(diag, nshot, exp='augd'):
    """Finds the actual edition number of ed=0
    Input:
        nshot    int  Shotnumber
        diag     str  Diagnostic label
        exp(opt) str  Expriment label (default: 'AUGD')

    Output:
        ed_nr    int  Actual edition number. 1 for level0, None if not found
    """
 
    sshot = str(nshot).zfill(5)
    exp = exp.lower()
    diag = diag.upper()

    if exp == 'augd':
        sf_dir = '%s/a/augd/shots/%s' %(afs_home, sshot[:4])
        if not os.path.isdir(sf_dir):
            return None
        a = os.listdir(sf_dir)
        fed_dir = None
        for subdir in a:
            fed_dir = '%s/%s/%s' %(sf_dir, subdir, diag)
            if os.path.isdir(fed_dir):
                if not os.path.isfile('%s/ed_cntl' %fed_dir):
                    return 1
                break
    else:
        fed_dir = '%s/%s/%s/shotfiles/%s/%s' %(afs_home, exp[0], exp, diag, sshot[:2])
        nshot = nshot % 1000
        if not os.path.isdir(fed_dir):
            return None
        else:
            if not os.path.isfile('%s/ed_cntl' %fed_dir):
                return 1

    ed_d = read_ed_cntl(fed_dir, exp=exp)
    if ed_d is None:
        return None
    logger.debug(nshot, ed_d)
    if nshot in ed_d.keys():
        return ed_d[nshot]
    else:
        return None


def read_ed_cntl(fed_dir, exp='augd'):
    """Parser of ed_cntl file

    Input:
        fed_dir   str   Path where to look for ed_cntl file
        exp(opt)  str   Exp
    Output:
        max_ed    int   Max edition number for given diag, shot
    """
    ed_ctrl = '%s/ed_cntl' %fed_dir
    if not os.path.isfile(ed_ctrl):
        return None

    exp = exp.strip().lower()
    if exp == 'augd':
        shot_byt  = 5
        delta_byt = 24
    else:
        shot_byt  = 3
        delta_byt = 20

    with open(ed_ctrl, 'rb') as f:
        byt_str = f.read()

    jbyt = 12
    max_ed = {}

    while(True):
        try:
            ed = struct.unpack('>I', byt_str[jbyt + 4: jbyt + 8])[0]
            shot = struct.unpack('>%dc' %shot_byt, byt_str[jbyt+16: jbyt+16+shot_byt])
            jbyt += delta_byt
            sshot = b''.join(shot)
            nshot = int(sshot)
            max_ed[nshot] = ed
        except:
            break

    return max_ed


if __name__ == '__main__':

    fed_in = '%s/g/git/shotfiles/TRA/35' %afs_home
    ed = read_ed_cntl(fed_in, exp='git')
    logger.info(fed_in, ed) 
    fed_in = '%s/a/augd/shots/3956/L1/NSP' %afs_home
    fed_in = '%s/a/augd/shots/3956/L1/TOT' %afs_home
    ed = read_ed_cntl(fed_in)
    logger.info(fed_in, ed)
