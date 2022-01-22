from pydantic import BaseModel

from conf.db_configurer import db_configurer
from conf.table_configurer import tables
from utils.conditions import Like, Limit
from utils.enums import LikeEnum


class User(BaseModel):
    id: int
    account: str


class Stuff(BaseModel):
    name: str
    count: int


if __name__ == '__main__':
    db_configurer \
        .set_host('localhost') \
        .set_user('root') \
        .set_password('123456') \
        .set_database('test') \
        .end()
    # init tables
    tables.init_tables(user=User, stuff=Stuff)
    print(
        tables.user.select_many(limit=Limit(1))
    )
    # [User(id=1, account='123456')]
    print(
        tables.user.select_many(limit=Limit(0, 3))
    )
    # [User(id=1, account='123456'), User(id=2, account='123454563466'), User(id=3, account='12gsdfhs')]
    print(
        tables.user.select_like(likes=Like('account', '123', LikeEnum.R_Like))
    )
    # Like(column, value, like_mode)
    # argument likes: Union[list[Like], Like]
    # print result [User(id=1, account='123456'), User(id=2, account='123454563466')]
