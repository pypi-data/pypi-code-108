
class iniFilePathError(Exception):

    """
    設定ファイル(config.ini)エラー例外
    """

    def __init__(self):

        """
        コンストラクタ
        """

        pass

    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "config.ini Not Found"