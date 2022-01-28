# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function

from aostools import *
import codecs
import time
import multiprocessing;


class Make(Command):
    common = True
    helpSummary = "Make aos program"
    helpUsage = """
%prog [option] [<subcommand> ...]
"""
    helpDescription = """
Make aos program.\n"
"\nPlease run 'aos make --help' to explore more ...
"""

    def _Options(self, p):
        p.add_option('-b', '--board',
                     dest='board', action='store',
                     help='select board to build')
        p.add_option('-c', '--config',
                     dest='config', action='store',
                     help='select solution and board')


    def Execute(self, opt, args):
        result = 0
        cmds = []
        params = []
        for arg in args:
            if "=" in arg:
                params.append(arg)
            else:
                cmds.append(arg)
        
        params_str = " ".join(params)
        # get workspace root directory
        conf = Configure()
        cur_dir = os.getcwd()
        # enter into solution directory if in the workspace root directory
        if cur_dir == conf.yoc_path:
            solution, board = getSolutionAndBoard(conf.yoc_path)
            if solution:
                new_dir = os.path.join(cur_dir, "solutions", solution)
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    put_string("change dir to %s." % new_dir)
            if board:
                # read board from .config, and set to opt.board. Like aos make -b board
                opt.board = board

        ext_scons_existed = False
        if get_host_os() == 'Win32':
            ext_scons = which('scons.exe')
            if ext_scons:
                ext_scons_existed = True
                put_string("Found incompatible version of SCons at %s." % ext_scons)
                put_string("It is better to uninstall it to avoid unexpected issues.\n")

        num = multiprocessing.cpu_count()
        multi_thread = "-j" + str(num)
        count = len(cmds)
        if count == 0:
            starttime = time.time()
            if opt.board:
                if ext_scons_existed:
                    if params_str.find("V=1") >= 0:
                        result = os.system("scons --verbose --board=%s -j%d  %s" % (opt.board, num, params_str)) >> 8
                    else:
                        result = os.system("scons --board=%s -j%d %s" % (opt.board, num, params_str)) >> 8
                else:
                    result = os.system("make BOARD=%s MULTITHREADS=%s %s" % (opt.board, multi_thread, params_str)) >> 8
            else:
                if ext_scons_existed:
                    if params_str.find("V=1") >= 0:
                        result = os.system("scons --verbose -j%d %s" % (num, params_str)) >> 8
                    else:
                        result = os.system("scons -j%d %s" % (num, params_str)) >> 8
                else:
                    result = os.system("make MULTITHREADS=%s %s" % (multi_thread, params_str)) >> 8
            maketime = time.time() - starttime
            m, s = divmod(maketime, 60)
            put_string("Build takes %s Minutes %s Seconds." % (int(m), int(s)))
        for cmd in cmds:
            if cmd == "clean":
                if opt.board:
                    if ext_scons_existed:
                        result = os.system("scons -c --board=%s" % opt.board) >> 8
                    else:
                        result = os.system("make clean BOARD=%s" % opt.board) >> 8
                else:
                    if ext_scons_existed:
                        result = os.system("scons -c") >> 8
                    else:
                        result = os.system("make clean") >> 8
                break
            elif cmd == "distclean":
                self.clearSolutionAndBoard(conf.yoc_path)
                if opt.board:
                    if ext_scons_existed:
                        result = os.system("scons -c --board=%s" % opt.board) >> 8
                    else:
                        result = os.system("make clean BOARD=%s" % opt.board) >> 8
                else:
                    if ext_scons_existed:
                        result = os.system("scons -c") >> 8
                    else:
                        result = os.system("make clean") >> 8
                break
            elif "@" in cmd:
                self.saveSolutionAndBoard(conf.yoc_path, cmd)
            else:
                result = os.system("make %s %s" % (cmd, params_str)) >> 8
        return result

    def saveSolutionAndBoard(self, yoc_path, app_board):
        config_file = os.path.join(yoc_path, ".config")
        if not os.path.isfile(os.path.join(yoc_path, ".aos")):
            put_string("Please excute \"aos init\" in the workspace root directory first.")
            exit(-1)
        else:
            v = app_board.split("@")
            if len(v) != 2:
                put_string("Invalid format. Please config it like aos make solution@board -c config")
                exit(-1)

            # update package.yaml of solution: set the specified board as default one
            filename = os.path.join(yoc_path, "solutions", v[0], 'package.yaml')

            if os.path.isfile(filename):
                pack = Package(filename)
                for d in pack.depends:
                    if pack.hw_info.board_name in d:
                        pack.depends.remove(d)
                    l = str(d).replace("}","").replace("'","").split(":")
                depend = {v[1]: l[1]}
                pack.depends.append(depend)
                pack.hw_info.board_name = v[1]
                pack.save(filename)
                # save solution and board in .config file
                with codecs.open(config_file, 'w', 'UTF-8') as f:
                    f.write("{}: {}\n".format("solution", v[0]))
                    f.write("{}: {}\n".format("board", v[1]))
                    put_string("configuration %s written to %s." % (app_board, config_file))
            else:
                put_string("solution %s is not existed." % v[0])

    def clearSolutionAndBoard(self, yoc_path):
        config_file = os.path.join(yoc_path, ".config")
        if os.path.isfile(config_file):
            os.remove(config_file)
        if os.path.isfile('.config_burn'):
            os.remove('.config_burn')
        if os.path.isfile('.config_monitor'):
            os.remove('.config_monitor')
