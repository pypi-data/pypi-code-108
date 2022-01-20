# mongo orm
# setup: 2 replica sets
# intialize table with primary and multiple secondary shards

# insert 10000 documents
# 1. verify all 10000 are split to shards
# 2. verify secondary shards are also updated for all 10000 documents

# update 100 documents
# 1. verify  updates are propagated to the secondary shards and are available for query

import blaster
import gevent
import random
from blaster.mongo_orm import Model, Attribute, INDEX, SHARD_BY, initialize_mongo
from blaster.common_funcs_and_datastructures import get_random_id, get_str_id


class AModel(Model):
    _collection_name_ = get_str_id()

    a = Attribute(int)
    b = Attribute(str)
    c = Attribute(str)
    d = Attribute(str)
    e = Attribute(str)
    f = Attribute(str)

    INDEX(
        (a, b),
        (b, c),
        (c, d),
        (c, d, e),
        (c, e)
    )
    SHARD_BY(primary=a, secondary=[b, c])


initialize_mongo([{"host": "localhost:27017"}, {"host": "localhost:27019"}], "test")


def create_entry(i):
    return AModel(a=i).commit()

# create an default
create_entry(0)


def make_table_changes(_by):
    item = AModel.get(a=0)
    item.b = (item.b or "") + _by
    item.f = (item.f or "") + _by
    # this should propagate b to secondary shard correctly
    item.commit()

    print(item.to_dict())
    for i in range(10):
        _i = random.randint(0, 9)
        item = AModel.get(a=_i)
        if(not item):
            item = create_entry(_i)
        item.b = (item.b or "") + _by
        item.c = (item.c or "") + _by
        item.d = (item.d or "") + _by
        item.e = (item.e or "") + _by
        item.f = (item.f or "") + _by
        item.commit()
        print(item.to_dict())


gevent.joinall([gevent.spawn(make_table_changes, str(i)) for i in range(10)])
