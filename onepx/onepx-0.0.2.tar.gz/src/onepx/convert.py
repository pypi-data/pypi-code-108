"""
将ocr识别后的文本转换为DataFrame

"""


"""
将ocr识别后的文本转换为DataFrame

"""


# 定义个函数
def ocrtext2df(text, column_size, ignore_na=False):
    """
        便于ocr截图识别后转表格
        text: 带换行的text
        column_size: 需要转成几列
        ignore_na: 是否删除中间空行
    """

    import pandas as pd
    import numpy as np

    str_list = text.strip().splitlines()
    if ignore_na:
        str_list = [x for x in str_list if len(x)]
    nd_arr = np.array(str_list).reshape(len(str_list) // column_size, column_size)
    return pd.DataFrame(nd_arr[1:], columns=list(nd_arr[:1].flatten()))
