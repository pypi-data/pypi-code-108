#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import sys
from getopt import getopt

__version__ = 'v1.3.4'

class CheckObs(object):
    def __init__(self, obs_dir):
        self.obs_dir = obs_dir
        self.register_dir = os.path.join(obs_dir, '配置')
        self.character_dir = os.path.join(obs_dir, '特性')
        self.function_dir = os.path.join(obs_dir, '功能')
        self.all_config_dict = {}
        self.err_config = {}

        self.all_character_dict = {}

    def get_md_file_list(self, in_dir):
        md_list = []
        for i in os.listdir(in_dir):
            if not i.startswith('.') and (i.endswith('.md') or i.endswith('.MD')):
                path = os.path.join(in_dir, i)
                md_list.append(path)
        return md_list

    def get_all_config(self):
        md_list = self.get_md_file_list(self.register_dir)
        for md_file in md_list:
            register_name = os.path.basename(md_file[:-3])
            #print(register_name)
            with open(md_file, 'r') as fd:
                info = fd.read()
                fields = re.findall('(?<=## ).*', info)
                for field in fields :
                    config = register_name + "#" + field
                    fix_msg = config.replace('~', '').replace('(', '').replace(')', '').replace(':', '').replace('.', '').replace('/', '')\
                            .replace(',', '').replace('-', '').replace('>', '').replace('[', '').replace(']', '').replace('=', '').replace('…','')\
                            .replace(' ', '').strip(' \n')
                    #print(fix_msg)
                    self.all_config_dict[fix_msg] = {
                            'source': config,
                            'config': ''
                            }

    def check_character(self):
        md_list = self.get_md_file_list(self.character_dir)
        for md_file in md_list:
            character_name = os.path.basename(md_file[:-3])
            #print(character_name)
            with open(md_file, 'r') as fd:
                info = fd.read()
                fields = re.findall('(?<=!\[\[).*(?=\]\])', info)
                for field in fields:
                    fix_msg = field.replace('~', '').replace('(', '').replace(')', '').replace(':', '').replace('.', '').replace('/', '')\
                            .replace(',', '').replace('-', '').replace('>', '').replace('[', '').replace(']', '').replace('=', '').replace('…','')\
                            .replace(' ', '').strip(' \n')
                    if fix_msg in self.all_config_dict:
                        self.all_config_dict[fix_msg]['config'] = True
                    else:
                        self.err_config[character_name] = field

    def get_all_character(self):
        md_list = self.get_md_file_list(self.character_dir)
        for md_file in md_list:
            character_name = os.path.basename(md_file[:-3])
            with open(md_file, 'r') as fd:
                info = fd.read()
                fields = re.findall('(?<=## ).*', info)
                for field in fields :
                    config = character_name + "#" + field
                    fix_msg = config.replace('~', '').replace('(', '').replace(')', '').replace(':', '').replace('.', '').replace('/', '')\
                            .replace(',', '').replace('-', '').replace('>', '').replace('[', '').replace(']', '').replace('=', '').replace('…','')\
                            .replace(' ', '').strip(' \n')
                    #print(fix_msg)
                    self.all_character_dict[fix_msg] = {
                            'source': config,
                            'config': ''
                            }

    def check_function(self):
        md_list = self.get_md_file_list(self.function_dir)
        for md_file in md_list:
            function_name = os.path.basename(md_file[:-3])
            with open(md_file, 'r') as fd:
                info = fd.read()
                fields = re.findall('(?<=!\[\[).*(?=\]\])', info)
                for field in fields:
                    fix_msg = field.replace('~', '').replace('(', '').replace(')', '').replace(':', '').replace('.', '').replace('/', '')\
                            .replace(',', '').replace('-', '').replace('>', '').replace('[', '').replace(']', '').replace('=', '').replace('…','')\
                            .replace(' ', '').strip(' \n')
                    if fix_msg in self.all_character_dict:
                        self.all_character_dict[fix_msg]['config'] = True

    def show(self):
        used_config = []
        not_used_config = []
        mis_config = 0

        used_character = []
        not_used_character = []
        mis_character = 0

        # 获取特性覆盖配置的结果
        for config, used in self.all_config_dict.items():
            if used['config']:
                used_config.append(used['source'])
            else:
                not_used_config.append(used['source'])

        # 获取功能覆盖特性的结果
        for config, used in self.all_character_dict.items():
            if used['config']:
                used_character.append(used['source'])
            else:
                not_used_character.append(used['source'])

        if len(not_used_config) > 0:
            print('\033[1;31m%s: \033[0m'%"下列寄存器未配置")
            mis_config = 1
            for i in not_used_config:
                print("\t",i)
        #if len(self.err_config) > 0:
        #    print('\033[1;31m%s: \033[0m'%"下列配置不在寄存器中")
        #    for character, config in self.err_config.items():
        #        print("\t", character + '.md : ', config)
        if len(not_used_character) > 0:
            print('\033[1;31m%s: \033[0m'%"下列特性未覆盖")
            mis_character = 1
            for i in not_used_character:
                print("\t",i)
        if (not mis_config) and (not mis_character):
            print("\t功能与特性覆盖完整")

    def start(self):
        self.get_all_config()
        self.check_character()

        self.get_all_character()
        self.check_function()
        self.show()

def usage():
    """
    Usage:
        checkobs -d dir
        
        -d: 指定obsidian文档所在路径
    """
    print(usage.__doc__)

def main():
    if len(sys.argv) <= 1:
            usage()
            sys.exit()
    opts,args = getopt(sys.argv[1:],"d:hv")
    obs_dir = "m2m_obs"
    for k,v in opts:
        if k == "-d":
            obs_dir = v
        if k == "-h":
            usage()
            sys.exit()
        if k == "-v":
            print(__version__)
            sys.exit()
    co = CheckObs(obs_dir)
    co.start()

if __name__ == "__main__":
    main()
