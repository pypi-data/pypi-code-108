import os
from socketserver import DatagramRequestHandler
import pandas as pd
from sqlalchemy import schema
from sqlalchemy.sql.elements import Null
import LibHanger.Library.uwGetter as Getter
from pandas.core.frame import DataFrame
from LibHanger.Library.uwImport import ExcelImporter

class modelGenerator(ExcelImporter):
    
    """ 
    Modelジェネレータークラス
    """
    
    def __init__(self) -> None:
        
        """
        コンストラクタ

        Parameters
        ----------
        None
        
        """
        
        super().__init__()
        
        # フィールド型の対応クラス及びカラムタイプ定義
        self.fieldTypeMapPy = {
             'varchar':{'method':'CharFields','columnType':'String'}
            ,'numeric':{'method':'NumericFields','columnType':'Numeric'}
            ,'date':{'method':'DateFields','columnType':'Date'}
            ,'datetime':{'method':'DateTimeFields','columnType':'DateTime'}
            ,'integer':{'method':'IntFields','columnType':'Integer'}
            ,'double':{'method':'FloatFields','columnType':'Float'}
        }
        
    def put_modelToPython(self):
        
        """
        モデル⇒Pythonファイル出力

        Parameters
        ----------
        None
        
        """
        
        for sheetname in self.sheets:
            if str(sheetname).startswith(('trn','mst')): 
                # テーブル定義をDataFrameで取得
                df = self.get_TableDefByDataFrame(sheetname)
                # Model内容をpythonファイル出力
                self.put_modelPython(df, sheetname)
    
    def put_modelToSql(self):
        
        """
        モデル⇒SQLファイル出力

        Parameters   
        ----------
        None
        
        """
        
        # テーブル一覧リスト取得
        dfTableList = self.get_TableListByDataFrame('テーブル一覧表')
        
        for sheetname in self.sheets:
            if str(sheetname).startswith(('trn','mst')): 
                # テーブル定義をDataFrameで取得
                dfDef = self.get_TableDefByDataFrame(sheetname)
                # Model内容をsqlファイル出力
                self.put_modelTableCreateSql(dfDef, dfTableList, sheetname)
        
    def get_TableDefByDataFrame(self, sheetname:str):
        
        """
        テーブル定義シートをDataFrameに変換
        
        Parameters
        ----------
        sheetname : str
            読込対象シート名
        """

        # シートをdict型に変換
        dict = pd.read_excel(self.filepath, sheet_name=sheetname, skiprows=8, usecols=[1,12,13,14,15,16])
        # dict->DataFrame
        df = pd.DataFrame(dict)
        # DataFrameの列名変更
        df = df.set_axis(['primary_key','fieldname','datatype','default','length','digits'], axis='columns')
        # 欠損値置換
        df = df.fillna({'primary_key': 0, 'fieldname':'','datatype':'','default':'','length':0, 'digits':0})
        # 一部float型をint型に変換
        df['primary_key'] = df['primary_key'].astype(int)
        df['length'] = df['length'].astype(int)
        df['digits'] = df['digits'].astype(int)
        # DataFrameとして返す
        return df
    
    def put_modelPython(self, df:DataFrame, sheetname:str):
        
        """
        ModelをPythonファイルに出力
        
        Parameters
        ----------
        df : DataFrame
            対象DataFrame
        sheetname : str
            読込対象シート名
        """
        
        # 出力先パス取得
        output_dir = os.path.dirname(self.filepath)
        
        # pythonファイル出力
        with open(os.path.join(output_dir, sheetname + '.py'), 'w', newline='', encoding='utf-8') as f:
            f.writelines('import LibHanger.Models.fields as fld\n')
            f.writelines('from sqlalchemy.ext.declarative import declarative_base\n')
            f.writelines('from sqlalchemy.sql.elements import Null\n')
            f.writelines('\n')
            f.writelines('# Baseクラス生成\n')
            f.writelines('Base = declarative_base()\n')
            f.writelines('\n')
            f.writelines('class {0}(Base):'.format(sheetname) + '\n')
            f.writelines('\t\n')
            f.writelines('\t' + '# テーブル名\n')
            f.writelines('\t' + '__tablename__ = \'{0}\''.format(sheetname) + '\n')
            f.writelines('\t\n')
            f.writelines('\t' + '# 列定義\n')
            for index, row in df.iterrows():
                print('LineNo={0}'.format(index))
                outputRow = '\t'  + '{0} = fld.{1}({2})'.format(row['fieldname'],self.get_fieldType_val(row, 'method'), self.get_fieldType_args(row)) + '\n'
                f.writelines(outputRow)
        f.close()
        
    def get_fieldType_val(self, defRow, valType):
        
        """
        テーブル定義のデータ型に対応するColumnType取得
        
        Parameters
        ----------
        defRow : Any
            対象Series
        valType : Any
            データ型
        """
        
        fieldTypeVal:dict = self.fieldTypeMapPy.get(defRow['datatype'])
        return fieldTypeVal.get(valType)
        
    def get_fieldType_val(self, defRow):
        
        """
        テーブル定義のデータ型に対応するColumnType取得
        
        Parameters
        ----------
        defRow : Any
            対象Series
        valType : Any
            データ型
        """
        
        # 桁数指定があるかどうか
        fldType = ''
        if defRow['length'] != 0:
            fldLength = []
            fldLength.append(str(defRow['length']))
            if defRow['digits'] != 0:                
                fldLength.append(str(defRow['digits']))
            
            fldType = '\t {0}({1})'.format(defRow['datatype'], ','.join(fldLength))
        else:
            fldType = defRow['datatype']
            
        # デフォルト値指定があるかどうか
        if defRow['default'] != '' and str(defRow['default']).isdigit():
            fldType += ' DEFAULT {0}'.format(int(defRow['default']))
        
        # 改行付与
        fldType += '\n'
        
        return fldType
    
    def get_fieldType_args(self, defRow):
        
        """
        Columnクラスに渡すパラメーター取得
        
        Parameters
        ----------
        defRow : Any
            対象Series
        """

        # フィールドタイプ設定
        dataType:str = defRow['datatype']
        if dataType == 'varchar':
            length = [str(defRow['length'])]
            digits = str(defRow['digits']) if defRow['digits'] != 0 else ''
            if digits != '':
                length.append(digits)                
            fieldType = [Getter.getListMargeString(',', length)]
        elif dataType == 'numeric':
            length = [str(defRow['length']), str(defRow['digits']) if defRow['digits'] != '' else '0']
            fieldType = [Getter.getListMargeString(',', length)]
        else:
            fieldType = []

        # 主キー設定
        if defRow['primary_key'] != 0:
            primary_key = 'primary_key=True'
            fieldType.append(primary_key)
        # 既定値設定
        if defRow['default'] != None:
            
            # 既定値書式
            defaultFormat = 'default=\'{0}\'' if dataType == 'varchar' and defRow['default'] != 'NUL' else 'default={0}'
            
            # 既定値の値
            default = 'Null' if defRow['default'] == 'NUL' \
                 else '' if defRow['default'] == '' and dataType == 'varchar' \
                 else 'Null' if defRow['default'] == '' and dataType != 'varchar' \
                 else str(int(defRow['default']))
            fieldType.append(defaultFormat.format(default))
        return Getter.getListMargeString(',', fieldType)

    def get_TableListByDataFrame(self, sheetname:str):
        
        """
        テーブル一覧シートをDataFrameに変換
        
        Parameters
        ----------
        sheetname : str
            読込対象シート名
        """
        
        # シートをdict型に変換
        dict = pd.read_excel(self.filepath, sheet_name=sheetname, skiprows=5, usecols=[7,8])
        # dict->DataFrame
        df = pd.DataFrame(dict)
        # DataFrameの列名変更
        df = df.set_axis(['schema','tablename'], axis='columns')
        # 欠損値置換
        df = df.fillna({'schema': '', 'tablename':''})
        # DataFrameとして返す
        return df[df['tablename'] != '']
    
    def put_modelTableCreateSql(self, dfDef:DataFrame, dfTableList:DataFrame, sheetname:str):
        
        """
        ModelをTableCreateSQLファイルに出力
        
        Parameters
        ----------
        dfDef : DataFrame
            テーブル定義DataFrame
        dfTableList : DataFrame
            テーブル一覧DataFrame
        sheetname : str
            読込対象シート名
        """

        # 出力先パス取得
        output_dir = os.path.dirname(self.filepath)

        # スキーマ取得
        dfSchema = dfTableList[dfTableList['tablename'] == sheetname]
        schema = ''
        if len(dfSchema) > 0:
            schema = dfSchema.iloc[0]['schema']
        
        # 主キー列取得
        dfPrimary_key:pd.Series = dfDef[dfDef['primary_key'] !=0]['fieldname']
        primary_key = []
        if len(dfPrimary_key) > 0:
            primary_key = dfPrimary_key.values.tolist()         
        
        # SQLファイル出力
        with open(os.path.join(output_dir, sheetname + '.sql'), 'w', newline='', encoding='utf-8') as f:
            f.writelines('create table {0}.{1} ('.format(schema, sheetname) + '\n')
            for index, row in dfDef.iterrows():
                print('LineNo={0}'.format(index))
                comma = ' '
                if index > 0:
                    comma = ','
                outputRow = '\t{0}{1}\t{2}'.format(comma, str(row['fieldname']), self.get_fieldType_val(row))
                f.writelines(outputRow)
            f.writelines('\t' + ',PRIMARY KEY({0})'.format(','.join(primary_key)) + '\n')
            f.writelines(');' + '\n')
        f.close()