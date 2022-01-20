#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from getopt import getopt
try:
    from JsonToMarkdown import preprocess
    from JsonToMarkdown import libsvg
    from JsonToMarkdown import libmd
except ImportError:
    import preprocess
    import libsvg
    import libmd

__version__ = 'v1.3.7'

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
        self.group_set = []
        self.pre_group = ''
        self.all_reg_data = ''
        self.all_reg_tex_data = ''
        self.all_reg_list = []
        self.reg_data = '# 寄存器详细说明\n\n'
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
        #print(group_path)
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
        #print(dpath)
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
        if len(group_path_list) > 0:
            if group_path_list not in self.group_set:
                self.group_set.append(group_path_list)
                for i in group_path_list:
                    if i in self.history_group:
                        self.history_group[i]['num'] +=1
            else:
                i = group_path_list[-1]
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
            #print((self.history_offset))
            #print('history: ', hex(self.history_offset))
            offset_addr = self.get_delem(self.js_dict, dpath, key='Offset')
            offset_addr = int(offset_addr,16)
            #now_addr =  self.history_offset + offset_addr
            if group_path:
                now_addr =  self.history_offset + offset_addr
            else:
                now_addr =  self.history_base + offset_addr
            #print('offset: ', hex(offset_addr))
            self.history_addrr = now_addr
            #print('now_addr: ', hex(now_addr))
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
            frange = "[" + str(r[-1]) + ":" + str(r[0]) + "]"
            re_fields.append({
                "name": "reserved",
                "range": frange,
                "reset_value": "0",
                })
        #print(re_fields)
        return re_fields
    
    
    def show_group(self, lm, group, name, des, st_addr, hex_reset):
        for i in range(int(group['range'])):
            new_name = name + "||" + str(i)
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
                    })

    def add_reset(self, reset, index_range, value):
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
                i_scope = i_index_range.strip("[]").split(":")
                i_end = int(i_scope[0])
                i_start = int(i_scope[-1])
                j_f = fields[j]
                j_index_range = j_f['range']
                j_scope = j_index_range.strip("[]").split(":")
                j_end = int(j_scope[0])
                j_start = int(j_scope[-1])
                if i_end <= j_end:
                    fields[i], fields[j] = fields[j], fields[i]

    
    def create_md3(self, dpath, lm, bit_num = 32):
        ls = libsvg.LibSVG()
        reset = {}
        for k,v in enumerate("0"*bit_num):
            reset[k] = v
    
        is_group = 0
        register = self.get_delem(self.js_dict, dpath)
        name = self.get_delem(self.js_dict, dpath, key = 'RegName' )
        name = name.upper()
        #addr = self.get_addr(dpath)
        addr = self.zero_fill(self.path_addr_dict[dpath])
        if dpath.find("group_reg") >= 0:
            is_group = 1
            addr_msg, scope_msg, group_msg = self.get_groupmsg(dpath)
            addr = str(addr) + addr_msg + "(" + scope_msg + " )"
        #print(name, "(" + addr + ")")
    
        #if name.endswith("reserved"):
        if name.endswith("RESERVED"):
            return -1
    
        des = self.get_delem(self.js_dict, dpath, key = 'Description')
        #self.xmind_md += '### ' + name + '\n' + '> ' + des + '\n'
        self.xmind_md += '### ' + name + '\n'
        fields = self.get_delem(self.js_dict, dpath, key = 'Fields')
        reserve_fields = self.get_reserve_fields(fields, bit_num)
        fields.extend(reserve_fields)
        self.relist_fields(fields)

        table = ls.create_blank_form(bit_num)
        for f in fields:
            ls.add_line(table, f['range'])
        for f in fields:
            ls.add_reset_value(table, f['range'], f['reset_value'], f['name'])
            self.add_reset(reset, f['range'], f['reset_value'])
        for f in fields:
            ls.add_name(table, f['range'], f['name'])
        hex_reset = self.get_reset(reset, bit_num)
        if is_group:
            st_addr = int(addr.split("+")[0], 16)
            self.show_group(lm, group_msg, name ,des, st_addr, hex_reset)
        else:
            st_addr = addr
            self.all_reg_list.append({
                'name':name,
                'addr':st_addr,
                'reset':hex_reset,
                'des':des,
                })
        #ls.write_down(table)
        ls.indent(table)
        svg_data = ls.svg_transform(table)
        svg_name = name + ".svg"
        with open(svg_name, "w") as fd:
            fd.write(svg_data)
        #register_data = "![](" + svg_name + ")\n<br>"
        register_data = "![](" + svg_name + ")\n"

        line = lm.md_create_title_line(['位域','变量名', '属性', '默认值', '描述'])
        register_data += "\n\n" + line
        fields_len = len(fields)
        for i in range(fields_len):
            #f = fields[fields_len - i -1]
            f = fields[i]
            if f['name'] != 'reserved':
                #self.xmind_md += '* ' + f['name'] + '\n    * ' + f['description'] + '\n'
                self.add_xmind_md(f['name'], f['description'])

                line = self.add_description_table(lm, [f['range'], f['name'], \
                        f['access'], f['reset_value'], f['description']])
                register_data += line
            else:
                line = self.add_description_table(lm, [f['range'], f['name'], \
                        '','',''])
                register_data += line
    
        #table_title = 'Register:' + name + ' ('  + addr + ')'
        reg_addr_msg = '地址偏移 : '  + addr
        reg_hex_reset = '默认值 : ' + hex_reset
        register_data = "## " + name + "\n\n" + reg_addr_msg + '<br>' + \
                reg_hex_reset + '\n' + register_data
        if self.output_md:
            os.system("mv " + svg_name + " " + self.markdownpath)
            self.data += register_data +'\n'
        if self.output_gitbook:
            os.system("mv " + svg_name + " " + self.gitbookpath)
            #register_data += '\n<br>\n'
            register_data += '\n'
            file_path = os.path.join(self.gitbookpath, name + '.md')
            self.reg_rst += '   ' + name + '.md\n'
            with open(file_path, 'w') as fd:
                fd.write(register_data)
            #self.reg_data += '{% include "./' + name +  '.md" %}\n'
            self.reg_data += register_data + '\n'

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
    
    def add_description(self, name, des, access):
        des = des.replace("；", ";")
        dess = des.split(";")
        msg = ''
        if len(dess) == 1:
            line = "**" + name.upper() + "** **["+ access + "]** :&emsp;" + des.strip(" ")
        else:
            for i in dess:
                msg += "<br>&emsp;" + i.strip(" ")
            line = "**" + name.upper() + "** **[" + access + "]** :" + msg
        return line

    def add_description_table(self, lm, argv):
        line = lm.md_create_body_line2(argv)
        return line

    def check_file(self, file_name):
        if self.dir_type != "link":
            return
        if os.path.exists(os.path.join(self.json_output_dir, file_name)):
            add_cmd = "cat " + os.path.join(self.gitbookpath, file_name) + " >> " \
                    + os.path.join(self.json_output_dir, file_name)
            os.system(add_cmd)
        else:
            mv_cmd = "mv " + os.path.join(self.gitbookpath, file_name) + " " \
                    + os.path.join(self.json_output_dir, file_name)
            os.system(mv_cmd)

    def relist(self, in_list):
        new_list = []
        list_len = len(in_list)
        for i in range(list_len):
            for j in range(i, list_len):
                #print(in_list[j])
                if int(in_list[i]['addr'], 16) >= int(in_list[j]['addr'], 16):
                    in_list[i], in_list[j] = in_list[j], in_list[i] 

    def create_all_reg_data(self, lm):
        for i in self.all_reg_list:
            self.all_reg_data += lm.md_create_body_line([i['name'], i['addr'], \
                    i['reset'], i['des']], self.output_md)
            self.all_reg_tex_data += lm.tex_create_body_line([i['name'], i['addr'], \
                    i['reset'], i['des']], self.gitbookpath)

    def get_gitlog(self):
        gitlog = ''
        gitlog += '# 最近修改:\n\n'
        gitlog += '|日期|作者|描述|commit_id|\n'
        gitlog += '|:---|:---|:---|:---|\n'
        json_dir = os.path.dirname(self.js_file)
        now_dir = os.getcwd()
        cmd = 'git log --pretty=format:"| %ad | %cn | %s | %h |" --date=short'
        os.chdir(json_dir)
        fd = os.popen(cmd)
        tmp = fd.readlines()
        if len(tmp) >= 1:
            for line in tmp:
                gitlog += line
        else:
            gitlog += '|暂无|暂无|暂无|暂无|\n'
        os.chdir(now_dir)
        with open(os.path.join(self.gitbookpath, 'gitlog.md'), 'w') as fc:
            fc.write(gitlog)
        return gitlog


    def main(self):
        file_msg = os.path.basename(self.js_file).split(".json")[0]
        pp = preprocess.PreProcess()
        self.js_dict = pp.start(self.js_file)
        self.js_dpath = self.get_dpath(self.js_dict)
        lm = libmd.LibMarkdown()
        self.all_reg_data = lm.md_create_title_line(['名称', '地址', '初值', '描述'])
        self.all_reg_tex_data = lm.md_create_title_line(['名称', '地址', '初值', '描述'])
        if self.output_gitbook:
            if self.dir_type == "alone":
                self.gitbookpath = os.path.join("_json_output/gitbook/", file_msg)
                if not os.path.exists(self.gitbookpath):
                    os.system("mkdir -p " + self.gitbookpath)
                readme = os.path.join(self.gitbookpath, 'README.md')
                summary = os.path.join(self.gitbookpath, 'SUMMARY.md')
                if not os.path.exists(readme):
                    with open(readme, 'w') as fd:
                        fd.write("   ")
                with open(summary, 'w') as fd:
                    fd.write('# Summary \n\n')
                    fd.write('* [寄存器列表](all_register.md)\n')
                    for i in self.js_dpath:
                        self.path_addr_dict[i] = self.get_addr(i)
                    self.max_len = len(self.path_addr_dict[self.js_dpath[-1]][2:])
                    for i in range(int(len(self.js_dpath))):
                        name = self.get_delem(self.js_dict, self.js_dpath[i], key = 'RegName' )
                        name = name.upper()
                        if name != "RESERVED":
                            dpath = self.js_dpath[i]
                            fd.write('  * [' + name + ']('+ name + '.md)\n')
                            bit_num = self.get_delem(self.js_dict, dpath.split('registers')[0], \
                                    key = 'd_width')
                            self.create_md3(self.js_dpath[i], lm, bit_num)
                    self.relist(self.all_reg_list)
                    self.create_all_reg_data(lm)
                    with open(os.path.join(self.gitbookpath, 'all_register.md'), 'w') as fc:
                        fc.write("## 寄存器列表\n\n" + self.all_reg_data)
                print("\n\tcreate " + self.gitbookpath +" success") 
            elif self.dir_type == "link":
                self.gitbookpath = os.path.join(self.link_path, file_msg)
                if self.save_dir:
                    path_msg = os.path.join("_json_output/", self.dirname, str(file_msg))
                else:
                    path_msg = "_json_output/" + str(file_msg)
                if not os.path.exists(self.gitbookpath):
                    os.system("mkdir -p " + self.gitbookpath)
                readme = os.path.join(self.gitbookpath, 'README.md')
                summary = os.path.join(self.gitbookpath, 'SUMMARY.md')
                if not os.path.exists(readme):
                    with open(readme, 'w') as fd:
                        fd.write("   ")
                with open(summary, 'w') as fd:
                    fd.write('# Summary \n\n')
                    reg_list_path = os.path.join(path_msg, "all_register.md") 
                    reg_detail_path = os.path.join(path_msg, "detail.md") 
                    fd.write('* [寄存器列表](' + reg_list_path + ')\n')
                    fd.write('* [寄存器详细说明](' + reg_detail_path + ')\n')
                    for i in self.js_dpath:
                        name = self.get_delem(self.js_dict, i, key = 'RegName' )
                        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        #print(name)
                        addr = self.get_addr(i)
                        self.path_addr_dict[i] = addr
                        name = self.get_delem(self.js_dict, i, key = 'RegName' )
                        #print(name, "(" + addr + ")")
                        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    self.max_len = len(self.path_addr_dict[self.js_dpath[-1]][2:])
                    for i in range(int(len(self.js_dpath))):
                        name = self.get_delem(self.js_dict, self.js_dpath[i], key = 'RegName' )
                        name = name.upper()
                        if name != "RESERVED":
                            dpath = self.js_dpath[i]
                            #md_path = os.path.join(path_msg, name + ".md")
                            #fd.write('  * [' + name + ']('+ md_path + ')\n')
                            bit_num = self.get_delem(self.js_dict, dpath.split('registers')[0], \
                                    key = 'd_width')
                            self.create_md3(self.js_dpath[i], lm, bit_num)
                    self.relist(self.all_reg_list)
                    self.create_all_reg_data(lm)
                    gitlog = ''
                    try:
                        gitlog = self.get_gitlog()
                    except:
                        pass
                    with open(os.path.join(self.gitbookpath, 'all_register.md'), 'w') as fc:
                        fc.write("## 寄存器列表\n\n" + self.all_reg_data)
                    with open(os.path.join(self.gitbookpath, 'all_register_tex.md'), 'w') as fc:
                        fc.write("## 寄存器列表\n\n" + self.all_reg_tex_data)
                    with open(os.path.join(self.gitbookpath, 'detail.md'), 'w') as fc:
                        fc.write(self.reg_data)
                    #with open(os.path.join(self.gitbookpath, 'detail.rst'), 'w') as fc:
                    #    fc.write(self.reg_rst)
                self.check_file('README.md')
                self.check_file('SUMMARY.md')
                print("\n\tcreate " + self.gitbookpath +" success") 
        if self.output_md:
            #self.markdownpath = "./_json_output/" + file_msg
            self.markdownpath = os.path.join("./_json_output/markdwon/", file_msg)
            if not os.path.exists(self.markdownpath):
                os.system("mkdir -p " + self.markdownpath)
            md_file = os.path.join(self.markdownpath, file_msg + ".md")
            for i in self.js_dpath:
                self.path_addr_dict[i] = self.get_addr(i)
            self.max_len = len(self.path_addr_dict[self.js_dpath[-1]][2:])
            for i in self.js_dpath:
                bit_num = self.get_delem(self.js_dict, i.split('registers')[0], \
                        key = 'd_width')
                self.create_md3(i, lm, bit_num)
            self.relist(self.all_reg_list)
            self.create_all_reg_data(lm)
            self.data = "# 寄存器列表\n" + self.all_reg_data + "\n"\
                    + "# 寄存器详细说明\n" + self.data
            self.data = self.data.replace("\n#", "\n##")
            if self.output_xmind:
                md_file = file_msg + '.md'
                with open(md_file, 'w') as fd:
                    fd.write(self.xmind_md)
                    print("\n\tcreate " + md_file + " success") 
                    return
            with open(md_file, 'w') as fd:
                fd.write(self.data)
            print("\n\tcreate " + md_file + " success") 


def usage():
    """
    Usage:
        jsontomd -f json_file (-g) (-l remote_dir)
      exp
        jsontomd -f npu_register.json -g -l target_dir

    parameters:
        -f : 指定json文件
        -l : 指定生成目录, 把生成的gitbook目录,放到指定目录下
        -d : 加-d ,在生成目录中保留-f所指路径层级, 不加-d 只以json文件名创建目录
        -g : 加-g ,生成gitbook目录, 不加-g 生成单个markdown文件(加-l 默认加上了-g)
    """
    print(usage.__doc__)

def main():
    if len(sys.argv) <= 1:
            usage()
            sys.exit()
    opts,args = getopt(sys.argv[1:],"f:l:gxhdv")
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
        if k == "-d":
            save_dir = 1
        if k == "-l":
            link_path = v
            dir_type = "link"
            output_gitbook = 1
            output_md = 0
        if k == "-g":
            output_gitbook = 1
            output_md = 0
        if k == "-x":
            output_xmind = 1
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
