import tkinter as tk
from tkinter import filedialog

class baseDialog:
    
    """
    ダイアログボックスクラス基底
    """
    
    def unVisibleRootWindow(self):
        
        """
        RootWindowを非表示にする
        
        Parameters
        ----------
        None
        
        """
        
        root = tk.Tk()
        root.withdraw()

class uwFileDialog(baseDialog):
    
    """
    ファイルダイアログボックスクラス
    """
    
    class fileTypes:
        
        """
        ファイルタイプ
        """
        
        excelBook_xlsxOnly = [('Excel ブック','*.xlsx')]
        """xlsxファイルのみ"""
        
        excelBook = [('Excel ブック','*.xlsx *.xls')]
        """xlsxファイル,xlsファイル"""

        csv = [('CSV (コンマ区切り)','*.csv')]
        """csvファイル"""

        pdf = [('PDF','*.pdf')]
        """pdfファイル"""

        any = {('*', '*.*')}
        """全てのファイル"""
        
    def __init__(self) -> None:
        
        """
        コンストラクタ
        
        Parameters
        ----------
        None
        
        """
        
        super().__init__()
        
    def openFileDialog(self, fileType:fileTypes):
        
        """
        ファイルダイアログボックスを開く
        
        Parameters
        ----------
        fileType : fileTypes
            ファイル種類        
        """
        
        # ルートウィンドウ非表示
        self.unVisibleRootWindow()
        
        # ファイル参照ダイアログを開く
        return filedialog.askopenfilename(filetypes=fileType)

class uwFolderDialot(baseDialog):

    """
    フォルダダイアログボックスクラス
    """
    
    def openFolderDialog(self):
        
        """
        フォルダダイアログボックスを開く
        
        Parameters
        ----------
        None
        
        """
        
        # ルートウィンドウ非表示
        self.unVisibleRootWindow()

        # フォルダ参照ダイアログを開く
        return filedialog.askdirectory()