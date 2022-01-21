# coding=utf-8
"""权限"""
import logging
import time, random
from bson.objectid import ObjectId
from lcyframe.libs.singleton import MongoCon
from lcyframe.libs import errors


class Permission(object):
    PERMISSION_TABLE = "permission_group"
    PERMISSION_CLASS_TABLE = "permission_class"

    CURRENT_PERMISSION_GROUP = None
    CURRENT_PERMISSION_CLASS = None
    __VERSION__ = 0
    MAX_NUMS = 63
    IS_DEBUG = False
    default_group_config = None
    default_class_config = None
    mongo = MongoCon._database

    @classmethod
    def initial(cls):
        if cls.mongo is None:
            cls.mongo = MongoCon._database
            if cls.mongo is None:
                raise Exception("you must get a mongo isinstance!")

        if cls.CURRENT_PERMISSION_GROUP is None:
            cls.__load_permission_group()
        if cls.CURRENT_PERMISSION_CLASS is None:
            cls.__load_permission_class()

        return cls

    @classmethod
    def bit_mp_obj(cls, name, sort, available=True):
        return {"name": name,
                "sort": sort,
                "desc": "",
                "available": available}

    @classmethod
    def gen_bit_mp(cls, nums):
        """
        生成位权限对象
        :param nums:  权限位数
        :return:
        """
        nums = max(nums, cls.MAX_NUMS)

        bit_mp = {}
        for i in range(nums):
            bit_mp[str(i)] = cls.bit_mp_obj("权限%s" % i, i)
        return bit_mp

    @classmethod
    def gen_class_obj(cls, k, nums=MAX_NUMS):
        """
        生成权限类别
        :return:
        """
        return {
            "_id": str(ObjectId()),
            "key": int(k),
            "available": True,
            "name": "权限类别:%s" % str(k),
            "bit_mp": cls.gen_bit_mp(nums),
            "create_at": int(time.time()),
            "desc": ""
        }

    @classmethod
    def gen_permission_class(cls, *class_obj, **kwargs):
        """
        生成多个权限类别和权限
        "config": [
                {
                "_id": "f3245d",
                "key": 1,   # 主键
                "available": True,
                "name": "用户管理权限类",
                "bit_mp": {
                    "0": {"name": "可创建用户", "available": True},   # 0位
                    "1": {"name": "可创建用户", "available": True},   # 1位
                    ...,
                    "62": {"name": "可创建用户", "available": True}   # 63位
                },
                ...
        ]
        :param ids:  权限类别ids
        :param nums:  小于64  每个类别最多可设置63种权限
        :return:
        """
        class_obj = class_obj or cls.default_class_config

        d = []

        if class_obj:
            if cls.mongo[cls.PERMISSION_CLASS_TABLE].find_one():
                raise Exception("the permission class is exists, you can create new obj.")

            if not cls.check_permission_class(class_obj):
                raise Exception("the permission config is error.")

            for _class in class_obj:
                _class.setdefault("_id", str(ObjectId()))
                d.append(_class)
        else:
            for k, key in enumerate(kwargs["keys"]):
                d.append(cls.gen_class_obj(k + 1, kwargs.get("nums", cls.MAX_NUMS)))

        cls.mongo[cls.PERMISSION_CLASS_TABLE].insert(d)
        return d

    @classmethod
    def gen_perminssion_group(cls, config=None):
        """
        角色组配置表
        :param config:  [
                            {
                                "gid": 1,   # 权限组ID，大小与父子关系没有必然联系
                                "pid": 1,   # 父子关系，1 > 2 > 3，值越小层级越高
                                "available": True,
                                "name": "角色组1",
                                "permission_class": {
                                        "0": 13243,   # 权限类key=xxx拥有的权限值为13243,
                                        "1": 54432,   # 权限类key=yyy拥有的权限值为13243
                                }
                            },
                            ...
                            {
                                "gid": 2,   # 权限组ID，大小与父子关系没有必然联系
                                "pid": 2,   # 父子关系，1 > 2 > 3，值越小层级越高
                                "available": True,
                                "name": "角色组5",
                                "permission_class": {
                                        "0": 13243,   # 权限类key=xxx拥有的权限值为13243,
                                        "1": 54432,   # 权限类key=xxx拥有的权限值为13243
                                }
                            }
                        ]
        :return:
        """
        config = config or cls.default_group_config
        if config and not cls.check_permission_group(config):
            return False

        if not config:
            permission_group_list = []
            classes = cls.gen_permission_class(keys=[ObjectId(), ObjectId()])
            permission_class = {}
            for g in classes:
                permission_class[str(g["key"])] = 0

            for i in range(1, 6):
                permission_group_list.append({
                    "_id": str(ObjectId()),
                    "gid": i,
                    "pid": i,
                    "available": True,
                    "name": "角色%d" % i,
                    "permission_class": permission_class,
                    "create_at": int(time.time()),
                    "desc": ""
                }
                )

            config = permission_group_list

        cls.mongo[cls.PERMISSION_TABLE].insert(config)
        return config

    @classmethod
    def check_permission_group(cls, group):
        """检测角色组配置文件
        {
            "gid": 1,
            "available": True,
            "name": "角色组1",
            "permission_class": {
                    "1": 13243,   # 权限类key=xxx拥有的权限值为13243,
                    "2": 54432,   # 权限类key=yyy拥有的权限值为13243
            }
        }
        """

        if not isinstance(group, list):
            group = [group]

        for g in group:
            try:
                assert type(g["gid"]) == int
                assert type(g["available"]) == bool
                assert type(g["name"]) in [str, unicode]
                assert type(g["desc"]) in [str, unicode]
                assert type(g["permission_class"]) == dict
                for k, v in g["permission_class"].items():
                    assert type(k) == str
                    assert type(v) == int
                return True
            except:
                return False

    @classmethod
    def check_permission_class(cls, _class):
        """检测权限类配置文件
        {
            "_id": "f3245d",
            "key": "1",   # 主键
            "available": True,
            "name": "用户管理权限类",
            "bit_mp": {
                "0": {"name": "可创建用户", "available": True},   # 0位
                "1": {"name": "可创建用户", "available": True},   # 1位
                ...,
                "62": {"name": "可创建用户", "available": True}   # 63位
            }
        """

        if type(_class) not in (tuple, list):
            _class = [_class]

        for g in _class:
            try:
                if "_id" in g:
                    assert type(g["_id"]) == str

                assert type(g["key"]) == int
                assert type(g["name"]) in [str, unicode]
                assert type(g["desc"]) in [str, unicode]
                assert type(g["bit_mp"]) == dict
                for k, v in g["bit_mp"].items():
                    assert int(k) >= 0 and int(k) <= cls.MAX_NUMS
                    assert type(v) == dict
                return True
            except:
                return False

    @classmethod
    def __load_permission_group(cls):
        """载入角色组"""
        mp = {"group": {}, "parent": {}}

        group = list(cls.mongo[cls.PERMISSION_TABLE].find())

        if not group:
            group = cls.gen_perminssion_group()

        for g in group:
            g.pop("_id", None)
            mp["group"][int(g["gid"])] = g  # 角色组mp
            mp["parent"][int(g["pid"])] = g  # 父子组mp， 获取某个gid的父级角色时使用

        cls.CURRENT_PERMISSION_GROUP = mp
        return cls.CURRENT_PERMISSION_GROUP

    @classmethod
    def __load_permission_class(cls):
        """载入可用的权限类别
        """
        mp = {}

        classes = list(cls.mongo[cls.PERMISSION_CLASS_TABLE].find())

        if not classes:
            classes = cls.gen_permission_class()

        for c in classes:
            mp[int(c["key"])] = c

        cls.CURRENT_PERMISSION_CLASS = mp

        return cls.CURRENT_PERMISSION_CLASS

    @classmethod
    def get_permission_group(cls, gid=None):
        """获取一个或所有角色组"""
        if not cls.CURRENT_PERMISSION_GROUP:
            cls.__load_permission_group()

        if gid is None:
            return cls.CURRENT_PERMISSION_GROUP or {}
        else:
            return cls.CURRENT_PERMISSION_GROUP["group"][int(gid)]

    @classmethod
    def get_permission_class(cls, class_key=None):
        """
        获取一个或所有权限类别
        :param class_key:
        :return:
        """
        if not cls.CURRENT_PERMISSION_CLASS:
            cls.__load_permission_class()

        if class_key is None:
            return cls.CURRENT_PERMISSION_CLASS
        else:
            return cls.CURRENT_PERMISSION_CLASS[int(class_key)]

    @classmethod
    def create_group(cls, **group):
        """
        创建一个新的角色组
        :param group: 提供配置文件
        :param parent_gid:   指定父角色，在其后面添加下级角色
        :return:
        """

        parent_pid = group.pop("parent_pid", None)
        if parent_pid == 0:
            return False

        max_gid = 0
        max_pid = 0
        for g in cls.mongo[cls.PERMISSION_TABLE].find():
            if g["gid"] > max_gid:
                max_gid = g["gid"]
            if g["pid"] > max_pid:
                max_pid = g["pid"]

        new_gid = max_gid + 1
        new_pid = max_pid + 1

        if parent_pid is not None:
            new_pid = parent_pid + 1
            cls.mongo[cls.PERMISSION_TABLE].update({"pid": {"$gte": parent_pid + 1}}, {"$inc": {"pid": 1}}, multi=True)

        group["_id"] = str(ObjectId())
        group["available"] = True
        group["gid"] = new_gid  # 权限组ID，大小与父子关系没有必然联系
        group["pid"] = new_pid  # 父子关系，1 > 2 > 3，值越小层级越高
        group["permission_class"] = group.get("permission_class", {})
        group["create_at"] = int(time.time())

        if not cls.check_permission_group(group):
            raise Exception("group config is error.")

        cls.mongo[cls.PERMISSION_TABLE].insert(group)
        cls.__load_permission_group()

        return group

    @classmethod
    def copy_group(cls, copy_gid):
        """
        复制指定的角色组并创建
        :param copy_gid:
        :return:
        """
        copy_group = cls.CURRENT_PERMISSION_GROUP["group"][copy_gid]
        new_group = cls.create_group(**copy_group)
        cls.__load_permission_group()
        return new_group

    @classmethod
    def add_class2group(cls, gid, **kwargs):
        """
        给某个角色组加上一个权限类别
        :param kwargs: {"1": 23}
        :param gid:
        :return:
        """
        s = {}
        for class_key, mask in kwargs.items():
            s["permission_class.%s" % int(class_key)] = int(mask)

        cls.mongo[cls.PERMISSION_TABLE].update({"gid": gid}, {"$set": s})
        cls.__load_permission_group()
        cls.__load_permission_class()

    @classmethod
    def create_class(cls, _class=None, nums=MAX_NUMS):
        """
        创建新的权限类
        :param _class:  权限类对象
        :param nums:  bit 权限位数
        :return:
        """
        if _class and not cls.check_permission_class(_class):
            return False

        if _class and cls.mongo[cls.PERMISSION_CLASS_TABLE].find_one({"key": int(_class["key"])}):
            return False

        if not _class:
            key = cls.mongo[cls.PERMISSION_CLASS_TABLE].find().sort("key", -1)[0]["key"]
            _class = cls.gen_class_obj(key + 1, nums)

        _class.setdefault("_id", str(ObjectId()))
        cls.mongo[cls.PERMISSION_CLASS_TABLE].insert(_class)

        _class.pop("_id", None)
        cls.__load_permission_class()
        return _class

    @classmethod
    def create_bit(cls, class_key, name):
        """
        生成新的权限位
        :param class_key:
        :param name:
        :return:
        """
        if cls.CURRENT_PERMISSION_CLASS is None:
            raise Exception("permission class is None, you must load it.")

        permission_class = cls.CURRENT_PERMISSION_CLASS[int(class_key)]

        bit_mp = permission_class["bit_mp"]

        if len(bit_mp) >= cls.MAX_NUMS:
            raise Exception("permission class bit nums must <= %d." % cls.MAX_NUMS)

        max_bit = 0
        max_sort = 0
        for k, item in bit_mp.items():
            if int(k) > max_bit:
                max_bit = int(k)
            if item["sort"] > max_sort:
                max_sort = item["sort"]

        max_bit += 1
        max_sort += 1
        if max_bit >= cls.MAX_NUMS:
            raise Exception("permission class bit nums must <= %d." % cls.MAX_NUMS)

        new_bit = cls.bit_mp_obj(name, max_sort)
        cls.mongo[cls.PERMISSION_CLASS_TABLE].update({"key": int(class_key)},
                                                  {"$set": {"bit_mp.%d" % max_bit: new_bit}})
        cls.__load_permission_class()

        return new_bit

    @classmethod
    def update_group_name(cls, gid, new_name):
        """
        更新用户组名称，但是特性不能改，如果与原有特性不一样，需要配合修改以用于判断的代码
        TODO 原则上不推荐修改
        :param gid:
        :param new_name:
        :return:
        """
        if gid not in cls.CURRENT_PERMISSION_GROUP["group"]:
            raise errors.ErrorInvalid("不存在该角色")

        for g in cls.CURRENT_PERMISSION_GROUP["group"].values():
            if g["name"].encode("u8") == new_name:
                return

        cls.mongo[cls.PERMISSION_TABLE].update({"gid": int(gid)}, {"$set": {"name": new_name}})
        return cls.__load_permission_group()

    @classmethod
    def update_group_available(cls, gid, available):
        """
        更新用户组名称
        TODO 原则上不推荐修改
        :param gid:
        :param new_name:
        :return:
        """
        if type(available) is not bool:
            return

        cls.mongo[cls.PERMISSION_TABLE].update({"gid": int(gid)}, {"$set": {"available": available}})
        cls.__load_permission_group()

    @classmethod
    def update_class_name(cls, class_key, new_name):
        """修改权限类名
        TODO 原则上不推荐修改
        """
        if class_key not in cls.CURRENT_PERMISSION_CLASS[class_key]:
            raise errors.ErrorInvalid("不存在该权限类")

        if cls.mongo[cls.PERMISSION_CLASS_TABLE].find_one({"name": new_name}):
            return False

        cls.mongo[cls.PERMISSION_CLASS_TABLE].update({"key": int(class_key)}, {"$set": {"name": new_name}})
        return cls.__load_permission_class()

    @classmethod
    def update_class_available(cls, class_key, available):
        """修改权限类可用
        TODO 原则上不推荐修改
        """
        cls.mongo[cls.PERMISSION_CLASS_TABLE].update({"key": int(class_key)}, {"$set": {"available": bool(available)}})
        return cls.__load_permission_class()

    @classmethod
    def update_bit_name(cls, class_key, bit, new_name):
        """修改单个权限位的权限名
        注意：权限如果被修改了，所有使用过该位的地方都要跟着改
        TODO 原则上不推荐修改
        """
        if class_key not in cls.CURRENT_PERMISSION_CLASS:
            raise errors.ErrorInvalid("不存在该权限类")
        if str(bit) not in cls.CURRENT_PERMISSION_CLASS[class_key]["bit_mp"]:
            raise errors.ErrorInvalid("不存在该权限")

        for c in cls.mongo[cls.PERMISSION_CLASS_TABLE].find():
            for b, name in c["bit_mp"].items():
                if name["name"].encode("u8") == new_name:
                    return

        cls.mongo[cls.PERMISSION_CLASS_TABLE].update({"key": int(class_key)},
                                                  {"$set": {"bit_mp.%s.name" % str(bit): new_name}})
        return cls.__load_permission_class()

    @classmethod
    def update_batch_bit_name(cls, class_key, **kwargs):
        """
        修改多个权限位的权限名,支持同时修改多个权限位
        注意：权限如果被修改了，所有使用过该位的地方都要跟着改
        TODO 原则上不推荐修改
        :param class_key:
        :param kwargs: {"0": {"available": True, "name": "新权限名"},
                        "1": {"name": "新权限名"},
                        "2": {"available": True}
                    }
        :return:
        """
        s = {}

        for k, v in kwargs.items():
            if not v:
                continue
            if "available" in v:
                s["bit_mp.%s.available" % str(k)] = v["available"]

            if "name" in v and v["name"]:
                s["bit_mp.%s.name" % str(k)] = v["name"]

        if s:
            cls.mongo[cls.PERMISSION_CLASS_TABLE].update({"key": int(class_key)}, {"$set": s})
            return cls.__load_permission_class()

    @classmethod
    def update_bit_available(cls, class_key, bit, available):
        """修改权限位可用
        TODO 原则上不推荐修改
        """
        cls.mongo[cls.PERMISSION_CLASS_TABLE].update({"key": int(class_key)},
                                                  {"$set": {"bit_mp.%s.available" % str(bit): bool(available)}})
        return cls.__load_permission_class()

    @classmethod
    def update_permission(cls, gid, class_key, **bits):
        """
        按单个角色组修改权限位值
        :param gid:  角色组ID
        :param class_key: 权限组类
        :param bits: 权限位，{"0": True/1, "1": False/0, "54": True/1}
        :return:
        """
        if int(gid) not in cls.CURRENT_PERMISSION_GROUP["group"]:
            raise errors.ErrorInvalid("不存在该角色")

        ts = int(time.time())
        # cls.mongo[cls.PERMISSION_TABLE].update({"gid": gid}, {"$bit": {"i": {"xor": 1}}})
        mask = cls.mongo[cls.PERMISSION_TABLE].find_one({"gid": int(gid)})["permission_class"][str(class_key)]
        new_mask = mask

        for k, v in bits.items():
            if type(v) in [None, bool]:
                v = v == True
            else:
                v = int(v) if v.isdigit() else v == True

            if not mask & 1 << int(k) and v:  # 勾选权限
                new_mask += 1 << int(k)
            elif mask & 1 << int(k) and not v:  # 取消权限
                new_mask -= 1 << int(k)

        if new_mask != mask:
            cls.mongo[cls.PERMISSION_TABLE].update({"gid": int(gid)}, {
                "$set": {"permission_class.%s" % str(class_key): new_mask, "update_at": ts}})
            cls.reload()
        return new_mask

    @classmethod
    def update_batch_permission(cls, **kwargs):
        """
        按多个角色组修改权限位值
        :param kwargs: {"1": {"1": {"0": 1, "1": 1}, "2": ..}, "2": {..}}
        :param gid:  角色组ID
        :param class_key: 权限组类
        :param bits: 权限位，{"0": True/1, "1": False/0, "54": True/1}
        :return:
        """
        for gid, permission_class_mp in kwargs.items():
            for class_key, bits in permission_class_mp.items():
                cls.update_permission(gid, class_key, **bits)
        cls.reload()
        return cls.CURRENT_PERMISSION_GROUP["group"]

    @classmethod
    def get_parent_group(cls, gid):
        """获取上级角色组，"""
        parent_group = {}
        me_pid = cls.CURRENT_PERMISSION_GROUP["group"][int(gid)]["pid"]
        for pid, g in cls.CURRENT_PERMISSION_GROUP["parent"].items():
            # 角色组可以被删除，所以有可能上级不是pid-1,而是pid-2,
            if pid >= me_pid:
                continue
            if g["available"] is not True:
                continue

            parent_group = g

        return parent_group

    @classmethod
    def get_parent_groups(cls, gid):
        """获取所有直系父级、父父级、叔父级"""
        parent_groups = []
        parent_group = cls.get_parent_group(gid)

        if parent_group:
            parent_groups.append(parent_group)

            # 叔父
            brother_groups = cls.get_brother_groups(parent_group["gid"])
            if brother_groups:
                parent_groups += brother_groups

            parent_gid = str(parent_group.get("pid"))
            if str(parent_gid) in cls.CURRENT_PERMISSION_GROUP["group"] and str(parent_gid) != str(parent_group["gid"]):
                parent_groups.extend(cls.get_parent_groups(parent_group["gid"]))

        return cls.parse_ppid_groups(*parent_groups)

    @classmethod
    def get_brother_groups(cls, gid):
        """
        获取gid的兄弟角色
        :param gid:
        :return:
        """
        brother_groups = []
        group = cls.CURRENT_PERMISSION_GROUP["group"][int(gid)]
        parent_gid = group.get("pid")
        if parent_gid == group["gid"]:
            return brother_groups

        for gid, item in cls.CURRENT_PERMISSION_GROUP["group"].items():
            if gid == group["gid"]:
                continue
            if str(item["gid"]) != str(group["gid"]) and item.get("pid") == parent_gid and item["available"] == 1:
                brother_groups.append(item)

        return brother_groups

    @classmethod
    def get_child_group(cls, gid):
        """获取下级角色组"""
        parent_group = {}
        me_pid = cls.CURRENT_PERMISSION_GROUP["group"][int(gid)]["pid"]
        for pid, g in cls.CURRENT_PERMISSION_GROUP["parent"].items():
            # 角色组可以被删除，所以有可能上级不是pid+1,而是pid+2
            if pid <= me_pid:
                continue
            if g["available"] is not True:
                continue

            parent_group = g

        return parent_group

    @classmethod
    def get_child_groups(cls, gid):
        """获取直系子孙级"""
        child_groups = []
        child_group_list = cls.get_child_group(gid)
        child_groups.extend(child_group_list)
        for child in child_group_list:
            child_groups.extend(cls.get_child_groups(child["gid"]))

        s = []
        for child in child_groups:
            if child["available"] != 1:
                continue
            s.append(child)
        return s

    @classmethod
    def get_group_name(cls, gid):
        """用户组->名称"""
        group_permission = cls.CURRENT_PERMISSION_GROUP["group"][int(gid)]
        return group_permission["name"]

    @classmethod
    def is_parent_group(cls, gid, parent_gid):
        """
        判断是否是上级角色
        :param parent_gid:
        :return:
        """
        step = 1
        group_mp = cls.CURRENT_PERMISSION_GROUP["group"]
        parent_mp = cls.CURRENT_PERMISSION_GROUP["parent"]

        pid = group_mp[int(gid)]["pid"]
        parent_pid = group_mp[parent_gid]["pid"]

        if pid <= parent_gid:
            return False

        keys = parent_mp.keys()
        keys.sort(reverse=True)
        for k in keys:
            if k >= pid:
                continue

            group = parent_mp[k]

            # 相邻多个上级被禁用，不算
            if group["available"] == False:
                continue
            else:
                if group["pid"] != parent_pid:
                    step += 1
                else:
                    break

        return step == 1

    @classmethod
    def is_child_group(cls, gid, child_gid):
        """
        判断是否是下级角色
        :param parent_gid:
        :return:
        """

        step = 1
        group_mp = cls.CURRENT_PERMISSION_GROUP["group"]
        child_mp = cls.CURRENT_PERMISSION_GROUP["parent"]

        pid = group_mp[int(gid)]["pid"]
        child_gid = group_mp[str(child_gid)]["pid"]

        if pid >= child_gid:
            return False

        keys = child_mp.keys()
        keys.sort()
        for k in keys:
            if k <= pid:
                continue

            group = child_mp[k]

            # 相邻多个下级被禁用，不算
            if group["available"] == False:
                continue
            else:
                if group["pid"] != child_gid:
                    step += 1
                else:
                    break

        return step == 1

    @classmethod
    def reload(cls):
        """修改权限设置后,更新mp"""
        cls.CURRENT_PERMISSION_GROUP = None
        cls.CURRENT_PERMISSION_CLASS = None
        cls.__load_permission_group()
        cls.__load_permission_class()
        cls.permission_changed()

    @classmethod
    def check_permission(cls, gid, class_key, permission):
        """检测用户所在的组 是否有某个权限
        :param mask: 当前的权限设定
        :param permission: 需要判断是否有这个权限 xxxxx_PERMISSION 2的n阶数 多个不同权限可以相加, 检测是否同时拥有多个权限
        ANONYMOUS_PERMISSION = 0
        """

        if cls.IS_DEBUG:
            return True

        # 非必要,为了效率
        if permission == 0:
            return True

        group_permission = cls.get_permission_group(gid)

        if group_permission["available"] is False:
            return True

        mask = group_permission["permission_class"].get(str(class_key), 0)

        return mask & permission == permission

    @classmethod
    def crontab_update(cls):
        """检测是否需要更新"""
        last_version = int(cls.redis.get(PERMISSION_VERSION_CACHE_KEY) or -1)
        if cls.__VERSION__ == last_version:
            return False

        logging.debug("crontab_update: true")
        cls.reload()
        cls.__VERSION__ = last_version
        return True

    @classmethod
    def permission_changed(cls):
        pass
        # cls.__VERSION__ = int(cls.redis.incrby(PERMISSION_VERSION_CACHE_KEY, 1))

    @classmethod
    def test(cls):
        print("======所有角色组=======")
        print(cls.get_permission_group())
        print
        print("======角色组1=======")
        print(cls.get_permission_group(1))
        print
        print("======所有权限类别=======")
        print(cls.get_permission_class())


