#!/usr/bin/env python3

import codecs
import json
from Juwel import GUI_element_finder
from pathlib import Path

def read_template():

                home = str(Path.home())
                file_name=f'{home}/.juwel/config_template.txt'
                my_encoding='utf-8'
                fh=codecs.open(file_name,'r',encoding=my_encoding)
                f_str=fh.read().encode(my_encoding)
                fh.close()
                f_str = f_str.decode('utf-8')



                lines = f_str.split('\n')

                

                counter = 0
                line_dict = {}
                inter_list = []

                for element in lines:
                    if element != '':
                        inter_list.append(element)
                    elif element == '':
                        line_dict[counter] = inter_list
                        inter_list = []
                        counter = counter + 1


                positioning_list = []
                layout_bool = False
                for line in lines:
                                line = line.strip()
                                if line == 'layout':
                                                layout_bool = True
                                if layout_bool == True:
                                                if len(line) > 0 and line[0].isdigit():
                                                                if len(line) > 1:
                                                                                line = line.split()
                                                                positioning_list.append(line)


                newline_dict = {}
                for element in positioning_list:
                                if isinstance(element, str):
                                                newline_dict[element] = "yes"
                                elif isinstance(element, list):                
                                                for i in range(len(element)):
                                                                if i == 0:
                                                                                newline_dict[element[i]] = "yes"
                                                                elif i != 0:
                                                                                newline_dict[element[i]] = "no"

                                                
                wrong_gui_dict = {}
                wrong_name_dict = {}
                wrong_default_dict = {}
                wrong_items_dict = {}


                gui_dict = {}
                name_dict = {}
                default_dict = {}
                items_dict = {}



                for key in line_dict:
                        for element in line_dict[key]:
                            element = element.strip()
                            if element[0].isdigit():
                                position_number = (element.split())[0]
                                gui_element = (element.split())[1]
                                wrong_gui_dict[position_number] = gui_element
                            elif ":" in element:
                                pair = element.split(":")
                                if pair[0].strip() == "label" or pair[0].strip() == "key" or pair[0].strip() == "name":
                                    wrong_name_dict[position_number] = pair[1].strip() + ": "
                                elif pair[0].strip() == "start" or pair[0].strip() == "default":
                                    wrong_default_dict[position_number] = pair[1].strip()
                                elif pair[0].strip() == "items" or pair[0].strip() == "values" or pair[0].strip() =="options":
                                    item_list = []
                                    item_list = pair[1].split(",")
                                    for item in item_list:
                                        item_list[item_list.index(item)] = item.strip()
                                        wrong_items_dict[position_number] = item_list
                            elif element == "layout":
                                break
                                                

                                                
                for key in newline_dict:
                                if key in wrong_gui_dict:
                                                gui_dict[key] = wrong_gui_dict[key]
                                if key in wrong_name_dict:
                                                name_dict[key] = wrong_name_dict[key]
                                if key in wrong_default_dict:
                                                default_dict[key] = wrong_default_dict[key]
                                if key in wrong_items_dict:
                                                items_dict[key] = wrong_items_dict[key]



                final_dict = {}
                for key in gui_dict:
                                inter_dict = {}
                                inter_dict["GUI_type"] = gui_dict[key]
                                if key in name_dict:
                                                inter_dict["key"] = name_dict[key]
                                if key in items_dict:
                                                inter_dict["values"] = items_dict[key]
                                if key in default_dict:
                                                inter_dict["default"] = default_dict[key]
                                if key in newline_dict:
                                                inter_dict["newline"] = newline_dict[key]
                                final_dict[key] = inter_dict



                for key in final_dict:
                                corrected_gui_type = GUI_element_finder.find_gui_element(final_dict[key]["GUI_type"])
                                final_dict[key]["GUI_type"] = corrected_gui_type
                                                

                

                final_list = []
                for key in final_dict:
                                final_list.append(final_dict[key])

                for element in final_list:
                                if "default" not in element or element["default"] == "":
                                                if element["GUI_type"] == "selectbox" or element["GUI_type"] == "expiration":
                                                                element["default"] = element["values"][0]
                                                elif element["GUI_type"] == "textfield":
                                                                element["default"] = "Max Mustermann"                
                                if element["GUI_type"] == "calendar" or element["GUI_type"] == "expiration":
                                                if "format" not in element or element["format"] == "":
                                                                element["format"] = "deutsch"

                #json_object = json.dumps(final_list, indent = 4)
                #print(json_object)

                return final_list

