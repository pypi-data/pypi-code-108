#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# system utilities methods
# IMIO <support@imio.be>
#
from __future__ import print_function

import os
import re
import sys
import tempfile
import time
from datetime import datetime

# can be used in load_var
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def verbose(msg):
    print('>> %s' % msg)


def warning(msg):
    print('?? {}'.format(msg))


def error(msg):
    print('!! {}'.format(msg), file=sys.stderr)


def trace(TRACE, msg):
    if not TRACE:
        return
    print("TRACE:'{}'".format(msg))

# --- Writing files ---


def write_to(out_files, key, line):
    """
        Open output file and write line (adding line feed)
        outfiles param: dic containing this struct :
            {'key': {'file': 'filepath', 'header': 'First line'}}
    """
    if 'fh' not in out_files[key]:
        filename = out_files[key]['file']
        try:
            out_files[key]['fh'] = open(filename, 'w')
            if 'header' in out_files[key] and out_files[key]['header']:
                out_files[key]['fh'].write("%s\n" % out_files[key]['header'])
        except IOError as m:
            error("Cannot create '%s' file: %s" % (filename, m))
            return
    out_files[key]['fh'].write("%s\n" % line)


def close_outfiles(outfiles):
    """ Close the outfiles """
    for key in outfiles.keys():
        if 'fh' in outfiles[key]:
            outfiles[key]['fh'].close()
#            verbose("Output file '%s' generated" % outfiles[key]['file'])

# --- Reading files ---


def read_file(filename, strip_chars='', skip_empty=False, skip_lines=0):
    """ read a file and return lines """
    lines = []
    try:
        thefile = open(filename, 'r')
    except IOError:
        error("! Cannot open %s file" % filename)
        return lines
    for i, line in enumerate(thefile.readlines()):
        if skip_lines and i < skip_lines:
            continue
        line = line.strip('\n')
        if strip_chars:
            line = line.strip(strip_chars)
        if skip_empty and not line:
            continue
        lines.append(line)
    thefile.close()
    return lines


def read_csv(filename, strip_chars='', replace_dq=True, skip_empty=False, skip_lines=0, **kwargs):
    """ read a csv file and return lines """
    lines = []
    try:
        thefile = open(filename, 'r')
    except IOError:
        error("! Cannot open %s file" % filename)
        return lines
    import csv
    for i, data in enumerate(csv.reader(thefile, **kwargs)):
        if skip_lines and i < skip_lines:
            continue
        replaced = []
        empty = True
        for item in data:
            if replace_dq:
                item = item.replace('""', '"')
            if strip_chars:
                item = item.strip(strip_chars)
            if item:
                empty = False
            replaced.append(item)
        if skip_empty and empty:
            continue
        lines.append(replaced)
    thefile.close()
    return lines


def read_dictcsv(filename, fieldnames=[], strip_chars='', replace_dq=True, skip_empty=False, skip_lines=0, ln_key='_ln',
                 **kwargs):
    """ read a csv file and return dict row list """
    rows = []
    import csv
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, restkey='_rest', restval='__NO_CO_LU_MN__', **kwargs)
        for row in reader:
            if reader.line_num == 1:
                reader.restval = u''
                if '_rest' in row:
                    error(u'! STOPPING: some columns are not defined in fieldnames: {}'.format(row['_rest']))
                    return u'STOPPING: some columns are not defined in fieldnames: {}'.format(row['_rest']), []
                extra_cols = [key for (key, val) in row.items() if val == '__NO_CO_LU_MN__']
                if extra_cols:
                    error(u'! STOPPING: to much columns defined in fieldnames: {}'.format(extra_cols))
                    return u'STOPPING: to much columns defined in fieldnames: {}'.format(extra_cols), []
            if reader.line_num <= skip_lines:
                continue
            empty = True
            new_row = {}
            if ln_key:
                new_row[ln_key] = reader.line_num
            for key, val in row.items():
                if replace_dq:
                    val = val.replace('""', '"')
                if strip_chars:
                    val = val.strip(strip_chars)
                if val:
                    empty = False
                new_row[key] = val
            if skip_empty and empty:
                continue
            rows.append(new_row)
    return u'', rows


def read_dir(dirpath, with_path=False, only_folders=False, only_files=False, to_skip=[]):
    """ Read the dir and return files """
    files = []
    for filename in os.listdir(dirpath):
        if filename in to_skip:
            continue
        if only_folders and not os.path.isdir(os.path.join(dirpath, filename)):
            continue
        if only_files and not os.path.isfile(os.path.join(dirpath, filename)):
            continue
        if with_path:
            files.append(os.path.join(dirpath, filename))
        else:
            files.append(filename)
    return files


def read_dir_filter(dirpath, with_path=False, extensions=[], only_folders=False):
    """ Read the dir and return some files """
    files = []
    for filename in read_dir(dirpath, with_path=with_path, only_folders=only_folders):
        basename, ext = os.path.splitext(filename)
        if ext and ext.startswith('.'):
            ext = ext[1:]
        if extensions and ext not in extensions:
            continue
        files.append(filename)
    return files


def read_dir_extensions(dirpath, to_skip=[]):
    """ Read the dir and return extensions """
    extensions = []
    for filename in read_dir(dirpath):
        if filename in to_skip:
            continue
        basename, ext = os.path.splitext(filename)
        if ext and ext.startswith('.'):
            ext = ext[1:]
        if ext not in extensions:
            extensions.append(ext)
    extensions.sort()
    return extensions

# ------------------------------------------------------------------------------


def runCommand(cmd, outfile=None, append=True):
    """ run an os command and get back the stdout and stderr outputs """
    def get_ret_code(line):
        match = re.match(r'RET_CODE=(\d+)', line)
        if match is None:
            return -1
        else:
            return int(match.group(1))
    now = datetime.now()
    if outfile:
        fh = open(outfile, '%s' % (append and 'a' or 'w'))
        fh.write("==================== NEW RUN on {} ====================\n".format(now.strftime('%Y%m%d-%H%M')))
        fh.write("=> Running '%s' at %s\n" % (cmd, now.strftime('%Y%m%d %H:%M')))
        fh.close()
        os.system(cmd + ' >>{0} 2>&1 ;echo "RET_CODE=$?" >> {0}'.format(outfile))
        lines = read_file(outfile)
        return [], [], get_ret_code(lines[-1])

    os.system(cmd + ' >_cmd_pv.out 2>_cmd_pv.err ;echo "RET_CODE=$?" >> _cmd_pv.out')
    stdout = stderr = []
    try:
        if os.path.exists('_cmd_pv.out'):
            ofile = open('_cmd_pv.out', 'r')
            stdout = ofile.readlines()
            ofile.close()
            os.remove('_cmd_pv.out')
        else:
            error("File %s does not exist" % '_cmd_pv.out')
    except IOError:
        error("Cannot open %s file" % '_cmd_pv.out')
    try:
        if os.path.exists('_cmd_pv.err'):
            ifile = open('_cmd_pv.err', 'r')
            stderr = ifile.readlines()
            ifile.close()
            os.remove('_cmd_pv.err')
        else:
            error("File %s does not exist" % '_cmd_pv.err')
    except IOError:
        error("Cannot open %s file" % '_cmd_pv.err')
    return stdout, stderr, get_ret_code(stdout.pop())

# --- Dumping and loading data on disk ---


def load_var(infile, var):
    """
        load a dictionary or a list from a file
    """
    if os.path.exists(infile):
        ofile = open(infile, 'r')
        if isinstance(var, dict):
            var.update(eval(ofile.read()))
        elif isinstance(var, list):
            var.extend(eval(ofile.read()))
        ofile.close()


load_dic = load_var


def dump_var(outfile, var):
    """
        dump a dictionary or a list to a file
    """
    ofile = open(outfile, 'w')
    ofile.write(str(var))
    ofile.close()


dump_dic = dump_var

# --- Various ---


def human_size(nb):
    size_letter = {1: 'k', 2: 'M', 3: 'G', 4: 'T'}
    for x in range(1, 4):
        quot = nb // 1024 ** x
        if quot < 1024:
            break
    return "%.1f%s" % (float(nb) / 1024 ** x, size_letter[x])


def disk_size(path, pretty=True):
    """
        return disk size of path content
    """
    cmd = "du -s"
    if pretty:
        cmd += 'h'
    (cmd_out, cmd_err) = runCommand("%s %s" % (cmd, path))
    for line in cmd_out:
        (size, path) = line.strip().split()
        return size
    return 0


def create_temporary_file(initial_file, file_name):
    """
    Create a temporary copy of a file passed as argument.
    file_name is a string used to create the name of the
    temporary file.
    """
    if initial_file and initial_file.size:
        # save the file in a temporary one
        temp_filename = get_temporary_filename(file_name)
        with open(temp_filename, "w") as new_temporary_file:
            new_temporary_file.write(initial_file.data)
            return temp_filename
    return ''


def get_temporary_filename(file_name):
    """
    Returns the name of a temporary file.
    """
    temp_filename = '%s/%f_%s' % (
        tempfile.gettempdir(),
        time.time(),
        file_name,
    )
    return temp_filename


def process_memory():
    """Returns current process memory in MB"""
    import psutil
    process = psutil.Process(os.getpid())
    infos = process.memory_info()
    # possibly infos[0] in some versions
    return infos.rss / 1024 ** 2


def memory():
    """Returns memory information in MB"""
    import psutil
    mem = psutil.virtual_memory()
    return (mem.total/1024**2, mem.used/1024**2, mem.percent, mem.available/1024**2, mem.free/1024**2,
            mem.active/1024**2, mem.inactive/1024**2)