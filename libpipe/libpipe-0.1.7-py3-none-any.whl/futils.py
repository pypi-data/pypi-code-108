# File/Folder utilities
#
# Author: F. Mertens

import re
import os
import time
import shutil


def file_not_found_retry(fct, n_try, *args, **kargs):
    for i in range(n_try):
        try:
            fct(*args, **kargs)
            return 0
        except FileNotFoundError:
            if i + 1 == n_try:
                raise
            print('File not found error, will try again in a second ...')
            time.sleep(1 + i)


def reglob(path, exp, invert=False):
    m = re.compile(exp)

    if invert is False:
        res = [f for f in os.listdir(path) if m.search(f)]
    else:
        res = [f for f in os.listdir(path) if not m.search(f)]

    return map(lambda x: "%s/%s" % (path, x, ), res)


def rm_if_exist(directory, verbose=False):
    if os.path.exists(directory):
        if verbose:
            print('Remove ' + directory)
        shutil.rmtree(directory)


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def abspath(p):
    return os.path.abspath(os.path.expanduser(p))


def is_file(f):
    return os.path.isfile(os.path.expanduser(f))


def zip_copy(dir_ins, dir_outs, filename, filename_out=None, verbose=True, n_retry=1):
    if not filename_out:
        filename_out = filename
    for dir_in, dir_out in zip(dir_ins, dir_outs):
        if verbose:
            print(f'Copy {dir_in}/{filename} -> {dir_out}/{filename_out}')
        file_not_found_retry(shutil.copyfile, n_retry, f'{dir_in}/{filename}', f'{dir_out}/{filename_out}')


def zip_copytree(dir_ins, dir_outs, dirname, verbose=True, n_retry=1):
    for dir_in, dir_out in zip(dir_ins, dir_outs):
        if verbose:
            print(f'Copy {dir_in}/{dirname} -> {dir_out}/{dirname}')
        file_not_found_retry(shutil.copytree, n_retry, f'{dir_in}/{dirname}', f'{dir_out}/{dirname}')


def zip_rename(dir_ins, dir_outs, filename_or_dirname=None, verbose=True, n_retry=1):
    for f_in, f_out in zip(dir_ins, dir_outs):
        if filename_or_dirname is not None:
            f_in = f'{f_in}/{filename_or_dirname}'
            f_out = f'{f_out}/{filename_or_dirname}'
        if verbose:
            print(f'Rename {f_in} -> {f_out}')
        file_not_found_retry(os.rename, n_retry, f_in, f_out)


def zip_rename_reg(dir_ins, dir_outs, regex, verbose=True, invert=False, n_retry=1):
    for f_in, f_out in zip(dir_ins, dir_outs):
        for f_in2 in reglob(f_in, regex, invert=invert):
            f_out2 = f'{f_out}/{os.path.basename(f_in2)}'
            if verbose:
                print(f'Rename {f_in2} -> {f_out2}')
            file_not_found_retry(os.rename, n_retry, f_in2, f_out2)


def zip_rm(dirs, verbose=True):
    for directory in dirs:
        rm_if_exist(directory, verbose=verbose)
