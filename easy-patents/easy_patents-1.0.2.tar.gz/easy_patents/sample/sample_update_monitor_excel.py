from easy_patents.get_info import app_progress
from easy_patents.errors import NoDocumentError, TooManyAccessError, ParameterError, UnknownError
import pandas as pd
from datetime import datetime


def update_monitor_excel(excel_path, sheet_name="Sheet1"):
    '''
    特許情報監視エクセルを更新する。

    Parameters
    ----------
    excel_path: str
        更新対象のエクセルのパス
    sheet_name: str or int
        シート名またはシート番号
    '''
    # 指定されたエクセルを読み出す
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # インストールしたpandasのバージョンによっては、以下のようにencodingを指定する必要がある。
    # df = pd.read_excel(excel_path,
    #         sheet_name=sheet_name, encoding="utf-8_sig")

    for index, row in df.iterrows():

        # 読み込んだエクセルから出願番号を取得
        app_number = row['app_number']

        # 特許経過情報の取得
        try:
            # reget_date=0とすることで、
            # コンピュータにファイルが保存されているかにかかわらず、
            # APIから最新の情報を取得する
            progress_info_all = app_progress(app_number, reget_date=0)
        except NoDocumentError:
            # 未公開情報などでドキュメントが取得できない場合にはスキップ
            continue
        except ParameterError as e:
            # パラメーターエラーの場合（出願番号の記載に誤りがあるような場合）には、
            # メッセージを出してスキップ
            print(e)
            continue
        except (TooManyAccessError, UnknownError) as e:
            # アクセス数超過、原因不明エラーの場合には
            # エラーメッセージを出力して終了
            print(e)
            break

        # 重要なデータのみ取り出し
        progress_info = progress_info_all['result']['data']

        # 発明の名称を設定
        row['invention_title'] = progress_info['inventionTitle']

        # bibliographyInformationの中には、
        # 複数のリストがあって処理がしずらいので、
        # 強引に1つにまとめる
        document_lists = []
        for binfo in progress_info['bibliographyInformation']:
            document_lists += binfo['documentList']

        # 最後の処理が最新の処理と推定して、最後の処理を取ってくる。
        last_progress = document_lists[-1]
        # 日付が8桁の整数であらわされているので、日付型に変換
        row['last_process_date'] = datetime.strptime(
                last_progress['legalDate'], "%Y%m%d")
        row['last_process'] = last_progress['documentDescription']

        # データフレームの対象行を取得した情報でアップデート
        df.loc[index] = row

    # エクセルに反映
    df.to_excel(excel_path,
            sheet_name=sheet_name, index=False)

    # インストールしたpandasのバージョンによっては、以下のようにencodingを指定する必要がある。
    # df.to_excel(excel_path,
    #        sheet_name=sheet_name, index=False, encoding="utf-8_sig")


if __name__ == "__main__":
    import sys
    excel_path = sys.argv[1]
    sheet_name = sys.argv[2]
    update_monitor_excel(excel_path, sheet_name)
