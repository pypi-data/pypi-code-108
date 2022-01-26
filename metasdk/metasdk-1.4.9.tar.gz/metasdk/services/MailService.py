class MailService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}
        self.__data_get_cache = {}
        self.__metadb = app.db("meta")
        self.log = app.log

    def submit_mail(self, send_from, send_to, subject, body, unique_id=None):
        """
        Добавляем письмо в очередь на отправку
        :param send_from: Отправитель
        :param send_to: Получатель
        :param subject: Тема письма
        :param body: Тело письма. Можно с HTML
        :param unique_id: Уникальный идентификатор письма. Обычно что-то вроде md5 + человекочитаемый префикс подходят лучше всего. Письмо с одинаковым unique_id не будет добавлено
        """
        self.__metadb.update("""
        INSERT INTO meta.mail("template", "from", "to", "subject", "body", "attachments", "unique_id")
        VALUES ('meta', :send_from, :send_to, :subject, :body, null, :unique_id)
        ON CONFLICT (unique_id) DO NOTHING
        """, {
            "send_from": send_from,
            "send_to": send_to,
            "subject": subject,
            "body": body,
            "unique_id": unique_id
        })
