import tkinter as tk
from tkinter import messagebox

def confirmMessageDialog(message: str, title:str = ''):

    """
    確認ダイアログ表示

    Parameters
    ----------
    message : str
        メッセージ内容
    title : str
        ダイアログタイトル

    """

    # ルートウィンドウ非表示
    root = tk.Tk()
    root.withdraw()

    # 確認ダイアログ表示
    ret = messagebox.askyesno(title, message)
    
    # 選択値を返す
    return ret
