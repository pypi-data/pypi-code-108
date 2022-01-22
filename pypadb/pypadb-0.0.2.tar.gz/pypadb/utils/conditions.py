from utils.enums import LikeEnum


class Limit:
    __slots__ = ['start', 'count']

    start: int
    count: int

    def __init__(self, start: int, count: int = None):
        self.start = start
        self.count = count

    def __str__(self):
        if self.count is None:
            return f' limit {self.start}'
        return f' limit {self.start}, {self.count}'


class Like:
    __slots__ = ['sql', 'value', 'column']

    sql: str
    column: str
    value: str

    def __init__(self, column: str, value, like_type: LikeEnum):
        self.column = column
        self.value = value
        self.sql = f' {column} like'
        if like_type == LikeEnum.L_Like:
            self.sql += f' concat(\'%%\',%({column})s)'
        elif like_type == LikeEnum.R_Like:
            self.sql += f' concat(%({column})s,\'%%\')'
        elif like_type == LikeEnum.ALL_Like:
            self.sql += f' concat(\'%%\',%({column})s,\'%%\')'

    def __str__(self):
        return self.sql
