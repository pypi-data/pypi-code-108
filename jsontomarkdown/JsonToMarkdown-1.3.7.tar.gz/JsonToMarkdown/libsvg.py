# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET

class LibSVG(object):
    def __init__(self):
        self.cell = 20
        self.bit_num = 32
        self.bit_width = {
                '32':20,
                '8':40,
                }

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

    def create_blank_form(self, bit_num = 32):
        self.bit_num = int(bit_num)
        self.cell = int(self.bit_width[str(bit_num)])
        table = ET.Element('svg', attrib = {
            "baseProfile":"full",
            "width":"800",
            "height":"250",
            "version":"1.1",
            "viewBox":"0 0 700 250",
            "xmlns":"http://www.w3.org/2000/svg",
            "xmlns:ev":"http://www.w3.org/2001/xml-events",
            "xmlns:xlink":"http://www.w3.org/1999/xlink",
            })
        defs = ET.SubElement(table,'defs')
        all_group = ET.SubElement(table,'g', attrib = {"transform":"translate(4.5,150)"})
        # 名称组, 分区名
        name_group = ET.SubElement(all_group, 'g', attrib = {
            "transform":"rotate(-45 0,0)",
            })

        # 线条组, 表格框
        line_group = ET.SubElement(all_group, 'g', attrib = {
            "stroke":"black",
            "stroke-linecap":"round",
            "stroke-width":"1",
            "transform":"translate(0,20.0)",
            })
        flen = str(self.bit_num * self.cell)
        ET.SubElement(line_group, 'line', attrib = {"x1":"0", "y1":"0", "x2":flen, "y2":"0"})
        ET.SubElement(line_group, 'line', attrib = {"x1":"0", "y1":"0", "x2":"0", "y2":"40"})
        ET.SubElement(line_group, 'line', attrib = {"x1":"0", "y1":"40", "x2":flen, "y2":"40"})
        ET.SubElement(line_group, 'line', attrib = {"x1":flen, "y1":"0", "x2":flen, "y2":"40"})
        for i in range(self.bit_num):
            x_p = str(i*self.cell)
            ET.SubElement(line_group, 'line', attrib = {"x1":x_p, "y1":"0", "x2":x_p, "y2":"5"})
            ET.SubElement(line_group, 'line', attrib = {"x1":x_p, "y1":"35", "x2":x_p, "y2":"40"})

        # 值组, 分区坐标,分区初始值
        value_group = ET.SubElement(all_group, 'g', attrib = {
            "text-anchor":"middle",
            })
        index_group = ET.SubElement(value_group, 'g', attrib = {"transform":"translate(20.0,16.0)"})
        reset_group = ET.SubElement(value_group, 'g', attrib = {"transform":"translate(20.0,46.0)"})
        color_group = ET.SubElement(value_group, 'g', attrib = {"transform":"translate(0,20.0)"})

        # 刻度组
        ruler_group = ET.SubElement(all_group, 'g', attrib = {
            "stroke":"black",
            "stroke-linecap":"round",
            "stroke-width":"1",
            "transform":"translate(0,60.0)",
            })
        ET.SubElement(ruler_group, 'line', attrib = {"x1":"0", "y1":"5", "x2":flen, "y2":"5"})
        for i in range(int(self.bit_num /4) + 1):
            x_p = str(i*self.cell*4)
            ET.SubElement(ruler_group, 'line', attrib = {"x1":x_p, "y1":"0", "x2":x_p, "y2":"10"})
            if i == 0:
                x_p = str(self.cell/2)
                index_elem = ET.SubElement(ruler_group, 'text', attrib = {
                    "text-anchor":"middle",
                    "transform":"translate(0,17.0)",
                    "font-family":"source code pro",
                    "font-size":"12",
                    "font-weight":"normal",
                    "x":x_p,
                    })
                index_elem.text = str(self.bit_num - 1)
            else:
                x_p = str(i*self.cell*4 - int(self.cell/2))
                index_elem = ET.SubElement(ruler_group, 'text', attrib = {
                    "text-anchor":"middle",
                    "transform":"translate(0,17.0)",
                    "font-family":"source code pro",
                    "font-size":"12",
                    "font-weight":"normal",
                    "x":x_p,
                    })
                index_elem.text = str(self.bit_num - i*4)
        return table

    def add_line(self, table, index_range):
        scope = index_range.strip("[]").split(":")
        end = int(scope[0]) + 1
        start = int(scope[-1])
        for index in range(start, end):
            re_index = self.bit_num - 1 - index
            if index == start:
                self._add_long_string(table, re_index + 1)
            if index == end - 1:
                self._add_long_string(table, re_index)

    def add_reset_value(self, table, index_range, value, name):
        scope = index_range.strip("[]").split(":")
        end = int(scope[0]) + 1
        start = int(scope[-1])
        if name == "reserved":
            self._add_color(table, start, end)
        else:
            self._add_index(table, start, end)
        self._add_value(table, start, end, value)

    def add_name(self, table, index_range, name):
        scope = index_range.strip("[]").split(":")
        end = int(scope[0]) + 1
        start = int(scope[-1])
        middle = int((end + start)/2)
        x_p = str(((self.bit_num - 1 - middle)*self.cell + (int(self.cell/2)))/1.414)
        value_elem = ET.SubElement(table[1][0], 'text', attrib = {
                "font-family":"source code pro",
                "font-size":"12",
                "font-weight":"normal",
                "x":x_p,
                "y":x_p,
                })
        if name != "reserved":
            value_elem.text = name.upper()
        else:
            value_elem.attrib['font-size'] = "12"
            value_elem.text = "(" + name + ")"

    def _add_color(self, table, start, end):
        x_p = str((self.bit_num - 1 - end + 1)*self.cell)
        width = str((end - start)*self.cell)
        index_elem = ET.SubElement(table[1][2][2], 'rect', attrib = {
            "fill":"black",
            "fill-opacity":"0.1",
            "height":"40",
            "width":width,
            "x":x_p,
            "y":"0",
            })

    def _add_value(self, table, start, end, value):
        if int(value, 16) == 0:
            for i in range(start, end):
                x_p = str((self.bit_num - 1 - i)*self.cell - 20 + int(self.cell/2))
                index_elem = ET.SubElement(table[1][2][1], 'text', attrib = {
                    "font-family":"source code pro",
                    "font-size":"16",
                    "font-weight":"normal",
                    "x":x_p,
                    })
                index_elem.text = str(0)
        else:
            fill_list = list(bin(int(value, 16))[2:])
            for i in range(start, end):
                x_p = str((self.bit_num - 1 - i)*self.cell - 20 + int(self.cell/2))
                index_elem = ET.SubElement(table[1][2][1], 'text', attrib = {
                    "font-family":"source code pro",
                    "font-size":"16",
                    "font-weight":"normal",
                    "x":x_p,
                    })
                if fill_list != []:
                    index_elem.text = str(fill_list.pop(-1))
                else:
                    index_elem.text = str(0)

    def _add_index(self, table, start, end):
        if end == start + 1:
            x_p = str((self.bit_num - 1 - start)*self.cell - 20 + int(self.cell/2))
            index_elem = ET.SubElement(table[1][2][0], 'text', attrib = {
                "font-family":"source code pro",
                "font-size":"12",
                "font-weight":"normal",
                "x":x_p,
                })
            index_elem.text = str(start)
        else:
            start_p = str((self.bit_num - 1 - start)*self.cell - 20 + int(self.cell/2))
            index_elem = ET.SubElement(table[1][2][0], 'text', attrib = {
                "font-family":"source code pro",
                "font-size":"12",
                "font-weight":"normal",
                "x":start_p,
                })
            index_elem.text = str(start)
            end_p = str((self.bit_num - 1 - end)*self.cell + self.cell + (int(self.cell/2) - 20))
            index_elem = ET.SubElement(table[1][2][0], 'text', attrib = {
                "font-family":"source code pro",
                "font-size":"12",
                "font-weight":"normal",
                "x":end_p,
                })
            index_elem.text = str(end - 1)

    def _add_long_string(self, table, index):
        x_p = str(index * self.cell)
        ET.SubElement(table[1][1], 'line', attrib = {"x1":x_p, "y1":"0", "x2":x_p, "y2":"40"})

    def _add_short_string(self, table, index):
        # not used
        x_p = str(index * 20)
        ET.SubElement(table[1][1], 'line', attrib = {"x1":x_p, "y1":"0", "x2":x_p, "y2":"5"})
        ET.SubElement(table[1][1], 'line', attrib = {"x1":x_p, "y1":"35", "x2":x_p, "y2":"40"})

    def svg_transform(self, table):
        return str(ET.tostring(table), 'utf-8') + "\n"

if __name__ == "__main__":
    ls = LibSVG()
    table = ls.create_blank_form(8)
    ls.add_line(table, '[6:0]')
    ls.indent(table)

    svg_data = ls.svg_transform(table)
    svg_name = 'demo.svg'
    with open('demo.svg', 'w') as fd:
        fd.write(svg_data)
