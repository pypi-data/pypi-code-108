# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function
import os
import shutil
from aostools import *
from aostools.subcmds import all_commands
from aostools.cmd import __version__

class Createproject(Command):
    common = True
    helpSummary = "Create project from templet"
    helpUsage = """
%prog [-b board] [-t templet] [-d destdir] [-r repo] [-B branch] [solution_name]
"""
    helpDescription = """
Create a new workspace and intialize it, 
Create project from templet
"""

    def _Options(self, p):
        p.add_option('-b', '--board',
                     dest='board', action='store', type='str', default=None,
                     help='select board templet')
        p.add_option('-t', '--templet',
                     dest='templet', action='store', type='str', default="helloworld_demo",
                     help='select project templet')
        p.add_option('-d', '--destdir',
                     dest='destdir', action='store', type='str', default=None,
                     help='workspace destination directory')
        p.add_option('-r', '--repo',
                     dest='repo', action='store', type='str', default=None,
                     help='the manifest repo address')
        p.add_option('-B', '--branch',
                     dest='branch', action='store', type='str', default=None,
                     help='the manifest repo branch')


    def Execute(self, opt, args):
        invalid_opt = False
        if not opt.board:
            put_string("Select board with option -b or --board.")
            invalid_opt = True
        if not opt.destdir:
            put_string("Specify workspace destination directory with option -d or --destdir.")
            invalid_opt = True
        if not args:
            put_string("Specify the solution name.")
            invalid_opt = True
        if invalid_opt:
            put_string("")
            self.Usage()
            exit(-1)
        opt.destdir = os.path.abspath(opt.destdir)
        solution_name = args[0]

        # mkdir destdir
        created_newdir = ""
        inited_workspace = False
        if os.path.exists(opt.destdir):
            if os.path.isdir(opt.destdir):
                pass
            else:
                put_string("\"%s\" is not directory." % opt.destdir)
                exit(-1)
        else:
            put_string("create directory: %s" % opt.destdir)
            os.makedirs(opt.destdir)
            created_newdir = opt.destdir

        # enter into destdir
        put_string("enter into directory: %s" % opt.destdir)
        os.chdir(opt.destdir)

        # check destdir is under an existed workspace
        conf = Configure()
        if conf.init:
            if(opt.destdir == conf.yoc_path) :
                put_string("Workspace is already existed at %s." % opt.destdir)
                # opt.destdir = conf.yoc_path
                os.chdir(opt.destdir)
                if created_newdir:
                    rmtree_enhanced(created_newdir)
                    created_newdir = ""
            else:
                put_string("Workspace is not existed at %s." % opt.destdir)
                os.chdir(opt.destdir)
                if created_newdir:
                    rmtree_enhanced(created_newdir)
                    created_newdir = opt.destdir
            # put_string("Workspace is already existed at %s." % opt.destdir)
        cur_dir = os.getcwd()

        # check solution is already existed
        solution_path = os.path.join(opt.destdir, "solutions", solution_name)
        if os.path.exists(solution_path):
            put_string("Directory \"%s\" is already existed." % solution_path)
            if created_newdir:
                # if cur_dir == created_newdir:
                os.chdir(os.path.dirname(cur_dir))
                rmtree_enhanced(created_newdir)
            exit(-1)

        # aos init
        if not os.path.exists(".aos"):
            try:
                cmd = all_commands['init']
                argv = []
                if opt.repo:
                    argv.append(opt.repo)
                if opt.branch:
                    argv.append('-b')
                    argv.append(opt.branch)
                put_string("aos init %s" % ' '.join(argv))
                copts, cargs = cmd.OptionParser.parse_args(argv)
                result = cmd.Execute(copts, cargs)
                inited_workspace = True
            except Exception as e:
                put_string("AosCommand error:", e)
                if created_newdir:
                    # if cur_dir == created_newdir:
                    os.chdir(os.path.dirname(cur_dir))
                    rmtree_enhanced(created_newdir)
                exit(-1)
        elif conf.init:
            if opt.repo or opt.branch:
                # default url is conf.repo, and default branch is master
                opt.repo = conf.repo if not opt.repo else opt.repo
                opt.branch = "master" if not opt.branch else opt.branch
                if opt.repo != conf.repo or opt.branch != conf.branch:
                    put_string("\nThe workspace is already initialized as %s(%s)." % (conf.repo, conf.branch))
                    put_string("It can not be reinitialzed to %s(%s)" % (opt.repo, opt.branch))
                    if created_newdir:
                        os.chdir(os.path.dirname(cur_dir))
                        rmtree_enhanced(created_newdir)
                    exit(-1)

        def remove_project_files(cur_dir, created_newdir, inited_workspace):
            if created_newdir:
                # if cur_dir == created_newdir:
                os.chdir(os.path.dirname(cur_dir))
                rmtree_enhanced(created_newdir)
            elif inited_workspace:
                os.remove(".aos")
                rmtree_enhanced("components")
                rmtree_enhanced("kernel")
                rmtree_enhanced("hardware")
                rmtree_enhanced("solutions")
                rmtree_enhanced("documentation")

        # aos install [templet] and [board]
        try:
            cmd = all_commands['install']
            argv = ['aos_sdk', opt.templet, opt.board]
            if opt.branch:
                argv.append('-b')
                argv.append(opt.branch)
            put_string("aos install %s" % ' '.join(argv))
            copts, cargs = cmd.OptionParser.parse_args(argv)
            result = cmd.Execute(copts, cargs)
        except Exception as e:
            put_string("AosCommand error:", e)
            remove_project_files(cur_dir, created_newdir, inited_workspace)
            exit(-1)
        
        # aos copy [templet] [solution_name]
        # rename directory will fail in vscode IDE of windows platform, change to copy
        if opt.templet != solution_name:
            try:
                cmd = all_commands['copy']
                argv = [opt.templet, solution_name]
                put_string("aos copy %s" % ' '.join(argv))
                copts, cargs = cmd.OptionParser.parse_args(argv)
                result = cmd.Execute(copts, cargs)
                if result != 0:
                    remove_project_files(cur_dir, created_newdir, inited_workspace)
                    exit(-1)
            except Exception as e:
                put_string("AosCommand error:", e)
                remove_project_files(cur_dir, created_newdir, inited_workspace)
                exit(-1)

            templet_path = os.path.join(cur_dir, "solutions", opt.templet)
            rmtree_enhanced(templet_path)

        # update package.yaml of solution: set the specified board as default one
        filename = os.path.join(cur_dir, "solutions", solution_name, 'package.yaml')

        if os.path.isfile(filename):
            pack = Package(filename)
            for d in pack.depends:
                if opt.board in d:
                    pack.depends.remove(d)
            pack.depends.append({opt.board: "master"})
            pack.hw_info.board_name = opt.board
            pack.save(filename)
        else:
            put_string("File \"%s\" is not existed" % filename)
            remove_project_files(cur_dir, created_newdir, inited_workspace)
            exit(-1)

        # success
        put_string("Create solution \"%s\" successfully." % solution_name)
        check_remote_version(__version__)
        return 0