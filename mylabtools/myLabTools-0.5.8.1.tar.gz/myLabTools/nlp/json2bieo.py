#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       : 命名实体识别 任务中数据格式的转换
@Date               :2021/02/07 12:00:08
@Author             :mayq
@version            :1.0
'''
from typing import  Dict,Optional,List
class Json2BIEO:
    def __init__(
        self,
        ch_label2en_char = None
        ) -> None:
        
        self.ch_label2en_char = ch_label2en_char
    
    @staticmethod
    def get_single_entity_BIEO_labels(
        entity_text_len:int,
        label_en_char:str
        ) -> List[str]:
        """
        @description  :将单个实体转换为 BIEO label list
        @param  :
        @Returns  :
        """
        temp_label = []
        if entity_text_len == 1:
            temp_label = ["B-"+label_en_char]
            return temp_label

        elif entity_text_len == 2:
            temp_label = ["B-"+label_en_char,"E-"+label_en_char]
            return temp_label

        elif entity_text_len == 3:
            temp_label = ["B-"+label_en_char,"I-"+label_en_char,"E-"+label_en_char]
            return temp_label

        elif entity_text_len >= 4:
            temp_label = ["I-"+label_en_char]*entity_text_len
            temp_label[0] = "B-"+label_en_char
            temp_label[-1] ="E-"+label_en_char
            return temp_label

        else:
            return temp_label
    def data_trans(
        self,
        text : str,
        entity_info, # [[实体开始位置，实体结束位置，实体类型]]
        entity_filter = lambda entity_text,label : True, # 该函数传参：实体文本，实体类型： [str,str]
        entity_labels_post_filter = lambda char_list, label_list : list(zip(char_list,label_list)), # 该函数传参： 实体字符列表，实体标签列表:[List[str],List[str]]
        print_log = True
        ):
        """
        @description  : 使用BIEO 模式对命名实体识别的标注数据进行格式转换
        @param  :
        @Returns  :
        """
        
        labels = ["O"] * len(text)

        for row in entity_info:
            start_i,end_i ,label  = row[:3]
            entity_text = text[start_i:end_i]
            entity_text_len = len(entity_text)
            if entity_filter(entity_text,label):
                label_en_char = self.ch_label2en_char[label]
                temp_labels_list = Json2BIEO.get_single_entity_BIEO_labels(entity_text_len,label_en_char)
                labels[start_i:end_i] = temp_labels_list
        filtered_data = entity_labels_post_filter(list(text),labels)
        if print_log:
            for char,label in filtered_data:
                print("%s\t%s" % (char,label))
            print("\n")
        return filtered_data 

class BIEO2Entity:
    @staticmethod
    def bieo2entity_list(label_list:List[str]) -> List[str]:
        # https://blog.csdn.net/hqh131360239/article/details/107764716

        return [""]


    