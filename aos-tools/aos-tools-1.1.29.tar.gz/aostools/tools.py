# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function
import os
import sys
import time
import hashlib
import zipfile
import codecs
import json
import re
import platform
import subprocess
import chardet
import glob2
import shutil

try:
    from urlparse import urlparse
    import urllib
    import httplib as http
    urlretrieve = urllib.urlretrieve
    import urllib2 as urllib
except:
    from urllib.parse import urlparse
    import urllib.request
    import http.client as http
    urlretrieve = urllib.request.urlretrieve


try:
    import yaml
except:
    put_string("\n\nNot found pyyaml, please install: \nsudo pip install pyyaml")
    sys.exit(-1)

def is_contain_chinese(check_str):
    if sys.version_info.major == 2:
        if type(check_str) == str:
            check_str = check_str.decode('utf-8')
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    match = zhPattern.search(check_str)
    if match:
        return True

def is_leagal_name(name):
    pattern = re.compile(u'^[_a-zA-Z]\w*$')
    match = pattern.search(name)
    if match:
        return True

def string_len(text):
    L = 0
    R = ''
    if sys.version_info.major == 2:
        if type(text) == str:
            text = text.decode('utf8')
    for c in text:
        if ord(c) >= 0x4E00 and ord(c) <= 0x9FA5:
            L += 2
        else:
            L += 1
    return L


def put_string(*args, **keys):
    for a in args:
        if sys.version_info.major == 2:
            if type(a) == unicode:
                a = a.encode('utf8')
        if 'key' in keys:
            key = keys['key']
            color_print(a, key=key, end=' ', ignorecase=True)
        else:
            print(a, end=' ')
    print()


def color_print(text, key=[], end='\n', ignorecase=False):
    idx = {}
    itext = text
    if ignorecase:
        itext = text.lower()
    for k in key:
        index = 0
        while True:
            s = itext.find(k, index)
            if s >= 0:
                e = s + len(k)
                need_del = []
                for a, b in idx.items():
                    if max(s, a) <= min(e, b):
                        s = min(s, a)
                        e = max(e, b)
                        need_del.append(a)
                for v in need_del:
                    del idx[v]
                idx[s] = e
                index = e
            else:
                break
    s = 0
    for v in list(sorted(idx)):
        e = v
        print(text[s: e], end='')
        print('\033[1;31m' + text[v: idx[v]] + '\033[0m', end='')
        s = idx[v]
    print(text[s: len(text)], end=end)


def yaml_load(filename):
    try:
        with codecs.open(filename, 'r', encoding='UTF-8') as fh:
            text = fh.read()
            return yaml.safe_load(text)
    except Exception as e:
        put_string("(%s) in file:%s" % (str(e), filename))
        exit(-1)


def home_path(path=''):
    return os.path.join(os.path.expanduser('~'), path)


def http2git(url):
    conn = urlparse(url)
    url = 'git@' + conn.netloc + ':' + conn.path[1:]
    return url


def MD5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()


def http_request(method, url, data=None, headers={}):
    conn = urlparse(url)

    if conn.scheme == "https":
        connection = http.HTTPSConnection(conn.netloc)
    else:
        connection = http.HTTPConnection(conn.netloc)
    # connection.debuglevel = 1

    connection.request(method=method, url=conn.path + '?' +
                       conn.query, body=data, headers=headers)
    response = connection.getresponse()
    return response.status, response.read(), response.msg



def http_get(url, path):
    conn = urlparse(url)

    if conn.scheme == "https":
        connection = http.HTTPSConnection(conn.netloc)
    else:
        connection = http.HTTPConnection(conn.netloc)

    connection.request('GET', conn.path)
    response = connection.getresponse()

    filename = os.path.join(path, os.path.basename(conn.path))

    try:
        with codecs.open(filename, 'wb', encoding='UTF-8') as f:
            f.write(response.read())
    except:
        pass

    return filename


def wget(url, out_file):
    start_time = time.time()

    def barProcess(blocknum, blocksize, totalsize):
        speed = (blocknum * blocksize) / (time.time() - start_time)
        # speed_str = " Speed: %.2f" % speed
        speed_str = " Speed: %sB/S         " % format_size(speed)
        recv_size = blocknum * blocksize

        # 设置下载进度条
        f = sys.stdout
        percent = float(recv_size) / totalsize
        if percent > 1:
            percent = 1
        percent_str = " %.2f%%" % (percent * 100)
        n = int(percent * 50)
        s = ('#' * n).ljust(50, '-')
        f.write(percent_str.ljust(9, ' ') + '[' + s + ']' + speed_str)
        f.flush()
        f.write('\r')

    def format_size(bytes):
        bytes = float(bytes)
        kb = bytes / 1024
        if kb >= 1024:
            M = kb / 1024
            if M >= 1024:
                G = M / 1024
                return "%.3fG" % (G)
            else:
                return "%.3fM" % (M)
        else:
            return "%.3fK" % (kb)

    return urlretrieve(url, out_file, barProcess)


# make_archive(base_name, format, root_dir=None, base_dir=None, verbose=0,dry_run=0, owner=None, group=None, logger=None)
def dfs_get_zip_file(input_path, result):
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            dfs_get_zip_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)


def version_inc(v, x):
    l = len(v)
    num_start = -1
    for i in range(l - 1, -1, -1):
        if num_start == -1:
            if v[i:i + 1].isdigit():
                num_start = i + 1
        else:
            if not v[i:i + 1].isdigit():
                s = v[i + 1:num_start]
                v2 = v.replace(s, str(int(s) + x))
                return v2

    return v + '-0'


def zip_path(input_path, zipName):
    if os.path.isdir(input_path):
        base = os.path.dirname(zipName)
        try:
            os.makedirs(base)
        except:
            pass
        predir = input_path.rsplit('/', 1)[0]
        f = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
        filelists = []
        dfs_get_zip_file(input_path, filelists)
        for file in filelists:
            suffix = os.path.splitext(file)[-1]
            if suffix != '.d' and suffix != '.o':
                f.write(file, file.split(predir)[1])
        f.close()

def unzip_path(output_path, zipName):
    if os.path.exists(output_path):
        if os.path.isfile(output_path):
            os.remove(output_path)
            os.makedirs(output_path)
    else:
        os.makedirs(output_path)

    file = os.path.abspath(zipName)
    if zipfile.is_zipfile(file):
        try:
            with zipfile.ZipFile(file, "r") as myzip:
                badcrc = myzip.testzip()
                if badcrc:
                    put_string("Bad CRC for file %s of the zip archive" % badcrc)
                myzip.extractall(output_path)
                return True
        except Exception as e:
            put_string("Failed to install from zip file, error: %s!" % format(e))
    else:
        put_string("%s is not zip file" % file)
    return False

def write_file(text, filename):
    contents = None

    try:
        with codecs.open(filename, 'r', encoding='UTF-8') as f:
            contents = f.read()
    except:
        pass

    if text == contents:
        return
    try:
        p = os.path.dirname(filename)
        try:
            os.makedirs(p)
        except:
            pass

        with codecs.open(filename, 'w', encoding='UTF-8') as f:
            f.write(text)
    except:
        put_string("Generate %s file failed." % filename)


def genSConcript(path):
    file_name = os.path.join(path, 'SConscript')
    text = '''Import('defconfig')\ndefconfig.library_yaml()\n'''
    write_file(text, file_name)
    return file_name


def genSConstruct(components, path):
    text = """#! /bin/env python

from aostools.make import Make

defconfig = Make()

Export('defconfig')

defconfig.build_components()
defconfig.program()
"""

    comp_list = ''
    for component in components:
        if component != '.':
            comp_list += '    "' + component.name + '",\n'

    text = text % comp_list

    script_file = os.path.join(path, 'SConstruct')
    write_file(text, script_file)


def genMakefile(path):
    text = """CPRE := @
ifeq ($(V),1)
CPRE :=
endif


.PHONY:startup
startup: all

all:
	$(CPRE) scons -j4
	@echo YoC SDK Done


.PHONY:clean
clean:
	$(CPRE) rm -rf aos_sdk
	$(CPRE) scons -c
	$(CPRE) find . -name "*.[od]" -delete

%:
	$(CPRE) scons --component="$@" -j4
"""

    script_file = os.path.join(path, 'Makefile')
    write_file(text, script_file)


def save_yoc_config(defines, filename):
    contents = ""

    try:
        with codecs.open(filename, 'r', encoding='UTF-8') as f:
            contents = f.read()
    except:
        pass

    text = '''/* don't edit, auto generated by tools/toolchain.py */\n
#ifndef __YOC_CONFIG_H__
#define __YOC_CONFIG_H__
#ifndef CONFIG_CPU\n\n'''
    for k, v in defines.items():
        if v in ['y', 'Y']:
            text += '#define %s 1\n' % k
        elif v in ['n', 'N']:
            text += '// #define %s 1\n' % k
        elif type(v) == int:
            text += '#define %s %d\n' % (k, v)
        else:
            text += '#define %s "%s"\n' % (k, v)

    text += '\n#endif\n#endif\n'

    if text == contents:
        return False

    write_file(text, filename)


def save_csi_config(defines, filename):
    text = '''/* don't edit, auto generated by tools/toolchain.py */

#ifndef __CSI_CONFIG_H__
#define __CSI_CONFIG_H__

#include <yoc_config.h>

#endif

'''

    write_file(text, filename)

def get_cmpt_path_by_type(type):
    if type == 'board':
        path = os.path.join('hardware', 'board')
    elif type == 'chip':
        path = os.path.join('hardware', 'chip')
    elif type == 'arch':
        path = os.path.join('hardware', 'arch')
    elif type == 'drv_core':
        path = os.path.join('components', 'drivers', 'core')
    elif type == 'drv_peripheral':
        path = os.path.join('components', 'drivers', 'peripheral')
    elif type == 'drv_external_device':
        path = os.path.join('components', 'drivers', 'external_device')
    elif type == 'kernel':
        path = 'kernel'
    elif type == 'solution':
        path = 'solutions'
    elif type == 'document':
        path = '.'
    else:
        # common and sdk
        path = 'components'
    return path

def get_cmpt_top_path_by_type(type):
    if type == 'board' or type == 'chip' or type == 'arch':
        path = 'hardware'
    elif type == 'drv_core' or type == 'drv_peripheral' or type == 'drv_external_device':
        path = 'components'
    elif type == 'kernel':
        path = 'kernel'
    elif type == 'solution':
        path = 'solutions'
    elif type == 'document':
        path = '.'
    else:
        # common and sdk
        path = 'components'
    return path

def get_type_by_cmpt_path(path):
    path = os.path.abspath(path)
    dirname = os.path.dirname(path)
    name = os.path.basename(dirname)
    if name in ['board', 'chip', 'arch', 'kernel']:
        comp_type = name
    elif name == 'core':
        comp_type = 'drv_core'
    elif name == 'peripheral':
        comp_type = 'drv_peripheral'
    elif name == 'external_device':
        comp_type = 'drv_external_device'
    elif name == 'solutions':
        comp_type = 'solution'
    else:
        comp_type = 'common'
    return comp_type

def get_host_os():
    host_os = platform.system()
    if host_os == 'Windows':
        host_os = 'Win32'
    elif host_os == 'Linux':
        if platform.machine().endswith('64'):
            bit = '64'
        else:
            bit = '32'
        host_os += bit
    elif host_os == 'Darwin':
        host_os = 'OSX'
    else:
        host_os = None
    return host_os

def find_latest_file(src):
    latest_modified_time = 0.0
    latest_file = ""
    for s in glob2.iglob(src):
        modified_time = os.stat(s).st_mtime
        if modified_time > latest_modified_time:
            latest_modified_time = modified_time
            latest_file = s
    return latest_file

def get_elf_bin_file(filename):
    elf_file = ''
    bin_file = ''
    if not os.path.isfile(filename):
        return elf_file, bin_file
    try:
        with codecs.open(filename, 'r', encoding='UTF-8') as fh:
            lines = fh.readlines()
            elf_pattern = re.compile('elf\s*=\s*[\'\"](.+?)[\'\"]')
            bin_pattern = re.compile('objcopy\s*=\s*[\'\"](.+?)[\'\"]')
            for line in lines:
                if line.startswith('defconfig'):
                    match = elf_pattern.search(line)
                    if match:
                        elf_file = match.group(1)
                    match = bin_pattern.search(line)
                    if match:
                        bin_file = match.group(1)
                    break
            # if not specified, search in out directory
            if not elf_file:
                elf_file = find_latest_file(os.path.join("out", "*@*.elf"))
            if not bin_file:
                bin_file = find_latest_file(os.path.join("out", "*@*.bin"))
            return elf_file, bin_file
    except Exception as e:
        put_string("(%s) in file:%s" % (str(e), filename))
        exit(-1)

def which(program, extra_path=None):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    def which_internal(program, extra_path):
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            paths = os.environ["PATH"].split(os.pathsep)
            if extra_path:
                paths += extra_path.split(os.pathsep)

            for path in paths:
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        return ""
    if get_host_os() == 'Win32':
        program_bak = program
        if program.endswith('.exe') == False:
            program += '.exe'
        exe_file = which_internal(program, extra_path)
        if not exe_file:
            if program_bak.endswith('.bat') == False:
                program = program_bak + '.bat'
            exe_file = which_internal(program, extra_path)
        return exe_file
    else:
        return which_internal(program, extra_path)

def get_mem_info(map_file, XIP_ENABLE = True):
    mem_map_text = ''
    sym_all_list = []
    lib_dic_list = []
    id_list      = []
    map_lines    = []
    total_ro = 0
    total_rw = 0

    #1. get 'all_map_str' from file
    with open(map_file, 'r') as f:
        all_map_str = f.read()
        if not all_map_str:
            print ('Can\'t parse map_file!')
            return

    #2. get 'sym_map_text' from 'all_map_str'
    # find memory map (without discard and debug sections)
    mem_map_list = re.findall(r'Linker script and memory map([\s\S]+?)OUTPUT', all_map_str)
    mem_map_text = '' if not mem_map_list else mem_map_list[0]
    if not mem_map_text:
        print ('Can\'t parse memory info, memory info get fail!')
        return
    mem_map_text = mem_map_text.replace('\r', '')

    #3. get all symbol information from 'sym_map_text'
    sym_all_list_a = re.findall(r' [\.\w]*\.(iram1|text|literal|rodata|rodata1|data|bss|gcc_except_table)(?:\.(\S+)\n? +| +)(0x\w+) +(0x\w+) +.+[/\\](.+\.a)\((.+\.o)\)\n', mem_map_text)
    sym_all_list_a = map(lambda arg : {'Type':arg[0], 'Sym':arg[1], 'Addr':int(arg[2], 16),
                    'Size':int(arg[3], 16), 'Lib':arg[4], 'File':arg[5]}, sym_all_list_a)

    sym_all_list_o = re.findall(r' [\.\w]*\.(iram1|text|literal|rodata|data|bss|mmu_tbl)(?:\.(\S+)\n? +| +)(0x\w+) +(0x\w+) +.+[/\\](.+\.o)\n', mem_map_text)
    sym_all_list_o = map(lambda arg : {'Type':arg[0], 'Sym':arg[1], 'Addr':int(arg[2], 16),
                    'Size':int(arg[3], 16), 'Lib':'null', 'File':arg[4]}, sym_all_list_o)

    sym_com_list_a = re.findall(r' (COMMON) +(0x\w+) +(0x\w+) +.+[/\\](.+\.a)\((.+\.o)\)\n +0x\w+ +(\w+)\n', mem_map_text)
    sym_com_list_a = map(lambda arg : {'Type':arg[0], 'Sym':arg[5], 'Addr':int(arg[1], 16),
                    'Size':int(arg[2], 16), 'Lib':arg[3], 'File':arg[4]}, sym_com_list_a)

    sym_com_list_o = re.findall(r' (COMMON) +(0x\w+) +(0x\w+) +.+[/\\](.+\.o)\n +0x\w+ +(\w+)\n', mem_map_text)
    sym_com_list_o = map(lambda arg : {'Type':arg[0], 'Sym':arg[4], 'Addr':int(arg[1], 16),
                    'Size':int(arg[2], 16), 'Lib':'null', 'File':arg[3]}, sym_com_list_o)

    sym_all_list.extend(sym_all_list_a)
    sym_all_list.extend(sym_all_list_o)
    sym_all_list.extend(sym_com_list_a)
    sym_all_list.extend(sym_com_list_o)

    #for each memmap info, classify by mem type
    for obj_dic in sym_all_list:
        id_str = obj_dic['Lib']
        if id_str not in id_list:
            idx = len(lib_dic_list)
            lib_dic_list.append({'Lib':obj_dic['Lib'], 'ROM':0, 'RAM':0, 'Text':0, 'Rodata':0, 'Data':0, 'Bss':0})
            id_list.append(id_str)
        else:
            idx = id_list.index(id_str)

        if obj_dic['Type'] == 'text' or obj_dic['Type'] == 'literal' or obj_dic['Type'] == 'iram1':
            lib_dic_list[idx]['Text'] += obj_dic['Size']
        elif obj_dic['Type'] == 'rodata' or obj_dic['Type'] == 'rodata1':
            lib_dic_list[idx]['Rodata'] += obj_dic['Size']
        elif obj_dic['Type'] == 'data' or obj_dic['Type'] == 'gcc_except_table':
            lib_dic_list[idx]['Data'] += obj_dic['Size']
        elif obj_dic['Type'] == 'bss' or obj_dic['Type'] == 'COMMON' or obj_dic['Type'] == 'mmu_tbl':
            lib_dic_list[idx]['Bss'] += obj_dic['Size']

    lib_dic_list.sort(key = lambda x : x['Lib'].upper())

    #sum ROM and RAM for each library file
    for lib_dic in lib_dic_list:
        lib_dic['ROM'] = lib_dic['Text'] + lib_dic['Rodata'] + lib_dic['Data']
        if XIP_ENABLE == True:
            lib_dic['RAM'] = lib_dic['Data'] + lib_dic['Bss']
        else:
            lib_dic['RAM'] = lib_dic['Text'] + lib_dic['Rodata'] + lib_dic['Data'] + lib_dic['Bss']
        map_lines.append(r'| %-40s | %-8d  | %-8d |'%(lib_dic['Lib'], lib_dic['ROM'], lib_dic['RAM']))
        total_rw += lib_dic['RAM']
        total_ro += lib_dic['ROM']

    print('\n                        AOS MEMORY MAP                            ')
    print('|=================================================================|')
    print('| %-40s | %-8s  | %-8s |'%('MODULE','RO Size','RW Size'))
    print('|=================================================================|')
    for line in map_lines:
        print(line)
    print('|=================================================================|')
    print('| %-40s | %-8d  | %-8d |'%('TOTAL (bytes)', total_ro, total_rw))
    print('|=================================================================|')

def getSolutionAndBoard(yoc_path):
    config_file = os.path.join(yoc_path, ".config")
    if os.path.isfile(config_file) and os.path.isfile(os.path.join(yoc_path, ".aos")):
        conf = yaml_load(config_file)
        return conf["solution"], conf["board"]
    return None, None

def change_dir_to_solution(yoc_path):
    cur_dir = os.getcwd()
    # enter into solution directory if in the workspace root directory
    if cur_dir == yoc_path:
        solution, board = getSolutionAndBoard(yoc_path)
        if solution:
            new_dir = os.path.join(cur_dir, "solutions", solution)
            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                put_string("change dir to %s." % new_dir)
    return cur_dir

def check_version_text(current_version, lines):
    text = ""
    pattern = re.compile(r'aos-tools\s+([0-9\.]*)\s+([0-9\.]*)')
    for line in lines:
        try:
            if type(line) != str:
                encode = chardet.detect(line)
                line = line.decode(encode["encoding"]).strip()
        except UnicodeDecodeError:
            line = " "
            pass
        if line.find("aos-tools") >= 0:
            match = pattern.search(line)
            if match:
                text = line
                if current_version != match.group(2):
                    put_string("\n\n[NOTICE]The lastest version aos-tools is %s. You can upgrade it as below:" % match.group(2))
                    put_string("python -m pip install -U aos-tools")
                break
    return text

def check_remote_version(current_version):
    need_check = False
    ver_file = home_path('.aliot/version')
    if os.path.isfile(ver_file):
        modified_time = os.stat(ver_file).st_mtime
        now = time.time()
        if modified_time > now or (now - modified_time) > 4 * 3600:
            need_check = True
        else:
            with open(ver_file, 'r') as f:
                lines = f.readlines()
                check_version_text(current_version, lines)
    else:
        need_check = True
        aliot_dir = home_path('.aliot')
        if not os.path.exists(aliot_dir):
            os.mkdir(aliot_dir)
    if need_check:
        put_string("\n\nChecking latest version of aos-tools from pip server...")
        script_process = subprocess.Popen("python -m pip list --outdated", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = script_process.stdout.readlines()
        line = check_version_text(current_version, lines)
        if line:
            with open(ver_file, 'w') as f:
                f.write(line)
        else:
            with open(ver_file, 'w') as f:
                f.write("latest")
            put_string("It is already latest version.")

def rmtree_enhanced(rm_path):
    try:
        delete_ret = 0
        shutil.rmtree(rm_path)
    except:
        delete_ret = 1
        if get_host_os() == 'Win32':
            delete_ret = os.system("cmd /c rmdir /s /q \"%s\"" % rm_path) >> 8
        if delete_ret != 0:
            put_string("Delete %s failed. Please delete it manually." % rm_path)
    return delete_ret
