from easy_patents.get_info import app_progress
from easy_patents.errors import NoDocumentError, TooManyAccessError, ParameterError, UnknownError
import pandas as pd
from datetime import datetime, timedelta


def check_due_date(excel_path, sheet_name="Sheet1"):
    '''
    中間処理の対応状況を確認する
    最新の拒絶理由に対して、その後に意見書が提出されているかをチェックし、
    その状況をエクセルに記録する。

    Parameters
    ----------
    excel_path: str
        更新対象のエクセルのパス
    sheet_name: str or int
        シート名またはシート番号
    '''
    # 指定されたエクセルを読み出す
    #df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # インストールしたpandasのバージョンによっては、以下のようにencodingを指定する必要がある。
    df = pd.read_excel(excel_path,
            sheet_name=sheet_name, encoding="utf-8_sig")

    for index, row in df.iterrows():

        # データの初期化
        row['rejection_date'] = ''
        row['due_date'] = ''
        row['warning'] = ''
        row['opinion_submit_date'] = ''
        row['invention_title'] = ''

        # 読み込んだエクセルから出願番号を取得
        app_number = row['app_number']

        # 特許経過情報の取得
        try:
            progress_info_all = app_progress(app_number, reget_date=1)
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


        # ドキュメントから拒絶理由通知と意見書を抽出。
        rejection_list = []
        opinion_list = []
        for document in document_lists:
            if document['documentDescription'] == "拒絶理由通知書":
                rejection_list.append(document)
            if document['documentDescription'] == "意見書":
                opinion_list.append(document)

        # 拒絶理由がない場合には、次のループへ
        if len(rejection_list) == 0:
            continue

        # legalDateで並び替え
        sort_key = lambda x : x['legalDate']
        rejection_list.sort(key=sort_key)
        opinion_list.sort(key=sort_key)

        # 最新の拒絶理由を取得
        latest_rejection = rejection_list[-1]
        
        # 拒絶理由通知の日付を格納
        rejection_date = datetime.strptime(latest_rejection['legalDate'], "%Y%m%d")
        row['rejection_date'] = rejection_date

        # 応答期限を取得(暫定的に60日期限, 土日等の繰り越しなし)
        due_date = rejection_date + timedelta(days=60)
        row['due_date'] = due_date

        not_submitted_flag = True
        if len(opinion_list) != 0:
            latest_opinion = opinion_list[-1]
            opinion_date = datetime.strptime(latest_opinion['legalDate'], "%Y%m%d")
            # 意見書の日付が拒絶理由通知の日付より新しい場合に、
            # opinion_submit_dateに日付を記入
            # これ以外の場合には追記しない。
            if opinion_date > rejection_date:
                row['opinion_submit_date'] = opinion_date
                not_submitted_flag = False

        # 応答期限が今日から30日以内の場合には、あと〇日という警告を出力
        now = datetime.now()
        days_by_due_date = due_date - now
        if -1 < days_by_due_date.days <= 30 and not_submitted_flag:
            row['warning'] = "あと%s日" % days_by_due_date.days
        if 30 < days_by_due_date.days and not_submitted_flag:
            row['warning'] = "要対応"

        # データフレームの対象行を取得した情報でアップデート
        df.loc[index] = row

    # エクセルに反映
    #df.to_excel(excel_path,
    #        sheet_name=sheet_name, index=False)

    # インストールしたpandasのバージョンによっては、以下のようにencodingを指定する必要がある。
    df.to_excel(excel_path,
          sheet_name=sheet_name, index=False, encoding="utf-8_sig")


if __name__ == "__main__":
    import sys
    excel_path = sys.argv[1]
    sheet_name = sys.argv[2]
    check_due_date(excel_path, sheet_name)
