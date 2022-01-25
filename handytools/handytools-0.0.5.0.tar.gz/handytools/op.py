#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
from line_profiler import LineProfiler
import cv2
from turtle import width
from numpy import asarray
import math
import traceback
from difflib import SequenceMatcher
import ast
import os
import re
from numpy import random
from tqdm.std import tqdm
from urllib.parse import quote, unquote
from datetime import datetime
from tqdm.std import tqdm
import os
import pickle
import traceback
import shutil
import glob
import jsonlines
import json
import zipfile
import csv
from typing import Dict
import pickle
import os
import pdfplumber
from datetime import datetime
import shutil
import glob
import os
from tqdm import tqdm
import json
import csv
import os
import shutil
import pandas as pd
import traceback
from numpy import random
import fitz
from PIL import Image
import numpy as np


class File(object):
    def __init__(self, *args):
        super(File, self).__init__(*args)

    def readlines(self, path, portion=1, end: int = None, show_bar=True, encoding="utf-8"):
        """read file and return a list of lines
        Args:
            path (string): file path
            portion (int, optional): specify the ratio of lines to be read. Defaults to 1.
            end (int, optional): specify which line to stop read. Defaults to None.
            show_bar (bool, optional): display the read progress or not. Defaults to True.
            encoding (str,optional): encoding format.Defaults to "utf-8".
        Returns:
            list: each elements is a row
        Examples:
            >>> lines = File.readlines("test.txt")
            >>> print(lines)
            ['line1', 'line2', 'line3']
        """
        data = []
        desc = path.split(os.sep)[-1] + " is loading..."
        with open(path, "r+", encoding=encoding) as f:
            num = end if end is not None and not show_bar else len(
                [1 for _ in open(path, "r", encoding=encoding)])*portion
            w = f if not show_bar else tqdm(
                f, total=num, desc=u'%s 0 text' % desc)
            for i, _ in enumerate(w):
                if i >= num:
                    break
                data.append(_.replace("\n", ""))
                if show_bar:
                    w.set_description(u'%s %s text' % (desc, str(i+1)))
        return data

    def glob_read(self, path, read_fun, stop_i=None,  show_bar=False):
        """read all files in path by glob

        Args:
            path (str): absolute path
            read_fun ([type]): different read function based on file type
            stop_i (int, optional): stop read at file i. Defaults to None.
            show_bar (bool, optional): display read process or not . Defaults to False.

        Returns:
            text_list (list): a list of lines in all files
            pathlist (list): a list of absolute file path

        Examples:
            >>> text_list, pathlist = glob_read("/home/directory/test", read_fun=read_txt)
            >>> print(text_list)
            ['line1', 'line2', 'line3']
        """
        text_list = []
        pathlist = glob.glob(path)
        if show_bar:
            w = tqdm(pathlist, desc=u'已加载0个text')
        else:
            w = pathlist
        for i, txt in enumerate(w):
            if stop_i is not None and i > stop_i:
                break
            text_list.extend(read_fun(txt, show_bar=False))
            if show_bar:
                w.set_description(u'已加载%s个text' % str(i+1))
        return text_list, pathlist

    def rjsonl(self, path, show_bar=False):
        """read jsonlines file

        Args:
            path (str): file path
            show_bar (bool, optional): display read process or not . Defaults to False.

        Returns:
            each time yield a json object

        Examples:
            >>> for item in File.rjsonl("test.jsonl"):
            >>>     print(item)
            {'a': 1}
            {'b': 2}
            {'c': 3}
        """
        with open(path, "r+", encoding="utf8") as f:
            lines = [1 for _ in open(path, "r", encoding="utf-8")]
            w = lines if not show_bar else tqdm(
                lines, total=len(lines), desc=u'已加载0个text')
            reader = jsonlines.Reader(f)
            for i, _ in enumerate(w):
                try:
                    item = reader.read()
                    yield item
                except Exception:
                    traceback.print_exc()
                if show_bar:
                    w.set_description(u'已加载%s个text' % str(i+1))
        f.close()

    def wjsonl(self, data, path):
        """write jsonlines file

        Args:
            data (list): a list of json object
            path (str): file path

        Returns:
            None

        Examples:
            >>> File.wjsonl([{'a': 1}, {'b': 2}, {'c': 3}], "test.jsonl")
        """
        with jsonlines.open(path, 'w') as writer:
            writer.write_all(data)

    def wjsons(self, jsons, path, mode="w"):
        """save json object to a file

        Args:
            jsons (list): a list of json object
            path (str): file path
            mode (str, optional): file mode. Defaults to "w".

        Returns:
            None

        Examples:
            >>> File.savejsons([{'a': 1}, {'b': 2}, {'c': 3}], "test.json")
        """
        with open(path, mode) as outfile:
            for entry in jsons:
                json.dump(entry, outfile)
                outfile.write('\n')

    def mkdir(self, dir_path):
        """make directory if dir_path not exist

        Args:
            dir_path (string): directory absolute path

        Returns:
            state: if successfully created directory return True,
                    nontheless return False
        Examples:
            >>> File.mkdir("/home/directory/test")
            True
        """
        state = True
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        except Exception:
            state = False
        return state

    def save2pkl(self, obj: dict, path: str):
        """save object to pickle file

        Args:
            obj (dict): object to be saved
            path (str): file path
        Returns:
            state: if successfully created directory return True,
                    nontheless return False
        Examples:
            >>> save2pkl({"a": 1}, "test.pkl")
            True
        """
        try:
            self.mkdir(os.path.dirname(path))
            f = open(path, "wb")
            pickle.dump(obj, f)
            f.close()
            return True
        except Exception:
            traceback.print_exc()
            return False

    def files_with_extension(self, path: str, extension: str):
        """get files by filename extension

        Args:
            path ([type]): [description]
            extension ([type]): [description]

        Returns:
            file_list: file name list
        """
        file_list = [
            file for file in sorted(os.listdir(path))
            if file.lower().endswith(extension)
        ]
        return file_list

    def read_csv(self, filepath: str):
        """read csv from a given filepath

        Args:
            filepath (str): absolute path to the csv file

        Returns:
            rows (list): each element is a row of the csv file
            column_titles (list): each element is a column title of the csv file

        Examples:
            >>> rows, column_titles = File.read_csv("test.csv")
            >>> print(rows)
            [['TOM',20],['JERRY',30],['JANE',25]]
            >>> print(column_titles)
            ['name', 'age']
        """
        # initializing the titles and rows list
        column_titles = []
        rows = []
        num_lines = len([1 for line in open(filepath, "r")])
        # reading csv file
        with open(filepath, 'r') as csvfile:
            # creating a csv reader object
            csvreader = csv.reader((line.replace('\0', '')
                                    for line in tqdm(csvfile,
                                                     desc=filepath.split(
                                                         os.sep)[-1]+" is filtering ",
                                                     total=num_lines)))
            # extracting field names through first row
            column_titles = next(csvreader)
            # extracting each data row one by one
            try:
                for row in tqdm(csvreader, desc=filepath.split(os.sep)[-1]
                                + " is loading..", total=num_lines):
                    rows.append(row)
            except Exception as e:
                traceback.print_exc()
        return rows, column_titles

    def delete(self, filepath: str):
        """delete file or folders if file exist

        Args:
            file_path (str): absolute path to the file
        """
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        elif os.path.isfile(filepath):
            os.remove(filepath)
        else:
            return False

    def zip(self, src_path: str, tgt_path: str):
        """zip files in a directory

        Args:
            zip_path (str): absolute path to the directory
            zip_name (str): zip file name
        """
        date = datetime.now()
        zip_name = src_path.split(os.sep)[-1] + str(date)+".zip"
        tgt_path = os.path.join(tgt_path, zip_name)
        self.delete(tgt_path)
        shutil.make_archive(tgt_path, 'zip', src_path)

    def copy(self, source_path: str, target_path: str):
        """copy files in a directory

        Args:
            source_path (str): absolute path to the directory
            target_path (str): absolute path to the directory

        Returns:
            state: if successfully copied return True,

        Examples:
            >>> File.copy("/home/directory/test", "/home/directory/test_copy")
            True
        """

        self.mkdir(target_path)
        if os.path.exists(source_path):
            # root :refer to current iteration directory
            # dirs :refer to all direct sub directories
            # files :refer to all files in current iteration directory
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    shutil.copy(src_file, target_path)
        return True

    def save_table2csv(self, data, path, sortby=None, ascending=False):
        """save a table to csv file 

        Args:
            data (dict): key is column name and value is list of values belong to the column
            path (str): save path
            sortby ([type], optional): [description]. Defaults to None.
            ascending (bool, optional): [description]. Defaults to False.

        Example:
            nme = ["aparna", "pankaj", "sudhir", "Geeku"]
            deg = ["MBA", "BCA", "M.Tech", "MBA"]
            scr = [90, 40, 80, 98]
            dict = {'name': nme, 'degree': deg, 'score': scr}
            save_table2csv(dict, os.path.join(sys.path[0], "dict.csv"))
        """
        df = pd.DataFrame(data)
        if sortby is not None:
            df.sort_values([sortby], axis=0, ascending=ascending, inplace=True)
        # saving the dataframe
        df.to_csv(path)

    def parent_dir(self, path: str, layers: int = 1):
        """get parent directory

        Args:
            path(str): file path
            layers(int, optional): layers of parent directory. Defaults to 1.

        Returns:
            path: parent directory
        """
        dirname = os.path.dirname
        for _ in range(layers):
            path = dirname(path)
        return path

    def newpth(self, path, subfolder="", filename: str = ""):
        """get new path

        Args:
            path(str): absolute path
            subfolder(str, optional): sub-folder inside this path . Defaults to "".
            filename(str, optional): filename inside sub-folder. Defaults to "".

        Returns:
            str: absolute path / path/subfolder/filename

        Examples:
            >>> newpth("/home/directory/test", "subfolder", "filename")
            /home/directory/test/subfolder/filename
        """
        return os.path.join(self.parent_dir(path, 1), subfolder, filename)

    def get_all_sub_folders(self, path):
        """get all sub folders by path

        Args:
            path(str): target path

        Returns:
            list: sub folder list

        Examples:
            >>> get_all_sub_folders("/home/directory/test")
            ['test1', 'test2']
        """
        sub_directory = []
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isdir(file_path):
                sub_directory.append(filename)
        return sub_directory

    def generate_cleanfolder(self, path: str):
        """clean/generate a directory by path recursively

        Args:
            path(str): target path

        Returns:
            state: if successfully created directory return True,

        Examples:
            >>> generate_cleanfolder("/home/directory/test")
            True
        """
        folder_paths = []
        if isinstance(path, list):
            folder_paths.extend(path)
        else:
            folder_paths.append(path)
        for floder in folder_paths:
            # print('make folder:',floder)
            if not os.path.isdir(floder):
                os.mkdir(floder)
        for folder in folder_paths:
            if not os.path.isdir(folder):
                print("this folder name doesn't exist...")
                break
            files = os.listdir(folder)
            for filename in files:
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        # print("shutil :",file_path)
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
                    return False
        return True

    def generate_emptyfolder_bylist(self, root_path, folders_list):
        """generate empty folder by list

        Args:
            root_path(str): absolute path
            folders_list(list): folder list

        Examples:
            >>> generate_emptyfolder_bylist("/home/directory/test", ["test1", "test2"])
        """
        floder_list = []
        for fol in folders_list:
            floder_list.append(os.path.join(root_path, fol))
        self.generate_cleanfolder(floder_list)

    def file_size(self, path):
        """give file absolute path, return file size

        Args:
            path(str): absolute path

        Returns:
            int: file size in bytes
            int: file size in kb
            int: file size in mb

        Examples:
            >>> file_size("/home/directory/test.txt")
            (9, 0.009, 0.0009)
        """
        size = os.path.getsize(path)
        return size, round(size / (1024**2),
                           2), round(size / (1024**2),
                                     2), round(size / (1024**3), 2)

    def savelist(self, obj, path):
        """save list to file

        Args:
            obj(list): a list to be saved
            path(str): file path

        Returns:
            state: if successfully created directory return True

        Examples:
            >>> savelist([1, 2, 3], "test.txt")
            True
        """
        try:
            self.mkdir(self.parent_dir(path, 1))
            with open(path, 'w') as f:
                for item in tqdm(obj, desc=path.split(os.sep)[-1] + " is saving..."):
                    f.write("%s\n" % item)
            return True
        except Exception as ex:
            traceback.print_exc()
            return False

    def append_list2file(self, path, obj, show_bar=False):
        """append list to file

        Args:
            path(str): absolute path
            obj(list): a list to be saved
            show_bar(bool, optional): [description]. Defaults to False.

        Returns:
            state: if successfully created directory return True

        Examples:
            >>> append_list2file("test.txt", [1, 2, 3])
            True
            >>> append_list2file("test.txt", [4, 5, 6], True)
            True
        """
        self.mkdir(os.path.dirname(path))
        try:
            with open(path, 'a+') as f:
                if show_bar:
                    for item in tqdm(obj, desc=path.split(os.sep)[-1] + " is saving..."):
                        f.write("%s\n" % item)
                else:
                    for item in obj:
                        f.write("%s\n" % item)
            return True
        except Exception as ex:
            traceback.print_exc()
            return False

    def rjson(path, encoding='utf-8'):
        """read json file

        Args:
            path(str): absolute path
            encoding(str, optional): [description]. Defaults to 'utf-8'.

        Returns:
            dict: json data

        Examples:
            >>> rjson("test.json")
            {'a': 1, 'b': 2}
        """
        f = open(path)
        data = json.load(f, encoding=encoding)
        return data

    def rpkl(self, dict_path):
        """read pickle file

        Args:
            dict_path(str): pickle file path

        Returns:
            dict_object(dict): pickle file object

        Examples:
            >>> rpkl("test.pkl")
            {'a': 1, 'b': 2}
        """
        with open(dict_path, "rb") as f:
            dict_object = pickle.load(f)
        return dict_object


class Dict(object):
    def __init__(self, *args):
        super(Dict, self).__init__(*args)

    def union_dict(self, dict1, dict2):
        """combine two dicts

        Args:
            dict1(dict): only allow dict which value is int
            dict2(dict): only allow dict which value is int

        Returns:
            dict2: combined dict
        Examples:
            >>> d = Dict()
            >>> d.union_dict({"a": 1}, {"b": 2})
            {'a': 1, 'b': 2}
        """
        for key in dict1.keys():
            if dict2.get(key) != None:
                dict2[key] += dict1[key]
            else:
                dict2[key] = dict1[key]
        return dict2

    def split_dict(self, dictionary: dict, split_nums: int):
        """split dict into several parts

        Args:
            dictionary(dict): a dict to be split
            split_nums(int): split nums

        Returns:
            list: each element is a dict

        Examples:
            >>> d = Dict()
            >>> d.split_dict({"a": 1, "b": 2, "c": 3}, 2)
            [{'a': 1, 'b': 2}, {'c': 3}]
        """
        dict_lengths = len(dictionary)
        batch_size = dict_lengths // split_nums
        batch_dict = []
        for n in range(split_nums + 1):
            cur_idx = batch_size * n
            end_idx = batch_size * (n + 1)
            cur_batch = dict(list(dictionary.items())[cur_idx: end_idx])
            batch_dict.append(cur_batch)
        return batch_dict

    def viw_pkl(self, path, start=0, end=10):
        """view dict in pickle file from start to end

        Args:
            path(str): absolute path
            start(int, optional): start index of dict. Defaults to 0.
            end(int, optional): end index of dict. Defaults to 10.

        Returns:
            result(dict): a small dict

        Examples:
            >>> d = Dict()
            >>> d.viw_pkl("/home/directory/test.pkl", 0, 10)
            {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5,
                'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10}
        """
        n_pkl = []
        with open(path, "rb") as f:
            dict_object = pickle.load(f)
            result = dict(list(dict_object.items())[start: end])
        return result

    def get_keys(slef, val, obj: dict):
        """get keys by value in dict

        Args:
            val([type]): value
            obj(dict): dict

        Returns:
            list: keys\

        Examples:
            >>> d = Dict()
            >>> d.get_keys(1, {"a": 1, "b": 2})
            ['a']
        """
        return [k for k, v in obj.items() if v == val]

    def sort_dict_by_value(self, d, increase=True):
        """sort dict by value

        Args:
            d(dict): dict to be sorted
            increase(bool, optional): increase sort or decrease sort. Defaults to True.

        Returns:
            [type]: [description]

        Examples:
            >>> d = Dict()
            >>> d.sort_dict_by_value({"a": 1, "b": 2, "c": 3}, increase=False)
            [{'c': 3}, {'b': 2}, {'a': 1}]
        """
        return dict(sorted(d.items(), key=lambda x: x[1], reverse=not increase))


class String(object):
    def __init__(self, *args):
        super(String, self).__init__(*args)

    def gen_a_random_probability():
        """generate a random probability obey uniform distribution

        Returns:
            float: a random probability

        Examples:
            >>> s = String()
            >>> s.gen_a_random_probability()
            0.5
        """
        return random.uniform(0, 1)

    def get_window_content(self, center, whole_context, windows_size):
        """given whole context, center then return window's content in range windows_size by character

        Args:
            center(str): center word
            whole_context(str): whole context
            windows_size(int): window size

        Returns:
            list: window's content

        Examples:
            >>> s = String()
            >>> s.get_window_content("a", "abcdefg", 3)
            ['a', 'b', 'c']
        """
        neighbors = []
        length = len(whole_context)
        # 窗口左边界下标
        left_boundary = max(center - windows_size // 2, 0)
        # 完整窗口坐标list
        window_idx = (
            list(range(left_boundary, center)) + [center] +
            list(range(center + 1, min(center + windows_size // 2 + 1, length))))
        # 完整窗口内容
        window_content = [whole_context[i] for i in window_idx]

        return "".join(window_content)

    def get_current_time(self, hour=True):
        """get current time

        Args:
            hour(bool, optional): show hours-minutes-seconds or not. Defaults to True.

        Returns:
            str: current time

        Examples:
            >>> s = String()
            >>> s.get_current_time()
            '2019-07-24 15:00:00'
            >>> s.get_current_time(False)
            '2019-07-24'
        """
        now = datetime.now()
        hour = "_%H-%M-%S" if hour else ""
        return now.strftime("%Y-%m-%d" + hour)

    def unquote_text(self, text):
        """parse quoted str to unquoted str

        Args:
            test (str): quoted text

        Returns:
            str: unquoted string

        Examples:
            >>> s = String()
            >>> s.url2str("%E6%8A%98%E5%8F%A0%E8%87%AA%E8%A1%8C%E8%BD%A6")
            '折叠自行车'
        """
        unquoted = unquote(text, encoding="utf-8", errors="replace")
        return unquoted

    def str2url(self, text):
        """convert unquoted str to quoted str

        Args:
            text (str): unquoted str

        Returns:
            str: quoted str

        Examples:
            >>> s = String()
            >>> s.str2url("折叠自行车")
            '%E6%8A%98%E5%8F%A0%E8%87%AA%E8%A1%8C%E8%BD%A6'
        """
        quoted = quote(text, encoding="utf-8", errors="replace")
        return quoted

    def remove_blank(self, text):
        """
        Args:
            text (str): input text, contains blank between zh and en, zh and zh, en and en
        Returns:
            str: text without blank between zh and en, zh and zh, but keep en and en

        Examples:
            >>> text = "比如 Convolutional Neural Network，CNN 对应中 文是卷 积神 经网络。"
            >>> remove_blank(text)
            "比如Convolutional Neural Network，CNN对应中文是卷积神经网络。"
        """
        # filter blank space between Chinese characters
        text = re.sub(r'([^a-zA-Z])([\u0020]*)', r'\1', text)
        # remove blank space between English characters and Chinese characters
        text = re.sub(r'([\u0020]*)([^a-zA-Z])', r'\2', text)
        return text

    def iszh(self, text):
        """check if text is Chinese

        Args:
            text (str): text

        Returns:
            bool: True if text is Chinese, False otherwise

        Examples:
            >>> iszh("比如")
            True
            >>> iszh("比如Convolutional Neural Network，CNN对应中文是卷积神经网络。")
            False
        """
        for ch in text:
            if not "\u4e00" <= ch <= "\u9fff":
                return False
        return True

    def colourful_text(text, color):
        """add color to text

        Args:
            text (str): [description]
            color (str): red, green, yello, blue, black, none

        Returns:
            str: coloured text

        Examples:
            >>> s = String()
            >>> s.colourful_text("比如Convolutional Neural Network，CNN对应中文是卷积神经网络。", "red")
            '\x1b[31m比如Convolutional Neural Network，CNN对应中文是卷积神经网络。\x1b[0m'
        """
        colourful = {
            "red": u"\033[1;31;1m%s\033[0m",
            "green": u"\033[1;32;1m%s\033[0m",
            "yello": u"\033[1;33;1m%s\033[0m",
            "blue": u"\033[1;34;1m%s\033[0m",
            "black": u"\033[1;30;1m%s\033[0m",
        }
        return colourful[color] % text if color != "none" else text

    def type_restore(self, value):
        """restore str go back to original type

        Args:
            value (str): input str 

        Returns:
            value (str): original type

        Examples:
            >>> s = String()
            >>> s.type_restore("1")
            1
            >>> s.type_restore("1.0")
            1.0
            >>> s.type_restore("True")
            True
            >>> s.type_restore("False")
            False
            >>> s.type_restore("None")
            None
            >>> s.type_restore("[1, 2, 3]")
            [1, 2, 3]
            >>> s.type_restore("{'a': 1, 'b': 2}")
            {'a': 1, 'b': 2}
        """
        try:
            value = ast.literal_eval(value)
        except Exception:
            value = value
        return value

    def extract(self, text, expression=None, type: str = None):
        """extract text from text by regular expression

        Args:
            text (str): input text
            expression (str, optional): regular expression. Defaults to None.
            type (str, optional): type of extracted text. Defaults to None.

        Returns:
            str: extracted text

        Examples:
            >>> s = String()
            >>> text ="我今天很happy，因为我喜欢的notebook终于卖完了。我是在刚刚发布的时候以12900元的价格买的，现在以12800元的价格卖出了。"
            >>> s.extract(text, type="en")
            (['happy', 'notebook'], True)
            >>> s.extract(text, type="zh")
            (['我今天很', '因为我喜欢的', '终于卖完了', '我是在刚刚发布的时候以', '元的价格买的', '现在以', '元的价格卖出了'], True)
            >>> s.extract(text, type="zh", expression="num")
            (['12900', '12800'], True)
            >>> s.extract(text, type="zh", expression="punctuation")
            (['，', '。', '，', '。'], True)
        """
        if type is not None:
            type2expression = {"en": r"[a-zA-Z]+", "zh": r"[\u4e00-\u9fa5]+", "num": r"\d+",
                               "punctuation": u"[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]"}
            expression = type2expression[type]
        try:
            pattern = re.compile(expression)
            results = re.findall(pattern, text)
            return results, True if len(results) != 0 else False
        except Exception:
            traceback.print_exc()

    def half_to_full(self, text):
        """convert half-width to full-width

        Args:
            text (str): half-width text

        Returns:
            change_text (str): full-width text

        Examples:
            >>> s = String()
            >>> s.half_to_full("abc")
            'ａｂｃ'
        """
        change_text = ""
        for word in text:
            inside_code = ord(word)
            if inside_code == 32:  # 半角空格直接转化
                inside_code = 12288
            elif inside_code >= 32 and inside_code <= 126:  # 半角字符（除空格）根据关系转化
                inside_code += 65248
            change_text += chr(inside_code)
        return change_text

    def full_to_half(self, text: str):  # 输入为一个句子
        """convert full-width to half-width

        Args:
            text (str): full-width text

        Returns:
            change_text (str): half-width text
        """
        change_text = ""
        for word in text:
            inside_code = ord(word)
            # print("before:", inside_code)
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            # elif inside_code in [ord("“"), ord("”")]:
            #     inside_code = ord('"')
            # elif inside_code == ord("。"):
            #     inside_code = ord(".")
            # elif inside_code in [ord("‘"), ord("’")]:
            #     inside_code = ord("'")
            elif inside_code >= 65281 and inside_code <= 65374:  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            change_text += chr(inside_code)
            # print("after:", inside_code)
        return change_text

    def lc_subsequence(self, str1: str, str2: str, split_char: str = " "):
        """longest common subsequence

        Args:
            str1 (str): str1
            str2 (str): str2
            split_char (str): split char, when character isn't joined, use split_char to split

        Returns:
            str: longest common subsequence

        Examples:
            >>> s = String()
            >>> s.lc_subsequence("我今天吃了碗饭", "我昨天也吃了一碗饭", "_")
            我_天_吃了_碗饭
            >>> s.lc_subsequence("我今天吃了碗饭", "我昨天也吃了一碗饭", "")
            我天吃了碗饭
        """
        m, n = len(str1), len(str2)
        L = [[0 for x in range(n + 1)] for x in range(m + 1)]
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif str1[i - 1] == str2[j - 1]:
                    L[i][j] = L[i - 1][j - 1] + 1
                else:
                    L[i][j] = max(L[i - 1][j], L[i][j - 1])
        index = L[m][n]
        lcs = [""] * (index + 1)
        lcs[index] = ""
        i = m
        j = n
        join = True
        while i > 0 and j > 0:
            if str1[i - 1] == str2[j - 1]:
                split_code = ""
                if not join:
                    split_code = split_char
                lcs[index - 1] = str1[i - 1] + split_code
                i -= 1
                j -= 1
                index -= 1
                join = True
            elif L[i - 1][j] > L[i][j - 1]:
                i -= 1
                join = False
            else:
                j -= 1
                join = False
        return "".join(lcs)

    def lc_substring(self, str1, str2):
        """longest common substring

        Args:
            str1 (str): str1
            str2 (str): str2

        Returns:
            str: longest common substring
            int: length of longest common substring

        Examples:
            >>> s = String()
            >>> s.lc_substring("我今天是吃了碗饭", "我昨天也是吃了一碗饭")
            ('是吃了', 3)
        """
        m = [[0 for i in range(len(str2) + 1)]
             for j in range(len(str1) + 1)]
        mmax = 0  # 最长匹配的长度
        p = 0  # 最长匹配对应在s1中的最后一位
        for i in range(len(str1)):
            for j in range(len(str2)):
                if str1[i] == str2[j]:
                    m[i + 1][j + 1] = m[i][j] + 1
                    if m[i + 1][j + 1] > mmax:
                        mmax = m[i + 1][j + 1]
                        p = i + 1
        return str1[p - mmax:p], mmax  # 返回最长子串及其长

    def index_substring(self, text, sub_text):
        """given a text, find all the sub-text's index

        Args:
            text (str): text
            sub_text (str): sub-text

        Yields:
            int: sub-text's index

        Examples:
            >>> s = String()
            >>> sub_idxs =s.index_substring("我今天吃了碗饭，我昨天也吃了一碗饭", "碗饭")
            >>> [_ for _ in sub_idxs]
            [5, 15]
        """
        start = 0
        while True:
            start = text.find(sub_text, start)
            if start == -1:
                return
            yield start
            # use start += 1 to find overlapping matches
            start += len(sub_text)

    def extact_content_between_marks(self, text, expression: str = None, type: str = None):
        """extract content in bracket

        Args:
            text (str): text
            expression (str): expression

        Returns:
            str: content in bracket

        Examples:
            >>> s = String()
            >>> text = "如果说【上天】愿意再次给我（一次机会），那么我(希望)保持现状"
            >>> s.extact_content_in_bracket(text=text)
            ['【上天】', '（一次机会）', '(希望)']
        """
        if type is not None:
            type2expression = {
                "bracket": r"(\[|（|\(|【|《).+?(）|\]|\)|】|》)", "quotation": r"(\"|\'|‘|“).+?(’|”|\'|\")"}
            expression = type2expression[type]
        elif expression is None:
            raise ValueError("expression is None")
        pattern = re.compile(expression)
        matchs = re.finditer(pattern, text)
        results = []
        for match in matchs:
            results.append(match.group())
        return results if len(results) != 0 else None

    def split_text(self, text, pattern=r";|。|；|,|，"):
        """split text by pattern

        Args:
            text (str): text
            pattern (regexp, optional): expression. Defaults to r";|。|；|,|，".

        Returns:
            str: text split by pattern

        Examples:
            >>> s = String()
            >>> text = "收快递的时候最怕收不到货，所以购物的时候一定要把地址写清楚，这样才会精准的送到你手里，我告诉大家以后怎么写：“本宇宙-拉尼凯亚超星系团-室女座星系团-本星系群-银河系-猎户臂-太阳系-第三行星-地球-亚洲板块-中国-xxx-xxx-xxx”这样可以保证不会送到其他宇宙去"
            >>> s.split_text(text=text)
            ['收快递的时候最怕收不到货', '所以购物的时候一定要把地址写清楚', '这样才会精准的送到你手里', '我告诉大家以后怎么写：“本宇宙-拉尼凯亚超星系团-室女座星系团-本星系群-银河系-猎户臂-太阳系-第三行星-地球-亚洲板块-中国-xxx-xxx-xxx”这样可以保证不会送到其他宇宙去']
        """
        txts = re.split(pattern, text)
        return txts

    def similar(self, str1, str2):
        """calculate similarity between two strings

        Args:
            str1 (str): str1
            str2 (str): str2

        Returns:
            float: similarity

        Examples:
            >>> s = String()
            >>> s.similar("我今天是吃了碗饭", "我昨天也是吃了一碗饭")
            0.75
        """
        return SequenceMatcher(None, str1, str2).ratio()

    def str_num_type(self, string):
        """check string whether belong to int,float,complex or not

        Args:
            string (str): string

        Returns:
            str: int,float,complex or None

        Examples:
            >>> s = String()
            >>> s.str_num_type("1")
            'int'
            >>> s.str_num_type("1.0")
            'float'
            >>> s.str_num_type("1+1j")
            'complex'
            >>> s.str_num_type("1.0.5.355")
            None

        """
        types = [int, float, complex]
        _string = self.type_restore(string)

        for type in types:
            if isinstance(_string, type):
                return str(type.__name__)
        return None

    def proper_nouns_alignment(self, original_text, changed_text):
        """this function align the content which surround by bracket or
        quotation marks. Prevent some proper nouns changed by the reducer system.

        Args:
            original_text (string): original text
            changed_text (string): changed text

        Returns:
            [string]: alignment text 
        """

        expression_types = ["bracket", "quotation"]
        for regular_exp in expression_types:
            result1 = self.extact_content_between_marks(
                original_text, type=regular_exp)
            result2 = self.extact_content_between_marks(
                changed_text, type=regular_exp)
            if len(result1) != len(result2):
                return changed_text, False
            for idx, ele in enumerate(result2):
                origin_ele = result1[idx]  # 按序匹配
                changed_text = changed_text.replace(ele, origin_ele)
        return changed_text, True

    def detect_repeat(self, text, expression=r"([\u4e00-\u9fa5])(\1+)"):
        """detect repeat characters

        Args:
            text (str): text
            expression (regexp, optional): regular expression . Defaults to r"([\u4e00-\u9fa5])(\1+)".

        Returns:
            (list): repeat characters

        Examples:
            >>> s = String()
            >>> text = "锄禾日当当午，汗滴禾下下土"
            >>> s.detect_repeat(text)
            ['当当', '下下']
        """
        pattern = re.compile(expression)
        matchs = re.finditer(pattern, text)
        results = []
        for match in matchs:
            results.append(match.group())
        return results


class PDF(object):
    def __init__(self, *args):
        super(PDF, self).__init__(*args)
        self.opfile = File()

    def pdf2image(self, pdf_path, pdf_stream=None, output_path=None, zoom_x=1, zoom_y=1, size: tuple = None, rotation_angle=0):
        # 打开PDF文件
        if pdf_path is not None:
            pdf = fitz.open(pdf_path)
        elif pdf_stream is not None:
            pdf = fitz.open(stream=pdf_stream, filetype="pdf")
        else:
            raise Exception("pdf_path or pdf_stream must be not None")
            # 逐页读取PDF
        images = []
        if output_path is not None:
            self.opfile.generate_cleanfolder(output_path)
        for pg in range(0, pdf.pageCount):
            page = pdf[pg]
            # 设置缩放和旋转系数
            _, _, page_width, page_height = page.rect
            if size is not None:
                zoom_x = size[0] / page_width
                zoom_y = size[1] / page_height
            trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
            pm = page.get_pixmap(matrix=trans, alpha=False)
            # 开始写图像
            img = Image.frombytes(
                mode="RGB", size=[pm.width, pm.height], data=pm.samples)
            if output_path is not None:
                path = os.path.join(output_path, str(pg)+".png")
                img.save(path)
            images.append(img)
        pdf.close()
        return images

    def extract_table(self, pdf_path: str, output_path: str = None, extension=".jpg"):
        """extract tables from pdf

        Args:
            pdf_path (str): pdf absolute path
            output_path (str): output path
            extension (str, optional): if save to output_path, then decide to extension. Defaults to ".jpg".

        Returns:
            pdf_infos (dict): pdf infos

        Examples:
            >>> pdf = PDF()
            >>> pdf.extract_table(pdf_path="../data/pdf/test.pdf", output_path="../data/pdf/test")
            {
                '18_0': {'bbox': (84.60000000000002, 95.63997999999998, 510.72000500000007, 215.16000999999997), 
                'data': [['xxx', 'xxx', 'xxx'], ['xxx', 'xxx', 'xxx'], ['xxx', 'xxx', 'xxx'], ['xxx', 'xxx', 'xxx'], ['微晶石', 'XAAR喷头', '图案清晰']]}
            }
        """
        if output_path is not None:
            self.opfile.generate_cleanfolder(output_path)
        images = self.pdf2image(pdf_path=pdf_path)
        pdf_infos = {}

        def isListEmpty(inList):
            if isinstance(inList, list):  # Is a list
                return all(map(isListEmpty, inList))
            elif isinstance(inList, str):
                return len(inList) == 0
            return False  # Not a list

        pdf = pdfplumber.open(pdf_path)
        for i, page in enumerate(tqdm(pdf.pages, desc="parsing pdf page...")):
            try:
                table_infos = page.find_tables(table_settings={})
                table_data = page.extract_tables(table_settings={})
            except Exception as e:
                continue
            for j, table_info in enumerate(table_infos):
                page_num = str(table_info.page.page_number)
                block_num = str(j)
                if not isListEmpty(table_data):
                    image = images[i]
                    image = asarray(image)
                    image = image[..., ::-1]
                    x_1, y_1, x_2, y_2 = table_info.bbox
                    temp = image[math.ceil(y_1):math.floor(
                        y_2), math.ceil(x_1):math.floor(x_2)]
                    temp = Image.fromarray(temp, 'RGB')
                    if output_path is not None:
                        savepath = os.path.join(output_path, "%s_%s.%s" % (
                            page_num, block_num, extension))
                        temp.save(savepath)
                    pdf_infos["%s_%s" % (page_num, block_num)] = {
                        "bbox": table_info.bbox, "data": table_data[j]}

        return pdf_infos


class Figure(object):
    def __init__(self, *args):
        super(Figure, self).__init__(*args)

    def dilation(self, image, thresh=250, save_path=None, morph_size=(8, 8), iterations=1):
        """ dialate given image

        Args:
            image (np.array): image to dialate
            save_path (str): path to save dialated image
            morph_size (tuple): size of the kernel
            iterations (int): number of iterations

        Returns:
            np.array: dialated image

        Example:
            >>> dilation(image=image, save_path=save_path, morph_size=(8, 8), iterations=1)
        """
        # convert RGB to grayscale image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # convert to binary image
        image = cv2.threshold(
            image, thresh, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # dilate the text to make it solid spot
        image = image.copy()
        struct = cv2.getStructuringElement(cv2.MORPH_RECT, morph_size)
        image = cv2.dilate(~image, struct, anchor=(-1, -1),
                           iterations=iterations)
        image = ~image
        if save_path is not None:
            cv2.imwrite(save_path, image)
        return image

    def is_blank_image(self, image):
        """ check if image is blank

        Args:
            image (np.array): image to check

        Returns:
            bool: True if image is blank, False otherwise
            white_percentage : percentage of white pixels

        Example:
            >>> is_blank_image(image=image)
        """
        # binary image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # get the shape of image
        shape = image.shape
        # get the number of pixels value = 255
        white_pixels = np.sum(image == 255)
        white_percentage = white_pixels / (shape[0] * shape[1])
        if white_percentage > 0.99:
            return True, white_percentage
        else:
            return False, white_percentage


if __name__ == '__main__':
    lp = LineProfiler()

    p = PDF()
    # lp.add_function(DTA.process_pdf)
    # lp.add_function(DTA._process_images)
    lp_wrapper = lp(p.pdf2image)
    lp_wrapper(pdf_path="/mnt/f/data/CV/pdfs/1100000206088611.pdf",
               size=(1654, 2339))
    lp.print_stats()
