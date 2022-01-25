import logging
import os
from .uwConfig import cmnConfig

def loggerDecorator(outputString, args_print = []):

    """
    関数の開始～終了でコンソールに文字列を出力するデコレーター
    """

    def _loggerDecorator(func):

        """
        関数の開始～終了でコンソールに文字列を出力するデコレーター
        """

        def  wrapper(*args, **kwargs):

            """
            デコレーターのラッパー
            """
            
            # 関数名の出力
            funcName = '({0}) ... Execute'.format(outputString)
            print(funcName)
            logging.info(funcName)

            # 引数の出力
            if len(args_print) > 0 and len(kwargs) > 0:
                for argsStr in args_print:
                    if kwargs.get(argsStr) == None : continue
                    argsValue = 'args:{0}={1}'.format(str(argsStr), str(kwargs.get(argsStr)))
                    print(argsValue)
                    logging.info(argsValue)

            try:
                # 関数本体の実行
                ret = func(*args, **kwargs)
                
                # 実行終了の出力
                funcEnded = '({0}) ... OK'.format(outputString)
                print(funcEnded)
                logging.info(funcEnded)

            except Exception as e:
                
                # 例外時エラーメッセージ
                errorInfo = '(' + outputString + ') ... ' + 'NG\n'\
                            '=== エラー内容 ===\n'\
                            'type:' + str(type(e)) + '\n'\
                            'args:' + str(e.args) + '\n'\
                            'e自身:' + str(e)

                # エラーメッセージの出力
                print(errorInfo)
                logging.error(errorInfo)

                return
            return ret

        return wrapper

    return _loggerDecorator

def setting(config: cmnConfig):

    """
    ロガー設定

    Parameters
    ----------
    config : cmnConfig
        共通設定クラス
    """

    # ログ出力先がない場合、作成する
    if os.path.exists(config.LogFolderName) == False:
        os.mkdir(config.LogFolderName)

    # ロガー設定
    logging.basicConfig(filename=os.path.join(config.LogFolderName, config.LogFileName),
                        level=config.LogLevel, 
                        format=config.LogFormat)
