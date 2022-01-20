import base64
import datetime
import email
import imaplib
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import pytz


class MailClient():
    '''
    メールクライアントクラス。
    '''

    host_name = ''
    user_id = ''
    password  = ''


    def __init__(self, host_name, user_id, password):
        self.host_name = host_name
        self.user_id = user_id
        self.password = password


    def _get_header_text(self, msg:email.message.EmailMessage):
        '''
        ヘッダー部をまとめて文字列として返す。
        '''

        text = ''
        for key, value in msg.items():
            text = text + '{}: {}\n'.format(key, value)
        return text


    def _get_main_content(self, msg:email.message.EmailMessage):
        '''
        メール本文、フォーマット、キャラクターセットを取得する。
        '''

        try:
            body_part = msg.get_body()
            main_content = body_part.get_content()
            format_ = body_part.get_content_type()
            charset = body_part.get_content_charset()

        except Exception:
            main_content = 'Analysis failed.'
            format_ = 'Unknown'
            charset = 'Unknown'
            # get_bodyでエラーになるのは文字コード設定がおかしいメールを受信した場合なので、
            # decodeせずにテキスト部分をそのまま返す。
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    format_ = part.get_content_type()
                    main_content = str(part.get_payload())
                    charset = part.get_content_charset()

        return ( main_content, format_, charset )


    def _get_attachments(self, msg:email.message.EmailMessage):
        '''
        添付ファイルが存在する場合はBase64エンコードしてファイル名とともに返す。
        '''

        files = []
        for part in msg.iter_attachments():
            filename = part.get_filename()
            if not filename:
                continue

            # 添付ファイルをBase64エンコード
            file_obj_byte = base64.b64encode(part.get_payload(decode=True))
            file_obj_str = file_obj_byte.decode('utf-8')

            # ファイルオブジェクトとファイル名を保存
            files.append({'file_obj': file_obj_str, 'file_name': filename})

        return files


    def fetch_mail(self, search_option='UNSEEN', timezone='Asia/Tokyo'):
        '''
        メールを受信し、内容と添付ファイルの情報をJSON形式で返す。
        '''

        result = []

        # メールサーバーに接続
        cli = imaplib.IMAP4_SSL(self.host_name)

        try:
            # 認証
            cli.login(self.user_id, self.password)

            # メールボックスを選択（標準はINBOX）
            cli.select()

            # 指定されたオプションを用いてメッセージを検索
            status, data = cli.search(None, search_option)

            # 受信エラーの場合は空の結果を返して終了
            if status == 'NO':
                return result

            # メールの解析
            for num in data[0].split():
                status, data = cli.fetch(num, '(RFC822)')
                msg = BytesParser(policy=policy.default).parsebytes(data[0][1])
                msg_id = msg.get('Message-Id', failobj='')
                from_ = msg.get('From', failobj='')
                to_ = msg.get('To', failobj='')
                cc_ = msg.get('Cc', failobj='')
                subject = msg.get('Subject', failobj='')
                date_str = msg.get('Date', failobj='')
                date_time = parsedate_to_datetime(date_str)
                if date_time:
                    # タイムゾーンを補正
                    date_time = date_time.astimezone(pytz.timezone(timezone))
                date = date_time.strftime('%Y/%m/%d') if date_time else ''
                time = date_time.strftime('%H:%M:%S') if date_time else ''
                header_text = self._get_header_text(msg)
                body, format_, charset = self._get_main_content(msg)
                attachments = self._get_attachments(msg)
                mail_data = {}
                mail_data['msg_id'] = msg_id
                mail_data['header'] = header_text
                mail_data['from'] = from_
                mail_data['to'] = to_
                mail_data['cc'] = cc_
                mail_data['subject'] = subject
                mail_data['date'] = date
                mail_data['time'] = time
                mail_data['format'] = format_
                mail_data['charset'] = charset
                mail_data['body'] = body
                mail_data['attachments'] = attachments
                result.append(mail_data)

            return result

        finally:
            cli.close()
            cli.logout()


    def delete_mail(self, days=90):
        '''
        メールを検索し、対象のメッセージをメールサーバーから削除する。
        '''

        delete_count = 0

        # 検索条件の生成
        target_date = datetime.datetime.now() - datetime.timedelta(days=days)
        search_option = target_date.strftime('BEFORE %d-%b-%Y')

        # メールサーバーに接続
        cli = imaplib.IMAP4_SSL(self.host_name)

        try:
            # 認証
            cli.login(self.user_id, self.password)

            # メールボックスを選択（標準はINBOX）
            cli.select()

            # 指定されたオプションを用いてメッセージを検索
            status, data = cli.search(None, search_option)

            # 受信エラーの場合はエラーを返して終了
            if status == 'NO':
                return delete_count

            # 対象メッセージの削除
            for num in data[0].split():
                cli.store(num, '+FLAGS', '\\Deleted')
                delete_count = delete_count + 1
            cli.expunge()

            return delete_count

        finally:
            cli.close()
            cli.logout()
