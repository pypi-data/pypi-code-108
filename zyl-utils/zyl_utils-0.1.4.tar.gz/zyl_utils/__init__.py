# encoding: utf-8
"""
@author: zyl
@file: __init__.py
@desc: import
"""

from .data_utils.analysis import Analyzer
# data
from .data_utils.processing import Processor
from .data_utils.text_processing import MyTokenizer
from .data_utils.text_processing import TextProcessor
from .data_utils.html_processing import HtmlProcessor
from .data_utils.image_processing import ImageProcessor
from .data_utils.pdf_processing import PDFProcessor


# processing
split_data_evenly = Processor.split_data_evenly  # 均分数据
split_train_eval = Processor.split_train_eval  # 切分训练集和评估集
two_classification_sampling = Processor.two_classification_sampling  # 二分类采样
remove_some_model_files = Processor.remove_some_model_files  # 删除模型冗余文件
save_dataframe_to_excel = Processor.save_dataframe_to_excel  # df保存至excel，sheet

# text processing
# 切句切词: my_tokenizer = MyTokenizer() \ my_tokenizer.cut_paragraph_to_sentences, my_tokenizer.cut_sentence_to_words
clean_text = TextProcessor.clean_text  # 清洗数据
ner_find = TextProcessor.ner_find  # 从文本中搜寻实体---继续优化
remove_illegal_chars = TextProcessor.remove_illegal_chars  # 移除非法字符
remove_invisible_chars = TextProcessor.remove_invisible_chars  # 移除不可见字符
remove_html_tags = TextProcessor.remove_html_tags  # 移除html标签---待优化

# analysis
get_text_language = Analyzer.get_text_language  # 文本的语言
get_text_string_length = Analyzer.get_text_string_length  # 文本字符串长度
get_text_token_length = Analyzer.get_text_token_length  # 文本model_token长度
show_dataframe_base_info = Analyzer.show_dataframe_base_info  # df基本信息
show_dataframe_completely = Analyzer.show_dataframe_completely  # df完全显示
show_plt_completely = Analyzer.show_plt_completely  # plt显示问题
analyze_numerical_array = Analyzer.analyze_numerical_array  # 分析数值数组
analyze_category_array = Analyzer.analyze_category_array  # 分析分类数组
show_bio_data_info = Analyzer.show_bio_data_info  # 分析实体识别bio数据

# image processing
ImgProcessor = ImageProcessor()
show_image = ImgProcessor.show_image
format_image = ImgProcessor.format_image
read_image = ImgProcessor.read_image
save_image = ImgProcessor.save_image
get_text_from_one_image = ImgProcessor.get_text_from_one_image
get_tables_from_image = ImgProcessor.get_tables_from_image

# html processing
turn_html_content_to_pdf = HtmlProcessor.turn_html_content_to_pdf

# pdf processing
extract_tables_from_non_scanned_pdf = PDFProcessor.extract_tables_from_non_scanned_pdf
get_text_from_pdf_area = PDFProcessor.get_text_from_pdf_area
get_texts_and_tables_from_pdf = PDFProcessor.get_texts_and_tables_from_pdf


#########################################################################
# model
from .model_utils.model_utils import ModelUtils

# model_uitls
get_best_cuda_device = ModelUtils.get_best_cuda_device  # 获取最好的若干cuda
fix_torch_multiprocessing = ModelUtils.fix_torch_multiprocessing  # fix_torch_multiprocessing
predict_with_multi_gpus = ModelUtils.predict_with_multi_gpus

# models
from .model_utils.models.ner_bio import NerBIO, NerBIOModel
from .model_utils.models.ner_t5 import NerT5

# metric
from .model_utils.metrics.ner_metric import entity_recognition_metrics  # 实体识别t5评估标准

# algorithm
from .model_utils.algorithms.sunday_match import sunday_match  # 子序列匹配
