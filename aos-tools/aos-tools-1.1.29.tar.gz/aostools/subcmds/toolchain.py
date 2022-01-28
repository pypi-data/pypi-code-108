# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function

import os
from aostools import *

enable_esp32 = True

class Toolchain(Command):
    common = True
    helpSummary = "Install toolchain"
    if enable_esp32:
        helpUsage = """
    %prog [--all] [--arm_none] [--csky] [--riscv] [--arm_ali] [--riscv64_ali] [--xtensa-esp32]
    """
    else:
        helpUsage = """
    %prog [--all] [--arm_none] [--csky] [--riscv] [--arm_ali] [--riscv64_ali]
    """
    helpDescription = """
Install toolchain.
"""

    def _Options(self, p):
        p.add_option('-c', '--csky',
                     dest='install_csky', action='store_true',
                     help=' install(or uninstall if with -d, --delete) csky-elfabiv2-tools')
        p.add_option('-r', '--riscv',
                     dest='install_riscv', action='store_true',
                     help=' install(or uninstall if with -d, --delete) riscv-elf-tools')
        p.add_option('-a', '--arm_none',
                     dest='install_arm_none', action='store_true',
                     help=' install(or uninstall if with -d, --delete) arm-none-eabi')
        p.add_option('-i', '--arm_ali',
                     dest='install_arm_ali', action='store_true',
                     help=' install(or uninstall if with -d, --delete) arm-ali-aoseabi')
        p.add_option('-v', '--riscv64_ali',
                     dest='install_riscv64_ali', action='store_true',
                     help=' install(or uninstall if with -d, --delete) riscv64-ali-aos')
        if enable_esp32:
            p.add_option('-x', '--xtensa-esp32',
                        dest='install_xtensa_esp32', action='store_true',
                        help=' install(or uninstall if with -d, --delete) xtensa-esp32-elf')
            p.add_option('-A', '--all',
                        dest='install_all', action='store_true',
                        help=' install(or uninstall if with -d, --delete) csky-elfabiv2-tools, riscv-elf-tools, arm-none-eabi, arm-ali-aoseabi, riscv64-ali-aos and xtensa-esp32-elf')
        else:
            p.add_option('-A', '--all',
                        dest='install_all', action='store_true',
                        help=' install(or uninstall if with -d, --delete) csky-elfabiv2-tools, riscv-elf-tools, arm-none-eabi, arm-ali-aoseabi and riscv64-ali-aos')
            p.add_option('-d', '--delete',
                        dest='uninstall_toolchain', action='store_true',
                        help=' uninstall specific toolchain')

    def Execute(self, opt, args):
        need_usage = True
        tool = ToolchainYoC()
        if opt.install_all:
            if not opt.uninstall_toolchain:
                tool.check_toolchain('csky-abiv2-elf', 1)
                tool.check_toolchain('riscv64-unknown-elf', 1)
                tool.check_toolchain('arm-none-eabi', 1)
                tool.check_toolchain('arm-ali-aoseabi', 1)
                tool.check_toolchain('riscv64-ali-aos', 1)
                if enable_esp32:
                    tool.check_toolchain('xtensa-esp32-elf', 1)
            else:
                tool.uninstall_toolchain('csky-abiv2-elf')
                tool.uninstall_toolchain('riscv64-unknown-elf')
                tool.uninstall_toolchain('arm-none-eabi')
                tool.uninstall_toolchain('arm-ali-aoseabi')
                tool.uninstall_toolchain('riscv64-ali-aos')
                if enable_esp32:
                    tool.uninstall_toolchain('xtensa-esp32-elf')
            need_usage = False
        else:
            if opt.install_csky:
                if not opt.uninstall_toolchain:
                    tool.check_toolchain('csky-abiv2-elf', 1)
                else:

                    tool.uninstall_toolchain('csky-abiv2-elf')
                need_usage = False
            if opt.install_riscv:
                if not opt.uninstall_toolchain:
                    tool.check_toolchain('riscv64-unknown-elf', 1)
                else:
                    tool.uninstall_toolchain('riscv64-unknown-elf')
                need_usage = False
            if opt.install_arm_none:
                if not opt.uninstall_toolchain:
                    tool.check_toolchain('arm-none-eabi', 1)
                else:
                    tool.uninstall_toolchain('arm-none-eabi')
                need_usage = False
            if opt.install_arm_ali:
                if not opt.uninstall_toolchain:
                    tool.check_toolchain('arm-ali-aoseabi', 1)
                else:
                    tool.uninstall_toolchain('arm-ali-aoseabi')
                need_usage = False
            if opt.install_riscv64_ali:
                if not opt.uninstall_toolchain:
                    tool.check_toolchain('riscv64-ali-aos', 1)
                else:
                    tool.uninstall_toolchain('riscv64-ali-aos')
                need_usage = False
            if enable_esp32:
                if opt.install_xtensa_esp32:
                    if not opt.uninstall_toolchain:
                        tool.check_toolchain('xtensa-esp32-elf', 1)
                    else:
                        tool.uninstall_toolchain('xtensa-esp32-elf')
                    need_usage = False
        if need_usage:
            self.Usage()
        return 0
