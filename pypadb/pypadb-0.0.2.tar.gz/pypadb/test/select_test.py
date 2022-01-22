from pydantic import BaseModel

from conf.db_configurer import DbConfigurer
from decorator.select import select


class User(BaseModel):
    id: int
    account: str


@select('select * from user', data_type=User)
def get_sth_many() -> list[User]:
    pass


@select('select * from user where id = %(id)s', data_type=User)
def get_sth_one(id: int) -> User:
    pass


if __name__ == '__main__':
    # end() must be called
    DbConfigurer() \
        .set_host('localhost') \
        .set_user('root') \
        .set_password('123456') \
        .set_database('test') \
        .end()

    print(get_sth_many())
    # [User(...), User(...), ...]
    print(get_sth_one(1))
    # id=1 account='...'
