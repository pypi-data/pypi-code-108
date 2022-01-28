import sys
import configparser
import os
import pathlib
import logging
import traceback
import functools
from .uwException import * 

class cmnConfigBase():
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        self.config_ini = None
        """ iniファイル読込内容 """

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

    def setInstanceMemberValues(self):

        """ 
        インスタンス変数に読み取った設定値をセットする
        
        Parameters
        ----------
        None
        """
        
        pass
    
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
    
class cmnConfig(cmnConfigBase):

    """
    共通設定クラス
    """ 

    class settingValueStruct():

        """
        設定値構造体
        """ 

        class ConnectionString:
            
            """
            接続文字列
            """ 
            
            def __init__(self):
                
                """ 
                コンストラクタ
                """ 

                # メンバ変数初期化

                self.DatabaseKind = 'postgresql+psycopg2'
                """ データベース種類 """

                self.User = ''
                """ 接続ユーザー """
                
                self.Password = ''
                """ 接続パスワード """
                
                self.Host = ''
                """ 接続先ホスト """
                
                self.Port = ''
                """ 接続先ポート番号 """
                
                self.DatabaseName = ''
                """ 接続先データベース名 """

    class startupConfig(cmnConfigBase):
        
        """
        スタートアップConfigクラス
        """

        def __init__(self):

            """
            コンストラクタ
            """
            
            self.configFolderPath = ''
            """ Configファイルが格納されているフォルダパス """

        def setInstanceMemberValues(self):

            """ 
            インスタンス変数に読み取った設定値をセットする
            
            Parameters
            ----------
            startupConfig_ini : ConfigParser
                スタートアップConfig用のConfigParser
            
            """
            
            # Configファイル格納場所
            self.setConfigValue('configFolderPath', self.config_ini,'PATH','CONFIG_FOLDER_PATH', str)

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

        self.ConnectionString = self.settingValueStruct.ConnectionString()
        """ 接続文字列 """

        self.scriptFilePath = ''
        """ スクリプトファイルパス """

        self.startupCfg = self.startupConfig()
        """ スタートアップConfig """
        
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
        _scriptFilePath : str
            スクリプトファイルパス
        configFileDir : str
            iniファイルがあるディレクトリ(相対パス)
        
        """
        
        # configparser宣言
        config_ini = configparser.ConfigParser()

        # Configファイル読込前の設定情報取得([呼び出し元pythonファイル名.ini])
        self.startupCfg = self.getStartupConfig(_scriptFilePath)
        if configFileDir == '':
            configFileDir = self.startupCfg.configFolderPath
            
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
                    sys.exit()

        # iniファイル読込
        config_ini.read(iniFilePath, encoding='utf-8')
        
        # 読込内容をインスタンス変数に設定する
        self.config_ini = config_ini

        # 各設定値をインスタンス変数にセット
        self.setInstanceMemberValues()
    
    def getStartupConfig(self, _scriptFilePath: str):

        """ 
        スタートアップ設定ファイル読込
        
        Parameters
        ----------
        _scriptFilePath : str
            スクリプトファイルパス
        
        """

        # startupConfigクラス
        startupCfg = self.startupConfig()

        # configparser宣言
        startupCfg.config_ini = configparser.ConfigParser()

        # ファイル名(拡張子なし)取得
        startupConfigFileNameNotExtention = pathlib.Path(_scriptFilePath).stem
        # スタートアップ設定ファイル名取得
        startupConfigFileName = startupConfigFileNameNotExtention + '.ini'
        # スタートアップ設定ファイルのパス取得
        startupConfigFilePath = os.path.join(os.path.dirname(_scriptFilePath), startupConfigFileName)
        # スタートアップ設定ファイルの存在有無
        if os.path.exists(startupConfigFilePath):
                        
            # iniファイル読込
            startupCfg.config_ini.read(startupConfigFilePath, encoding='utf-8')

            # メンバ変数に値セット
            startupCfg.setInstanceMemberValues()
            
        return startupCfg

    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        
        Parameters
        ----------
        None
        """
        
        # ログファイル名
        self.setConfigValue('LogFileName', self.config_ini,'DEFAULT','LOGFILE_NAME', str)
        # ログファイル格納先ディレクトリ
        self.setConfigValue('LogFolderName', self.config_ini,'DEFAULT','LOGFOLDER_NAME', str)
        # ログフォーマット
        self.setConfigValue('LogFormat', self.config_ini,'DEFAULT','LOGFORMAT', str)
        # ログレベル
        self.setConfigValue('LogLevel', self.config_ini,'DEFAULT','LOGLEVEL', int)

        # データベース種類
        self.setConfigValue('ConnectionString.DatabaseKind', self.config_ini,'CONNECTION_STRING','DATABASE_KIND', str)
        # 接続ユーザー
        self.setConfigValue('ConnectionString.User', self.config_ini,'CONNECTION_STRING','USER', str)
        # 接続パスワード
        self.setConfigValue('ConnectionString.Password', self.config_ini,'CONNECTION_STRING','PASSWORD', str)
        # ホスト名
        self.setConfigValue('ConnectionString.Host', self.config_ini,'CONNECTION_STRING','HOST', str)
        # ポート番号
        self.setConfigValue('ConnectionString.Port', self.config_ini,'CONNECTION_STRING','PORT', str)
        # データベース名
        self.setConfigValue('ConnectionString.DatabaseName', self.config_ini,'CONNECTION_STRING','DATABASE_NAME', str)
    