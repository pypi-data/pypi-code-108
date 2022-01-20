#!/usr/bin/env python 
# -*- coding:utf-8 -*-

'''
:Name:	YamlFileOperate.py
:Author:	Zheng Yabiao
:Usage:	Yaml file operation
:Data:	2017.5.23
:Version: v1.0
'''

from collections import defaultdict

class YamlWrite:
    """Class of yaml file write out

    :Args:
        input: The yaml file of writing out
    :Returns:
        None
    """
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode
    def yaml_write_dict(self, input_dict, level = 0):
        """Dictionary write out

        :Args:
            * input_dict: The dictionary
            * level (int): The indent level
        :Returns:
            None
        """
        space = int(level) * 4 * " "
        for k in input_dict:
            if not k: continue
            file_handle = open(self.file, self.mode)
            file_handle.write("%s%s:\n"%(space, k))
            file_handle.close()
            if type(input_dict[k]) == type(1) or type(input_dict[k]) == type("1"):
                self.yaml_write_str(input_dict[k], level + 1)
            elif type(input_dict[k]) == type([1, 2]):
                self.yaml_write_list(input_dict[k], level + 1)
            elif type(input_dict[k]) == type({1: 2}) or type(input_dict[k]) == type(defaultdict()):
                self.yaml_write_dict(input_dict[k], level + 1)
    def yaml_write_list(self, input_list, level = 0):
        """List write out

        :Args:
            * input_list: list
            * space: the number of spaces behind the element
        :Returns:
            None
        """
        file_handle = open(self.file, self.mode)
        space = int(level) * 4 * " "
        for i in input_list:
            file_handle.write("%s- %s\n" %(space, i))
    def yaml_write_str(self, input_strg, level = 0):
        """String write out

        :Args:
            * input_strg: string
            * level: the number of spaces behind the string
        :Returns:
            None
        """
        file_handle = open(self.file, self.mode)
        space = int(level) * 4 * " "
        file_handle.write("%s%s\n" %(space, input_strg))
