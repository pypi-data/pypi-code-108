"""
pyape.app.models.typeid
~~~~~~~~~~~~~~~~~~~

使用 typeid 定义
"""


class TypeID():
    # 保存初始化的 type
    # 0 默认状态，用于所有默认值，例如默认账号类型
    # 1-9 账户的状态
    # 10-49 特殊账户权限
    # 50-99 一般账户权限
    # 100-199 行为
    # 200-299 暂未使用
    # 300-399 数据库表 vo 的类型区分
    # 400-499 平台类型
    # 1001-xxxx 历史记录类型
    types = [
        (0, '默认', 'default'),
        (1, '可用', 'active'),
        (5, '锁定', 'lock'),
        (302, 'Token', 'Token Value Object'),
        (306, '频繁访问的配置', '不分类的需要频繁访问，写入内存缓存的配置'),
        (307, '通用配置', '通用配置，不区分类型'),
    ]

    typesdict = {}
    typesdictnamekey = {}

    @staticmethod
    def get_typesdict():
        if not TypeID.typesdict:
            for typeid, name, desc in TypeID.types:
                TypeID.typesdict[typeid] = {'typeid': typeid,
                                            'name': name, 'desc': desc}
        return TypeID.typesdict

    @staticmethod
    def get_typedict_namekey():
        if not TypeID.typesdictnamekey:
            for typeid, name, desc in TypeID.types:
                TypeID.typesdictnamekey[name] = {'typeid': typeid,
                                            'name': name, 'desc': desc}
        return TypeID.typesdictnamekey

    @staticmethod
    def get_type_byname(name):
        return TypeID.get_typedict_namekey().get(name)

    @staticmethod
    def get_type(typeid):
        return TypeID.get_typesdict().get(typeid)
