import configparser
import os
import pathlib
import logging
import traceback
import functools
from .uwException import * 

class cmnConfig:

    """
    共通設定クラス
    """ 

    def __init__(self):

        """
        コンストラクタ
        """

        self.LogFileName = 'default.log'
        """ ログファイル名 """

        self.LogFolderName = 'log'
        """ ログ出力先フォルダ名 """

        self.LogFormat = '%(levelname)s : %(asctime)s : %(message)s'
        """ ログフォーマット定義 """

        self.LogLevel:int = logging.DEBUG
        """ ログレベル """

        self.config_ini = None
        """ iniファイル読込内容 """

        self.scriptFilePath = ''
        """ スクリプトファイルパス """

    def getConfigFileName(self):
        
        """ 
        設定ファイル名を取得する
        
        Returns
        -------
            設定ファイル名
        
        Notes
        -----
            設定ファイル名を変更したい場合はcmnConfigを継承して当メソッドをオーバーライドする
        """
        return 'LibHanger.ini'
    
    def getConfig(self, _scriptFilePath: str, configFileDir: str = ''):

        """ 
        設定ファイルを読み込む 
        
        Parameters
        ----------
        self : LibHanger.cmnConfig
            共通設定クラス
        scriptPath : str
            スクリプトファイルパス
        configFileDir : str
            iniファイルがあるディレクトリ(相対パス)
        
        """
        
        # configparser宣言
        config_ini = configparser.ConfigParser()

        # スクリプトファイルパスをセット
        self.scriptFilePath = _scriptFilePath
        
        # スクリプトファイルの場所から見たiniファイル相対パス取得
        iniFileDirPath = self.getConfigFileName() \
            if configFileDir == '' else os.path.join(configFileDir, self.getConfigFileName())
        # スクリプトファイルの絶対パス取得
        iniScriptPathAbs = pathlib.Path(os.path.abspath(os.path.dirname(_scriptFilePath)))
        # iniファイルパス取得
        iniFilePath = os.path.join(iniScriptPathAbs, iniFileDirPath)

        # iniファイル存在確認
        if (not os.path.exists(iniFilePath)): 
            try:
                raise iniFilePathError
            except iniFilePathError as e:
                print(e)
                with open("log/error.log", 'a') as f:
                    traceback.print_exc(file=f)

        # iniファイル読込
        config_ini.read(iniFilePath, encoding='utf-8')
        
        # 読込内容をインスタンス変数に設定する
        self.config_ini = config_ini

        # 各設定値をインスタンス変数にセット
        self.setInstanceMemberValues()
        
    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        
        Parameters
        ----------
        None
        """
        
        self.setConfigValue('LogFileName', self.config_ini,'DEFAULT','LOGFILE_NAME', str)
        self.setConfigValue('LogFolderName', self.config_ini,'DEFAULT','LOGFOLDER_NAME', str)
        self.setConfigValue('LogFormat', self.config_ini,'DEFAULT','LOGFORMAT', str)
        self.setConfigValue('LogLevel', self.config_ini,'DEFAULT','LOGLEVEL', int)

    def setConfigValue(self, 
                       insVariableName: str, 
                       config_ini: list, 
                       section: str, 
                       key: str, 
                       dataType: type):
        
        """ 
        iniファイルから読み取った値をインスタンス変数セットする \n
        指定したセクション、キーが存在しない場合はインスタンス変数の元値を保持する
        
        Parameters
        ----------
        self : LibHanger.cmnConfig
            共通設定クラス
        insVariableName : str
            インスタンス変数名
        config_ini : list
            iniファイル読込内容List
        section : str
            iniファイルセクション名
        key : str
            iniファイルキー名
        dataType : type
            インスタンス変数のデータ型
        
        Notes
        -----
        
            @insVariableName
            ----------------
                インスタンス変数名をネストする場合は"."コロンで区切る 
                例:self.STRUCT.Test1の場合 ⇒ insVariableNameに"STRUCT.Test1"を指定する 
        
        """
        
        keyExists = section in config_ini
        if keyExists and config_ini[section].get(key) != None:
            
            if dataType is str:
                self.rsetattr(self, insVariableName, config_ini[section][key])
            elif dataType is int:
                self.rsetattr(self, insVariableName, int(config_ini[section][key]))
            elif dataType is float:
                self.rsetattr(self, insVariableName, float(config_ini[section][key]))

    def rsetattr(self, obj, attr, val):
        
        """ 
        インスタンス変数の値を書き換える(ネスト用setattr)

        Parameters
        ----------
        obj : LibHanger.cmnConfig
            cmnConfigインスタンス
        attr : str
            インスタンス変数名
        val : object
            置き換える値
        """
        
        pre, _, post = attr.rpartition('.')
        return setattr(self.rgetattr(obj, pre) if pre else obj, post, val)

    def rgetattr(self, obj, attr, *args):
        
        """ 
        インスタンス変数を参照する(ネスト用getattr)

        Parameters
        ----------
        obj : LibHanger.cmnConfig
            cmnConfigインスタンス
        attr : str
            インスタンス変数名
        *args : object
            Unknown
        """
        
        def _getattr(obj, attr):
            return getattr(obj, attr, *args)
        return functools.reduce(_getattr, [obj] + attr.split('.'))