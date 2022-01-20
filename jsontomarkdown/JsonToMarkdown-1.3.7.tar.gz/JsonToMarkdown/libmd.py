# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import os

class LibMarkdown(object):
    def __init__(self):
        pass

    def indent(self, elem, level=0):
        '''
        添加xml文件的换行符,增强可读性
        '''
        i = "\n" + level*"\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def create_blank_form(self):
        table = ET.Element('table')
        title = ET.SubElement(table, 'thead')
        title_tr = ET.SubElement(title, 'tr')
        data = ET.SubElement(table, 'tbody')
        data_tr = ET.SubElement(data, 'tr')
        for i in range(32):
            title_th = ET.SubElement(title_tr, 'td', attrib = {"align":"center"})
            title_th.text = "B" + str(31-i )
            data_th = ET.SubElement(data_tr, 'td', attrib = {"align":"center"})
            data_th.text = "reserve"
            if (i+1) % 8 == 0 and i != 31:
                title = ET.SubElement(table, 'thead')
                title_tr = ET.SubElement(title, 'tr')
                data = ET.SubElement(table, 'tbody')
                data_tr = ET.SubElement(data, 'tr')
        return table

    def fill_form(self, table, name, index_range):
        scope = index_range.strip("[]").split(":")
        end = int(scope[0]) + 1
        start = int(scope[-1])
        for index in range(start, end):
            if index < 0 or index > 31:
                print("index out of range")
            x = (3 - index//8) *2 + 1
            y = 7 - index%8
            table[x][0][y].text = name
        return table

    def merge_form(self, table):
        data_map = self._get_data_map_by_table(table)
        new_table = self._create_form_by_data_map(data_map)
        return new_table

    def _get_data_map_by_table(self, table):
        '''
        data_map format:
        [{'[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]': 'idle_cycle'}, \
                {'[16, 17, 18]': 'reserve'}, {'[19]': 'clock_gating_enable'},\
                {'[20, 21, 22, 23, 24, 25, 26]': 'reserve'}, {'[27]': 'idle_type'}, \
                {'[28, 29, 30]': 'reserve'}, {'[31]': 'en'}]
        '''
        data_map = []
        data_hash = {}
        data_range = []
        pre_data = ''
        for x, line in enumerate(table):
            if line.tag == "tbody":
                for y, data in enumerate(line[0]): 
                    now = int(((x-1)/2)*8 + y)
                    if data.text != pre_data:
                        if now - 1 >= 0 :
                            data_hash = {str(data_range):pre_data}
                            data_map.append(data_hash)
                            data_range = []
                        data_range.append(now)
                        pre_data = data.text
                    else:
                        data_range.append(now)
        data_hash = {str(data_range):pre_data}
        data_map.append(data_hash)
        #print(data_map)
        return data_map
    
    def _create_form_by_data_map(self, data_map):
        n = 0
        #table = ET.Element('table', attrib = {"width":"200px", "style":\
        #        {"word-break": "break-all", "word-wrap":"break-word"}})
        table = ET.Element('table', attrib = {"style":"TABLE-LAYOUT: fixed", "border":"1",\
                "cellspacing":"0", "cellpadding":"0", "width":"1250"})
        title = ET.SubElement(table, 'thead')
        title_tr = ET.SubElement(title, 'tr')
        data = ET.SubElement(table, 'tbody')
        data_tr = ET.SubElement(data, 'tr')
        data_th = ET.SubElement(data_tr, 'th', attrib = {"align":"center"})
        pre_col = 0
        is_return = 0
        for i in range(32):
            quotient = (i) // 8#商
            remainder = (i + 1) % 8#余数
            title_th = ET.SubElement(title_tr, 'th', attrib = {"align":"center"})
            title_th.text = "B" + str(31-i )
            if i in eval(list(data_map[n].keys())[0]):
                data_th.text = list(data_map[n].values())[0]
                colspan = i+1 - quotient*8
                data_th.set("colspan", str(colspan - pre_col))
                is_return = 0
            else:
                pre_col += colspan
                colspan = 0
                n += 1
                if is_return == 1:
                    pass
                elif is_return == 0:
                    data_th = ET.SubElement(data_tr, 'th', attrib = {"align":"center"})
                data_th.text = list(data_map[n].values())[0]
                if len(eval(list(data_map[n].keys())[0])) == 1:
                    pre_col += 1
                is_return = 0
            if remainder == 0 and i != 31:
                is_return = 1
                pre_col = 0
                colspan = 0
                title = ET.SubElement(table, 'thead')
                title_tr = ET.SubElement(title, 'tr')
                data = ET.SubElement(table, 'tbody')
                data_tr = ET.SubElement(data, 'tr')
                data_th = ET.SubElement(data_tr, 'th', attrib = {"align":"center"})
        return table

    def create_title_line(self, argv):
        table = ET.Element('table', attrib = {"border":"1"})
        title = ET.SubElement(table, 'thead')
        title_tr = ET.SubElement(title, 'tr')
        for i in argv:
            title_th = ET.SubElement(title_tr, 'th', attrib = {"align":"center"})
            title_th.text = str(i)
        return table

    def create_body_line(self, table, argv):
        data = ET.SubElement(table, 'tbody')
        data_tr = ET.SubElement(data, 'tr')
        for i in argv:
            data_th = ET.SubElement(data_tr, 'th', attrib = {"align":"left"})
            data_th.text = str(i)
        return table

    def md_create_title_line(self, argv):
        data = "|"
        end = "|"
        for i in argv:
            data += i + "|"
            end += ":---|"
        data = data + "\n" + end + "\n"
        return data

    def md_create_body_line(self, argv, is_md):
        if is_md:
            data = "|[" + argv[0].replace("||","_") + "](#" + argv[0].split("||")[0] +")|"
        else:
            #data = "|[" + argv[0].replace("||","_") + "](./" + \
            #        argv[0].split("||")[0]+".md)|"
            data = "|[" + argv[0].replace("||","_") + "](detail.md#" + \
                    argv[0].split("||")[0] +")|"


        for i in argv[1:]:
            if len(i) != 0:
                data += str(i) + "|"
            else:
                data += "&nbsp;" + "|"
        data = data + "\n"
        return data

    def md_create_body_line2(self, argv):
        data = '|'
        for i in argv:
            if len(i) != 0:
                msg = i.replace('；',';')
                #msg = msg.replace('。',';')
                msg = '<br>'.join(msg.strip(';').split(';'))
                data += str(msg) + "|"
            else:
                data += "&nbsp;" + "|"
        data = data + "\n"
        return data

    def tex_create_body_line(self, argv, path):
        link = os.path.join(path, argv[0].split("||")[0] + '.md')
        data = "|[" + argv[0].replace("||","_") + "](" + link + ")|"
        for i in argv[1:]:
            data += str(i) + "|"
        data = data + "\n"
        return data
    
    def md_register_name(self, name):
        data = "### " + name + "\n"
        return data

    def md_register_des(self, des):
        data = "&emsp;" + des + "\n"
        return data

    def md_register_addr(self, addr):
        data = "#### Address: " + addr + "\n"
        return data

    def md_transform(self, table):
        return str(ET.tostring(table), 'utf-8') + "\n" + "&nbsp;" + "\n"

if __name__ == "__main__":
    pass
    #lm = LibMarkdown()
    ##table = lm.create_blank_form2()
    #table = lm.create_blank_form()
    ##table = lm.fill_form(table, "clock_gating_enable", "[12]")
    ##table = lm.fill_form(table, "idle_type", "[4]")
    ##table = lm.fill_form(table, "en", "[0]")
    ##table = lm.fill_form(table, "idle_cycle", "[16:31]")
    #lm.fill_form(table, 'all_idle_int_en', '[31]')
    #lm.fill_form(table, 'mcu_cmd_int_en', '[16]')
    #lm.fill_form(table, 'op_cal_overflow_int_en', '[14]')
    #lm.fill_form(table, 'mac_cal_overflow_int_en', '[13]')
    #lm.fill_form(table, 'cmd_err_int_en', '[12]')
    #lm.fill_form(table, 'overtime_int_en', '[8]')
    #lm.fill_form(table, 'over_int_en', '[0]')
    #table = lm.merge_form(table)

    #print(table)
    #lm.indent(table)
    #w = ET.ElementTree(table)
    #w.write("ccc.md",'utf-8', True)
