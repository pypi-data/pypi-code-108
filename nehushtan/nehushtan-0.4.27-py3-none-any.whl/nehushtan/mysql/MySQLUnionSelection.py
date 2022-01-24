from typing import List, Tuple

from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLSelectionMixin import MySQLSelectionMixin
from nehushtan.mysql.MySQLTableSelection import MySQLTableSelection


class MySQLUnionSeletion(MySQLSelectionMixin):
    """
    Since 0.3.6
    """

    def __init__(self):
        super().__init__()
        self.sub_selection_list: List[Tuple[MySQLTableSelection, str]] = []

    def get_mysql_kit(self) -> MySQLKit:
        """
        Just use the MySQLKit instance of the first sub selection
        """
        if len(self.sub_selection_list) <= 0:
            raise AssertionError('Sub Selection List should not be empty.')
        return self.sub_selection_list[0][0].get_mysql_kit()

    def add_sub_selection(self, sub_selection: MySQLTableSelection, use_all: bool = False):
        union_type = 'UNION'
        if use_all:
            union_type += ' ALL'
        self.sub_selection_list.append((sub_selection, union_type))
        return self

    def generate_sql(self) -> str:
        sqls = ''
        for i in range(len(self.sub_selection_list)):
            if i > 0:
                sqls += ' ' + self.sub_selection_list[i][1] + ' '
            sqls += self.sub_selection_list[i][0].generate_sql()
        return sqls
