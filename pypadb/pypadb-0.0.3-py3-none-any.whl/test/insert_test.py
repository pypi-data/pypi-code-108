from typing import Optional

from pydantic import BaseModel

from conf.db_configurer import db_configurer
from conf.table_configurer import tables


class User(BaseModel):
    id: Optional[int]
    account: str
    stuffs: list = []


class Stuff(BaseModel):
    user_id: int
    name: str
    count: int


if __name__ == '__main__':
    db_configurer \
        .set_host('localhost') \
        .set_user('root') \
        .set_password('123456') \
        .set_database('test') \
        .end()
    tables.init_tables(user=User, stuff=Stuff)
    # tables.user.insert(User(id=None, account='czcz1'))
    tables.stuff.insert_batch([
        Stuff(user_id=1, name='232323', count=0),
        Stuff(user_id=2, name='343434', count=0)
    ])
