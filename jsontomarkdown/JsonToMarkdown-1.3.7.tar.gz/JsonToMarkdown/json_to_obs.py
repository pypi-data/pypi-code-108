#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import sys
from getopt import getopt
try:
    from JsonToMarkdown import libmd
except ImportError:
    import libmd

__version__ = 'v1.3.1'

class TranslateJson(object):
    def __init__(self, js_file, link_path, dir_type, output_md, output_gitbook, output_xmind, \
            save_dir):
        self.js_file = js_file
        self.json_output_dir = os.path.join(link_path, '_json_output')
        self.save_dir = save_dir
        if save_dir:
            self.dirname = os.path.dirname(self.js_file).strip('./')
            self.link_path = os.path.join(link_path, '_json_output', self.dirname)
        else:
            self.link_path = os.path.join(link_path, '_json_output')
        self.dir_type = dir_type
        self.output_dir = 'registers/'
        self.output_md = output_md
        self.output_gitbook = output_gitbook
        self.output_xmind = output_xmind

        self.gitbookpath = ''
        self.markdownpath = ''
        self.data = ''
        self.pre_leval = 0
        self.history_addrr = 0
        self.history_offset = 0
        self.history_base = -1
        self.history_group = {}
        self.pre_group = ''
        self.all_reg_data = ''
        self.all_reg_tex_data = ''
        self.all_reg_list = []
        self.reg_data = ''
        self.path_addr_dict = {}
        self.max_len = ''
        self.reg_rst = '寄存器详细说明\n==============\n\n.. toctree::\n'
        self.reg_rst += '   :caption: Contents:\n\n'
        self.xmind_md = '# REG\n## register\n'

    def get_dpath(self, in_dict, pre_path = ''):
        path_list = []
        for k in in_dict:
            l1_path = os.path.join(pre_path, k)
            if isinstance(in_dict[k], list):
                for n,v in enumerate(in_dict[k]):
                    l2_path = os.path.join(l1_path, str(n))
                    if k == "registers":
                        if "Attribute" not in v or v["Attribute"] != "GROUP":
                            path_list.append(l2_path.strip("/"))
                    if k == "group_reg":
                        if "group_reg" not in v:
                            path_list.append(l2_path.strip("/"))
                    path_list.extend(self.get_dpath(v, l2_path))
        return path_list
    
    def get_delem(self, in_dict, dpath, key = ''):
        path = dpath.strip('/').split('/')
        msg = ''
        for i in path:
            if i.isdigit():
                msg += "["  + i + "]"
            else:
                msg += "[\'"  + i + "\']"
        if key != '':
            msg += "[\'"  + key + "\']"
        return eval("in_dict" + msg)
    
    def get_group_path(self, in_path):
        tmp = []
        for n,v in enumerate(in_path.split("/")):
            if v == "group_reg":
                tmp.append(n)
        path = []
        if tmp != []:
            for i in tmp:
                path.append("/".join(in_path.split("/")[:i]))
        return path 
    
    def enter_group(self, dpath):
        #print("enter group")
        leval = 0
        group_path = self.get_group_path(dpath)
        for i in group_path:
            leval += 1 
            if i not in self.history_group:
                if 'Offset' in self.get_delem(self.js_dict, i):
                    group_step = int(self.get_delem(self.js_dict, i, key='Offset'), 16)
                    #self.history_addrr += group_step
                    self.history_addrr = self.history_offset + group_step
                    if leval >= 2:
                        self.history_offset = self.history_addrr
                    else:
                        self.history_offset = self.history_base + group_step
                elif 'Step' in self.get_delem(self.js_dict, i):
                    group_step = int(self.get_delem(self.js_dict, i, key='Step'), 16)
                    self.history_addrr += group_step
                    self.history_offset = self.history_addrr
                if 'depth' in self.get_delem(self.js_dict, i):
                    depth = self.get_delem(self.js_dict, i, key = 'depth')
                else:
                    depth = 1
                self.history_group[i] = {'depth':depth, 'num': 1, 'start': self.history_offset}
    
    def exit_group(self, dpath):
        #print("exit group")
        self.pre_group_list = self.get_group_path(self.pre_group + "/group_reg")
        now_group_list = self.get_group_path(dpath)
        self.exit_group_list = []
        self.enter_group_list = []
        for i in now_group_list:
            if i in self.pre_group_list:
                self.pre_group_list.remove(i)
            else:
                self.enter_group_list.append(i)
        self.exit_group_list = self.pre_group_list
        elen = len(self.exit_group_list)
        exit_step = 0
        next_num = 0 
        for i in range(elen):
            index = elen - i -1
            path = self.exit_group_list[index]
            if i == 0:
                next_num = self.history_group[path]['depth'] * self.history_group[path]['num']
            else:
                next_num = self.history_group[path]['depth'] * \
                        (self.history_group[path]['num'] + next_num -1)
        self.history_addrr = self.history_group[path]['start'] + (next_num-1) * (0x0004)
        self.history_offset = self.history_addrr
    
        if len(self.enter_group_list) > 0:
            self.enter_group(dpath)
    
    
    def get_addr(self, dpath):
        base_changed = 0
        block_path = dpath.split("registers")[0]
        base_addr = int(self.get_delem(self.js_dict, block_path, key='base_addr'), 16)
        if self.history_base == -1:
            self.history_base = base_addr
            self.history_offset = base_addr
            self.history_addrr = base_addr
        if self.history_base != base_addr:
            base_changed = 1
            self.history_base = base_addr
            self.history_offset = base_addr
            self.history_addrr = base_addr
    
        group_path_list = self.get_group_path(dpath)
        for i in group_path_list:
            if i in self.history_group:
                self.history_group[i]['num'] +=1
        if group_path_list != []:
            group_path = group_path_list[-1]
        else:
            group_path = ''
        if base_changed:
            self.pre_group = group_path
        else:
            if group_path != self.pre_group:
                if self.pre_group == '':
                    self.enter_group(dpath)
                else:
                    if group_path.find(self.pre_group) >= 0:
                        self.enter_group(dpath)
                    else:
                        self.exit_group(dpath)
                self.pre_group = group_path
        if 'Step' in self.get_delem(self.js_dict, dpath):
            offset_addr = self.get_delem(self.js_dict, dpath, key='Step')
            offset_addr = int(offset_addr,16)
            now_addr =  self.history_addrr + offset_addr
            self.history_addrr = now_addr
            return hex(now_addr)
        if 'Offset' in self.get_delem(self.js_dict, dpath):
            offset_addr = self.get_delem(self.js_dict, dpath, key='Offset')
            offset_addr = int(offset_addr,16)
            #now_addr =  self.history_offset + offset_addr
            if group_path:
                now_addr =  self.history_offset + offset_addr
            else:
                now_addr =  self.history_base + offset_addr
            self.history_addrr = now_addr
            return hex(now_addr)
    
    def find_group_path(self, group, root_path):
        group_list = []
        group_list.append(root_path)
        for i in range(len(group['group_reg'])):
            path = root_path + "/group_reg/" + str(i)
            if 'group_reg' in group['group_reg'][i]:
                group_list.extend(self.find_group_path(group['group_reg'][i], path))
        return group_list
    
    def get_group_dict(self, dpath):
        group_dict = {}
        group = self.get_delem(self.js_dict, dpath)
        if 'depth' in group:
            depth = group['depth']
        else:
            depth = 1
        group_dict[dpath] = {"depth":depth, "num":0}
        for i in group['group_reg']:
            group_dict[dpath]['num'] += 1
        return group_dict
    
    def create_groupmsg(self):
        group_msg = {
                'step':'',
                'range':'',
                'group':[],
                }
        return group_msg
    
    def get_groupmsg(self, dpath):
        msg_list = ["N","J","M","k","Z","I","D"]
        group_path_list = self.get_group_path(dpath)
        group_path = group_path_list[0]
        group_end = group_path_list[-1]
        group = self.get_delem(self.js_dict, group_path)
        group_list = self.find_group_path(group, group_path)
        for n, path in enumerate(group_list):
            if path == group_end:
                end = n
        group_dict = {}
        for i in group_list:
            group_dict.update(self.get_group_dict(i))
        #print(group_dict)
        step_msg = ''
        scope_msg = ''
        total_msg = ''
        for j in range(len(group_list)):
            elen = len(group_list[j:])
            next_num = 0 
            for i in range(elen):
                index = elen - i -1
                path = group_list[j + index]
                if index == 0:
                    if next_num == 0:
                        next_num = group_dict[path]['num']
                    else:
                        next_num = (group_dict[path]['num'] + next_num -1)
                elif i == 0:
                    next_num = group_dict[path]['depth'] * group_dict[path]['num']
                else:
                    next_num = group_dict[path]['depth'] * \
                            (group_dict[path]['num'] + next_num -1)
            step = next_num * (0x0004)
            step_msg += "+" + msg_list[j] + "*" + hex(step)
            if total_msg == '':
                group_msg = self.create_groupmsg()
                total_msg = group_msg
            else:
                group_msg['group'].append(self.create_groupmsg())
                group_msg = group_msg['group'][0]
            group_msg['step'] = step
            group_msg['range'] = group_dict[path]['depth']
            scope_msg += " " + msg_list[j] + "的范围为0~" + str(group_dict[path]['depth']-1)
            if j == end:
                break
        #print(step_msg)
        #print(scope_msg)
        return step_msg, scope_msg, total_msg
    
    
    def get_reserve_fields(self, fields, bit_num):
        bit_num = int(bit_num)
        re_map = [[0, bit_num -1]]
        re_fields = []
        for f in fields:
            index_range = f['range']
            scope = index_range.strip("[]").split(":")
            end = int(scope[0])
            start = int(scope[-1])
            for r in re_map:
                if r[0] <= start and r[-1] >= end:
                    re_map.remove(r)
                    if r[0] != start:
                        re_map.append([r[0], start - 1])
                    if r[-1] != end:
                        re_map.append([end + 1, r[-1]])
        #print(re_map)
        for r in re_map:
            frange = "(" + str(r[-1]) + "-" + str(r[0]) + ")"
            re_fields.append({
                "name": "reserved",
                "range": frange,
                "reset_value": "0",
                })
        #print(re_fields)
        return re_fields
    
    
    def show_group(self, group, name, des, st_addr, hex_reset, fields):
        for i in range(int(group['range'])):
            new_name = name + "-" + str(i)
            new_addr = st_addr + i * group['step']
            if group['group'] != []:
                for g in group['group']:
                    self.show_group(lm, g, new_name, des, new_addr, hex_reset)
            else:
                self.all_reg_list.append({
                    'name':new_name,
                    'addr':self.zero_fill(hex(new_addr)),
                    'reset':hex_reset,
                    'des':des,
                    'field':fields,
                    })

    def add_reset(self, reset, index_range, value):
        if index_range.startswith('('):
            scope = index_range.strip("()").split("-")
        else:
            scope = index_range.strip("[]").split(":")
        end = int(scope[0]) + 1
        start = int(scope[-1])
        if int(value, 16) == 0:
            pass
        else:
            fill_list = list(bin(int(value, 16))[2:])
            for i in range(start, end):
                if fill_list != []:
                    reset[i] = fill_list.pop(-1)
                else:
                    break

    def get_reset(self, reset, bit_num):
        bit_num = int(bit_num)
        value = ''
        for i in range(bit_num):
            value += str(reset[bit_num -1 -i])
        tmp = hex(int(value, 2))[2:]
        #if tmp == '0':
        #    hex_value = "0x" + tmp
        #else:
        hex_value = "0x" + tmp.zfill(8)
        return hex_value

    def zero_fill(self, in_hex):
        new_hex = "0x" + in_hex[2:].zfill(self.max_len)
        return new_hex

    def relist_fields(self, fields):
        fields_len = len(fields)
        for i in range(fields_len):
            for j in range(i+1, fields_len):
                i_f = fields[i]
                i_index_range = i_f['range']
                if i_index_range.startswith('('):
                    i_scope = i_index_range.strip("()").split("-")
                else:
                    i_scope = i_index_range.strip("[]").split(":")
                i_end = int(i_scope[0])
                i_start = int(i_scope[-1])
                j_f = fields[j]
                j_index_range = j_f['range']
                if j_index_range.startswith('('):
                    j_scope = j_index_range.strip("()").split("-")
                else:
                    j_scope = j_index_range.strip("[]").split(":")
                j_end = int(j_scope[0])
                j_start = int(j_scope[-1])
                if i_end <= j_end:
                    fields[i], fields[j] = fields[j], fields[i]

    def create_md(self, dpath, bit_num):
        is_group = 0
        register = self.get_delem(self.js_dict, dpath)
        name = self.get_delem(self.js_dict, dpath, key = 'RegName' )
        name = name.upper()
        addr = self.zero_fill(self.path_addr_dict[dpath])
        if dpath.find("group_reg") >= 0:
            is_group = 1
            addr_msg, scope_msg, group_msg = self.get_groupmsg(dpath)
            addr = str(addr) + addr_msg + "(" + scope_msg + " )"
        if name.endswith("RESERVED"):
            return -1
        des = self.get_delem(self.js_dict, dpath, key = 'Description')
        fields = self.get_delem(self.js_dict, dpath, key = 'Fields')
        reserve_fields = self.get_reserve_fields(fields, bit_num)
        fields.extend(reserve_fields)
        #print(fields)
        self.relist_fields(fields)
        #print(">>>>>>>>>>>>>>>>>>>>>")
        #print(name)
        #print(addr)
        #print(fields)
        ###################
        reset = {}
        for k,v in enumerate("0"*bit_num):
            reset[k] = v
        for f in fields:
            self.add_reset(reset, f['range'], f['reset_value'])
        hex_reset = self.get_reset(reset, bit_num)
        if is_group:
            st_addr = addr.split("+")[0]
            st_name = name + '(0~' + str(group_msg['range'] - 1) + ')'
            self.all_reg_list.append({
                'name':st_name,
                'addr':st_addr,
                'reset':hex_reset,
                'des':des,
                'field':fields,
                })
            #st_addr = int(addr.split("+")[0], 16)
            #self.show_group(group_msg, name ,des, st_addr, hex_reset, fields)
        else:
            st_addr = addr
            self.all_reg_list.append({
                'name':name,
                'addr':st_addr,
                'reset':hex_reset,
                'des':des,
                'field':fields,
                })
        #print(st_addr)
        #print(">>>>>>>>>>>>>>>>>>>>>")
        ###################
        #reg_dir = str(st_addr) + '_' + name
        #reg_path = os.path.join(self.output_dir, reg_dir)
        #if not os.path.exists(reg_path):
        #    os.makedirs(reg_path)

        #for i in fields:
        #    field_md = i['range'] + '_' + i['name'] + '.md'
        #    field_path = os.path.join(self.output_dir, reg_dir, field_md)
        #    with open(field_path, 'w') as fd:
        #        if 'description' in i:
        #            for d in i['description'].split(';'):
        #                fd.write('## ' + d + '\n')


    def add_xmind_md(self, name, des):
        self.xmind_md += '* ' + name + '\n'
        des = des.replace('：',':').replace('；',';')
        if re.findall(';[0-9]:|。[0-9]:', des):
            for tmp_des in re.split('[;。]', des):
                tmp_des = tmp_des.strip(' ')
                if not re.match('^[0-9]:', tmp_des):
                    self.xmind_md += '* > ' + tmp_des + '\n'
            for tmp_des in re.split('[;。]', des):
                tmp_des = tmp_des.strip(' ')
                if re.match('^[0-9]:', tmp_des):
                    self.xmind_md += '    * ' + tmp_des + '\n'
        else:
            for tmp_des in re.split('[。]', des)[1:]:
                self.xmind_md += '* > ' + tmp_des + '\n'
            tmp_des = re.split('[。]', des)[0]
            self.xmind_md += '    * ' + tmp_des + '\n'
    
    def add_description_table(self, lm, argv):
        line = lm.md_create_body_line2(argv)
        return line

    def start(self, json_file):
        with open(json_file, 'rb') as jf:
            js_dict = json.load(jf)
            #print(type(js_dict))
        return js_dict

    def relist(self, in_list):
        new_list = []
        list_len = len(in_list)
        for i in range(list_len):
            for j in range(i, list_len):
                #print(in_list[j])
                if int(in_list[i]['addr'], 16) >= int(in_list[j]['addr'], 16):
                    in_list[i], in_list[j] = in_list[j], in_list[i] 

    def main(self):
        file_msg = os.path.basename(self.js_file).split(".json")[0]
        self.js_dict =self.start(self.js_file)
        self.js_dpath = self.get_dpath(self.js_dict)
        lm = libmd.LibMarkdown()
        for i in self.js_dpath:
            addr = self.get_addr(i)
            self.path_addr_dict[i] = addr
            name = self.get_delem(self.js_dict, i, key = 'RegName' )
            #print(name, "(" + addr + ")")
        self.max_len = len(self.path_addr_dict[self.js_dpath[-1]][2:])
        for i in range(int(len(self.js_dpath))):
            name = self.get_delem(self.js_dict, self.js_dpath[i], key = 'RegName' )
            name = name.upper()
            if name != "RESERVED":
                dpath = self.js_dpath[i]
                bit_num = self.get_delem(self.js_dict, dpath.split('registers')[0], \
                        key = 'd_width')
                self.create_md(self.js_dpath[i], bit_num)
        self.relist(self.all_reg_list)
        list_data = ''
        for reg in self.all_reg_list:
            name = reg['name']
            addr = reg['addr']
            #print(str(addr) + '_' + name)
            list_data += '[[' + str(addr) + '_' + name  + ']]\n'
            fields = reg['field']
            ###########################
            #reg_dir = str(addr) + '_' + name
            #reg_path = os.path.join(self.output_dir, reg_dir)
            #if not os.path.exists(reg_path):
            #    os.makedirs(reg_path)

            #for i in fields:
            #    field_md = i['range'] + '_' + i['name'] + '.md'
            #    field_path = os.path.join(self.output_dir, reg_dir, field_md)
            #    with open(field_path, 'w') as fd:
            #        if 'description' in i:
            #            for d in i['description'].split(';'):
            #                fd.write('## ' + d + '\n')
            ###########################
            reg_md = str(addr) + '_' + name + '.md'
            reg_path = os.path.join(self.output_dir, reg_md)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            with open(reg_path, 'w') as fd:
                for i in fields:
                    fd.write('# ' + i['range'].replace('[','(').replace(']', ')') \
                            + '_' + i['name'] + ' (' + str(addr) + '_' + name + ')\n')
                    if 'description' in i:
                        for d in i['description'].split(';'):
                            fd.write('## ' + d + ' (' + str(addr) + '_' + name + '->' \
                                    + i['range'].replace('[','(').replace(']', ')') \
                                    + '_' + i['name'] + ')\n')
        with open(os.path.join(self.output_dir, 'list.md'), 'w') as fl:
            fl.write(list_data)
        print("Json to obsidian Success : ./registers")


def usage():
    """
    Usage:
        jsontomd -f json_file
      exp
        jsontomd -f npu_register.json

    parameters:
        -f : 指定json文件
    """
    print(usage.__doc__)

def main():
    if len(sys.argv) <= 1:
            usage()
            sys.exit()
    opts,args = getopt(sys.argv[1:],"f:hv")
    js_file = "demo.json"
    link_path = ''
    output_md = 1
    output_gitbook = 0
    output_xmind = 0
    save_dir = 0
    dir_type = "alone"
    for k,v in opts:
        if k == "-f":
            js_file = v
        if k == "-h":
            usage()
            sys.exit()
        if k == "-v":
            print(__version__)
            sys.exit()
    #print("opts:", opts, "args", args)
    tj = TranslateJson(js_file, link_path, dir_type, output_md, output_gitbook, output_xmind, \
            save_dir)
    tj.main()

if __name__ == "__main__":
    main()
