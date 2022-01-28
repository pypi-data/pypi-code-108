import pandas as pd

def dfAppend(df:pd.DataFrame, dicKey:int, row:int):

    """ 
    dataframeに行を追加(appendの代替)

    Parameters
    ----------
    df : pd.DataFrame
        pandas DataFrame
    dicKey : int
        ディクショナリキー
    row : int
        行番号

    """

    # 追加用のディクショナリを宣言
    dict_tmp = {}

    # ディクショナリに行番号をセット
    dict_tmp[dicKey] = row

    # キー値を加算
    dicKey += 1

    # 戻り値を返す
    return df.from_dict(dict_tmp, orient="index"), dicKey