from pydantic import BaseModel


class Sth(BaseModel):
    # __slots__ = ('id', 'name')
    id: int = 0
    name: str = '123'


def ret_li():
    li = [{'id': 10, 'name': 'sdf'}, {'id': 20, 'name': 'qwe'}]
    return [Sth(**i) for i in li]


if __name__ == '__main__':
    sth_name_li = [i.name for i in ret_li()]
    print(sth_name_li)
    print(sth_name_li[0])
