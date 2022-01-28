import inspect
from msilib.schema import CompLocator
import pandas as pd
import copy

class recset():
    
    """
    レコードセットクラス
    """
    
    def __init__(self, t) -> None:
        
        """
        コンストラクタ
        
        Parameters
        ----------
        t : Any
            Modelクラス
        """
        
        # Modelクラス
        self.modelType = t
        
        # レコードセット行初期化
        self.rows = []
        
        # カラム情報
        self.__columns = self.__getColumnAttr()
        
        # 主キー情報
        self.__primaryKeys = self.__getPrimaryKeys()
    
    def __getColumnAttr(self):
        
        """
        モデルクラスのインスタンス変数(列情報)取得

        Parameters
        ----------
        None
        
        """
        
        # インスタンス変数取得
        attributes = inspect.getmembers(self.modelType, lambda x: not(inspect.isroutine(x)))
        
        # 特定のインスタンス変数を除外してリストとしてインスタンス変数を返す
        return list(filter(lambda x: not(x[0].startswith("__") or x[0].startswith("_") or x[0] == "metadata" or x[0] == "registry"), attributes))
    
    def __getPrimaryKeys(self):
        
        """
        主キー情報取得

        Parameters
        ----------
        None
        
        """
        
        # 主キーリスト作成            
        primaryKeys = []
        for col in self.__columns:

            memberInvoke = getattr(self.modelType, col[0])            
            if memberInvoke.primary_key == True:
                primaryKeys.append(col[0])
        
        # 主キー情報を返す        
        return primaryKeys
    
    def newRow(self):
        
        """
        新規行を生成する

        Parameters
        ----------
        None

        """

        return self.rowSetting(self.modelType())
        
    def rowSetting(self, row):
        
        """
        行情報を生成する
        
        Parameters
        ----------
        None
        
        """
        
        for col in self.__columns:

            # Modelのインスタンス変数取得
            memberInvoke = getattr(self.modelType, col[0])
            # 既定値の設定
            setattr(row, col[0], memberInvoke.default.arg)

        # 生成した行を返す                                     
        return row
    
    def columns(self):
        
        """
        カラム情報プロパティ
        """
        
        return self.__columns
    
    def addRow(self, row):
        
        """
        レコードセットに行を追加する
        
        Parameters
        ----------
        row : Any
            追加する行情報
        """
        
        self.rows.append(row)
    
    def eof(self):
        
        """
        レコードセットの行情報有無を返す
        
        Parameters
        ----------
        None
        
        """
        
        return False if len(self.rows) > 0 else True
    
    def primaryKeys(self):
        
        """
        主キー情報プロパティ
        """
        
        return self.__primaryKeys
    
    def getDataFrame(self):
        
        """
        Model⇒DataFrameに変換する

        Parameters
        ----------
        None

        """
        
        rowlist = []
        if len(self.rows) == 0:
            for column in self.__columns:
                rowlist.append(column[0])
        else:            
            # 行インスタンスをDeepCopy
            targetRows = copy.deepcopy(self.rows)
            # DataFrame化で不要な列を削除
            for rowInstance in targetRows:
                delattr(rowInstance, '_sa_instance_state')
            # 行インスタンスをリスト化
            rowlist = list(map(lambda f: vars(f), targetRows))

        # rowlistをDataFrame変換
        df = pd.DataFrame(rowlist) if len(self.rows) > 0 else pd.DataFrame(columns=rowlist)
        
        # DataFrameに主キー設定
        if len(self.__primaryKeys) > 0 and len(self.rows) > 0:
            df = df.set_index(self.__primaryKeys, drop=False)
                
        # 戻り値を返す
        return df