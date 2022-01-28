import os
import json
import pandas as pd

class BaseImport():

    """
    インポートクラス基底
    """

    pass

class ExcelImporter(BaseImport):

    """
    Excelインポートクラス
    """
    
    def __init__(self):
        
        """
        コンストラクタ
        
        Parameters
        ----------
        None
        
        """
        
        self.workbooks = None
        """Excelワークブック"""

        self.sheets = None
        """Excelワークシート"""

        self.filepath = None
        """Excelファイルパス"""
        
    def openBook(self, filePath:str):
        
        """
        Excelブックを開く
        
        Parameters
        ----------
        filePath : str
            ファイルパス
            
        """
        
        # ファイルパス保持
        self.filepath = filePath
        # ブックの読み込み
        self.workbooks = pd.ExcelFile(filePath)
        # シートの読み込み
        self.sheets = self.workbooks.sheet_names

class ExcelToJson(ExcelImporter):
    
    """
    ExcelファイルをJsonファイルに変換する
    """
    
    def __init__(self, __startRowNo:int):
        
        """
        コンストラクタ
        """

        super().__init__()
        
        self.startRowNo = __startRowNo
        """ 読込開始行番号 """

    def put_excelToJson(self):
        
        """
        読み込んだExcelファイルをjsonファイルに変換して出力する

        Parameters
        ----------
        None
        
        """
                
        for sheetname in self.sheets:
            # シート内容をDataFrameで取得
            df = self.get_sheetByDataFrame(sheetname)
            # Model内容をpythonファイル出力
            self.put_jsonFile(df, sheetname)
    
    def get_sheetByDataFrame(self, sheetname:str):
        
        """
        シート内容をDataFrameに変換
        
        Parameters
        ----------
        sheetname : str
            読込対象シート名
        """

        # シートをdict型に変換
        dict = pd.read_excel(self.filepath, sheet_name=sheetname, skiprows=self.startRowNo)
        # dict->DataFrame
        df = pd.DataFrame(dict)
        # DataFrameとして返す
        return df
    
    def put_jsonFile(self, df:pd.DataFrame, sheetname:str):
        
        """
        シート内容をjsonファイルに変換
        
        Parameters
        ----------
        sheetname : str
            読込対象シート名
        """
        
        # 出力先パス取得
        output_dir = os.path.dirname(self.filepath)

        # 欠損値を置換する
        df = self.fillnaDataFrame(df)
        
        # 対象DataFrameをdictに変換
        data_dict = df.to_dict()
        
        # jsonファイル出力
        with open(os.path.join(output_dir, sheetname + '.json'), 'w', newline='', encoding='utf-8') as f:
            f.write(json.dumps(data_dict, ensure_ascii = False, indent = 4))
        
        # ファイルClose
        f.close()
        
    def fillnaDataFrame(self, df:pd.DataFrame):
        
        """
        DataFrameの欠損値置換
        
        Parameters
        ----------
        df : DataFrame
            対象DataFrame
        """
        
        return df.fillna('')
    
class JsonImporter(BaseImport):
    
    def __init__(self, __file__) -> None:
        
        """
        コンストラクタ
        """

        super().__init__()

        self.rootPath = os.path.dirname(__file__)
        """ ルートパス """

    def convertToDataFrame(self, dir, fileName) -> pd.DataFrame:
        
        # jsonファイルをdict型で取得する
        dict_json = self.convertToDict(dir, fileName)
        
        # dictをdataframeに変換する(キーをカラム名とする)
        return pd.DataFrame(dict_json)
        
    def convertToDict(self, dir, fileName) -> dict:

        # jsonファイルを開く
        file_json = self.openJsonFile(dir, fileName)
        
        # jsonファイルをロードする
        return json.load(file_json)

    def openJsonFile(self, dir, fileName):
        
        # jsonファイルパス取得
        filePath = os.path.join(self.rootPath, dir, fileName)

        # jsonファイルを開く
        return open(filePath,'r',encoding='utf-8')
        