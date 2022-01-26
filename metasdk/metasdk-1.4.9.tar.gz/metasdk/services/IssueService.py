class IssueService:

    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}
        self.__data_get_cache = {}
        self.__metadb = app.db("meta")

    def change_issue_status(self, issue_id, status_id: str):
        """
        Смета статуса тикета
        :param issue_id: int
        :param status_id: int
        """
        self.__metadb.update("""
              update meta.issue set 
                issue_status_id=:status_id,
                assignee_user_id=valera_user_id(),
                last_user_id=valera_user_id()
              where id = :issue_id
        """, {"issue_id": issue_id, "status_id": status_id})

    def pending_issue(self, issue_id):
        """
        Перевести в статус "В ожидании"
        :param issue_id: int
        """
        self.change_issue_status(issue_id, '1')

    def in_progress_issue(self, issue_id):
        """
        Взять в работу
        :param issue_id: int
        """
        self.change_issue_status(issue_id, '2')

    def reject_issue(self, issue_id):
        """
        Отклонить задачу
        :param issue_id: int
        """
        self.change_issue_status(issue_id, '7')

    def clarification_issue(self, issue_id):
        """
        Уточнение
        :param issue_id: int
        """
        self.change_issue_status(issue_id, '4')

    def done_issue(self, issue_id):
        """
        Успешное выполенение
        :param issue_id: int
        """
        self.change_issue_status(issue_id, '3')

    def add_issue_msg(self, issue_id, msg):
        self.__metadb.update("""
            INSERT INTO meta.issue_msg (msg, issue_id, user_id, last_user_id)
            VALUES (:msg, :issue_id, valera_user_id(), valera_user_id())
        """, {"issue_id": issue_id, "msg": msg})
