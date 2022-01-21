#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseModel
from model.schema.permission_schema import PermissionClassSchema, PermissionGroupSchema
import copy, xlrd

class PermissionModel(BaseModel, PermissionGroupSchema):
    """
        权限
        Example:

            ::: assert self.model.PermissionModel.has_permission(gid, class_key, *[class_bit])

            1、******，******：
            assert self.model.PermissionModel.has_permission(account_info.get('gid'), 9, *[10, 11])
            2、******，******
            assert self.model.PermissionModel.has_permissions(account_info.get('gid'), [(9, 10), (3, 2), (3, 4)])

    """

    @classmethod
    def has_permission(cls, gid, class_key, *bits):
        """
        ******
        :param gid:
        :param class_key:
        :param bits: [1, 2, ..] ******
        :return:
        """
        permission = 0

        if not isinstance(bits, list):
            bits = list(bits)

        for bit in bits:
            permission += 2 ** int(bit)

        if not gid or not cls.Permission.check_permission(gid, class_key, permission):
            raise cls.api_error.ErrorNoApiPermission(u"******")
        else:
            return True

    @classmethod
    def is_has_permission(cls, gid, class_key, *bits):
        """
        ******

        :param gid:
        :param class_key:
        :param bits: [1, 2, ..] ******
        :return: True or False
        """
        permission = 0

        if not isinstance(bits, list):
            bits = list(bits)

        for bit in bits:
            permission += 2 ** int(bit)

        if not gid or not cls.Permission.check_permission(gid, class_key, permission):
            return False
        else:
            return True

    @classmethod
    def has_permissions(cls, gid, class_list):
        """
        ******
        :param gid:
        :param class_list: [(class_key, bit),(class_key, bit)]
        :return:
        """
        exception_num = 0
        for i in class_list:
            class_key, bit = i
            try:
                cls.has_permission(gid, class_key, bit)
            except cls.api_error.ErrorNoApiPermission as e:
                exception_num += 1
                continue
        if len(class_list) == exception_num:
            raise cls.api_error.ErrorNoApiPermission
        else:
            return True

    @classmethod
    def get_permission(cls, gid):
        """******"""

        me_group = {}

        permission_class = copy.deepcopy(cls.Permission.CURRENT_PERMISSION_CLASS)
        permission_group = copy.deepcopy(cls.Permission.CURRENT_PERMISSION_GROUP['group'])

        if gid not in permission_group:
            raise cls.api_error.ErrorInvalid("******")

        for group in cls.bit2mp(permission_group, permission_class):
            if int(gid) != group["gid"]:
                continue

            me_group = group
            break

        # TODO ******“1”******
        me_group["permission_class"] = me_group["permission_class"]
        return me_group

    @classmethod
    def get_current_permission(cls):
        """
        ******
        :param gid:
        :param pid:
        :return:
        """

        permission_class = copy.deepcopy(cls.Permission.CURRENT_PERMISSION_CLASS)
        permission_group = copy.deepcopy(cls.Permission.CURRENT_PERMISSION_GROUP['group'])

        d = {"current_permission": cls.bit2mp(permission_group, permission_class),
             "permission_group": cls.get_groups(copy.deepcopy(permission_group).values()),
             "permission_class": copy.deepcopy(permission_class)
             }

        # TODO ******“1”******
        for k, value in d.items():
            if k == "current_permission":
                for item in value:
                    item["bit_mp"] = item["bit_mp"]

            if k == "permission_class":
                d[k] = value[1]
                d[k]["bit_mp"] = sorted(d[k]["bit_mp"].values(), key=lambda o: o["bit"])
        return d

    @classmethod
    def bit2mp(cls, permission_group, permission_class):
        """
        ******
        ******
        {
            u'available': 1,
            u'name': u'xxx',
            u'pid': 1,
            u'create_at': 1513590899,
            u'gid': 1
            u'permission_class': {"1": {"0": 1, "1": 0, ...},
                                  "2": {"0": 1, "1": 0, ...},
                                  ...
                                },
        }
        """
        new_permission_group = []

        for gid, group in permission_group.items():

            tmp_permission_class = []
            for k, mask in group.get("permission_class", {}).items():

                # TODO ******1
                if int(k) > 1:
                    continue

                tmp_bit_mp = []
                for bit, item in permission_class[int(k)]["bit_mp"].items():
                    item["class_key"] = k
                    item["bit"] = int(bit)
                    # item["id"] = "%s-%s" % (k.encode("u8"), str(bit))

                    # 1 ****** 0 ******
                    item["state"] = 1 if int(mask & 1 << int(bit)) else 0
                    # bit_mp[str(bit)] = item
                    tmp_bit_mp.append(item)

                # tmp_permission_class[str(k)] = sorted(tmp_bit_mp, key=lambda o: o["bit"])
                tmp_permission_class = sorted(tmp_bit_mp, key=lambda o: o["bit"])

            group["bit_mp"] = copy.deepcopy(tmp_permission_class)
            new_permission_group.append(group)

        return sorted(new_permission_group, key=lambda o: o["gid"])

    @classmethod
    def get_groups(cls, permission_group):
        """
        ******
        :param permission_group:
        :return:
        """
        group_list = []
        for group in permission_group:
            group.pop("permission_class", True)
            group_list.append(group)

        group_list = sorted(group_list, key=lambda o: o["gid"])

        return group_list

    @classmethod
    def update_permission(cls, **permission_mp):
        """
        ******
        :param permission_mp:{"1": {"1": {"0": 1, "1": 1}, "2": ..}, "2": {..}}
        :return:
        """
        cls.Permission.update_batch_permission(**permission_mp)
        return cls.get_current_permission()

    @classmethod
    def create_group(cls, **group):
        """
        ******
        :param group:
                    {
                        "_id" : "5a379073cbc86e7124eb2c6c",
                        "available" : true,
                        "permission_class" : {
                            "1" : NumberLong(9223372036854775807),
                            "2" : NumberLong(9223372036854775807)
                        },
                        "name" : "xxx",
                        "pid" : 1,
                        "create_at" : 1513590899,
                        "gid" : 1
                    }
        :return:
        """
        return cls.Permission.create_group(**group)

    @classmethod
    def update_group_name(cls, gid, new_name):
        """
        ******,******
        :param group:
        :return:
        """

        d = cls.Permission.update_group_name(gid, new_name)
        if d is None:
            raise cls.api_error.ErrorGroup("******")
        return d

    @classmethod
    def create_class(cls, nums, **classes):
        """
        ******
        :param nums:  ******
        :param classes: {
                            "_id" : "5a379072cbc86e7124eb2c6a",
                            "available" : true,
                            "name" : "******:1",
                            "key" : 1,
                            "bit_mp": {..}
                        }
        :return:
        """

        return cls.Permission.create_class(nums, classes)

    @classmethod
    def create_bit(cls, class_key, name):
        """
        ******
        :param class_key:
        :param name:
        :return:
        """
        return cls.Permission.create_bit(class_key, name)

    @classmethod
    def update_class_name(cls, class_key, new_name):
        """
        ******
        :param group:
        :return:
        """

        d = cls.Permission.update_class_name(class_key, new_name)
        if d is None:
            raise cls.api_error.ErrorGroup("******")
        return d

    @classmethod
    def update_bit_name(cls, class_key, bit, new_nam):
        """
        ******
        :param group:
        :return:
        """

        d = cls.Permission.update_bit_name(class_key, bit, new_nam)
        if d is None:
            raise cls.api_error.ErrorGroup("******")
        return d

    @classmethod
    def update_setting(cls, dir):
        """
        ******，******
        :param dir:
        :return:
        """
        import os
        if not os.path.exists(dir):
            raise Exception("not exists %s" % dir)

        with xlrd.open_workbook(dir) as data:
            def __get_bit_mp(s, e):
                """******"""
                bit_mp = {}
                for i, name in enumerate(table.col_values(1)[s: e]):
                    bit_mp[str(i)] = {
                        "name": name,
                        "available": True,
                        "sort": i + 1,
                        "p_type": table.col_values(3 - 1)[s + i],  # ******
                        "desc": table.col_values(4 - 1)[s + i],  # ******
                        "path": table.col_values(5 - 1)[s + i],  # ******
                    }

                return bit_mp

            def __get_permission_vals(group_index, s, e):
                """******mask
                skip: ******，******
                """
                mask = 0
                skip = 5
                for i, v in enumerate(table.col_values(group_index + skip)[s: e]):
                    if not v and v != 0:
                        v = 0
                    mask += 2 ** i if int(v) else 0
                return mask

            # ******
            table = data.sheets()[0]
            # ******
            cell_values = table._cell_values

            permission_group = []  # ******
            permission_class = []  # ******

            # ******
            groups_list = [n for n in cell_values[1][5:] if n]
            start_gid = 1000
            for i, name in enumerate(groups_list):
                if i == 0:
                    pid = 0
                else:
                    pid = i + start_gid - 1
                permission_group.append({
                    "_id": cls.utils.ObjectId_to(ObjectId()),
                    "name": name,
                    "gid": i + start_gid,
                    "pid": pid,
                    "available": 1,
                    "desc": "",
                    "permission_class": {},
                    "create_at": cls.utils.now()
                })

            # ******
            index_s_e = ([3, 9], [10, 15], [16, 34], [35, 40], [41, 55], [56, 76], [77, 79], [80, 99], [100, 116])
            key = 1
            for s, e in index_s_e:
                s, e = s - 1, e

                for class_name in table.col_values(0)[s: e]:
                    if not class_name:
                        continue

                    # ******
                    permission_class.append({
                        "_id": str(cls.utils.ObjectId()),
                        "name": class_name,
                        "key": str(key),
                        "desc": "",
                        "available": 1,
                        "bit_mp": __get_bit_mp(s, e),
                        "create_at": cls.utils.now()
                    })

                    # ******
                    for i, group in enumerate(permission_group):
                        group["permission_class"][str(key)] = __get_permission_vals(i, s, e)

                    key += 1
                    break

        # assert cls.Permission.check_permission_group(permission_group) is True
        # assert cls.Permission.check_permission_class(permission_class) is True
        # cls.mongo[cls.Permission.PERMISSION_TABLE].remove({}, multi=True)
        cls.mongo[cls.Permission.PERMISSION_CLASS_TABLE].remove({}, multi=True)
        # cls.mongo[cls.Permission.PERMISSION_TABLE].insert(permission_group)
        cls.mongo[cls.Permission.PERMISSION_CLASS_TABLE].insert(permission_class)
        cls.Permission.reload()

    @classmethod
    def get_parent_group(cls, gid, multi=False):
        """
        ******
        :param gid:
        :return:multi=True ******
        """
        if multi:
            return cls.Permission.get_parent_groups(int(gid))
        else:
            return cls.Permission.get_parent_group(int(gid))

    @classmethod
    def get_child_group(cls, gid, multi=False):
        """
        ******
        :param gid:
        :return:multi=True ******
        """
        if multi:
            return cls.Permission.get_child_groups(int(gid))
        else:
            return cls.Permission.get_child_group(int(gid))

    @classmethod
    def get_permission_group(cls, gid):

        """
        ******
        :param gid:
        :return:multi=True ******
        """
        return cls.Permission.get_permission_group(int(gid))

    @classmethod
    def get_childes(cls, gid, multi=False, fields=False):

        """
        ******
        :param gid: ******ID
        :param multi: ******
        :param fields: ******gid******name
        :return:
        """
        child_role_list = cls.get_child_group(gid, multi=multi)
        if fields:
            return [{'gid': i.get('gid'), 'name': i.get('name')} for i in child_role_list]
        else:
            return [i.get('gid') for i in child_role_list]

    @classmethod
    def get_parents(cls, gid, multi=False, fields=False):

        """
        ******
        :param gid: ******ID
        :param multi: ******
        :param fields: ******gid******name
        :return:
        """
        parent_role_list = cls.get_parent_group(gid, multi=multi)
        if fields:
            return [{'gid': i.get('gid'), 'name': i.get('name')} for i in parent_role_list]
        else:
            return [i.get('gid') for i in parent_role_list]

    @classmethod
    def get_permission_by_spec(cls, spec, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        d = cls.find_one(spec)
        return cls._parse_data(d)

    @classmethod
    def get_permission_list_by_last_id(cls, last_id, count, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        spec = {}.update(kwargs.get("spec", {}))
        data_list, last_id = cls.find_list_by_last_id(spec,
                                                      count,
                                                      sort=[("create_at", -1), ],
                                                      fields=False,
                                                      last_id_field=False)
        return [cls._parse_data(d) for d in data_list if d], last_id

    @classmethod
    def get_permission_list_by_page(cls, page, count, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        spec = {}
        spec.update(kwargs.get("spec", {}))
        data_list, pages = cls.find_list_by_page(spec,
                                                 page,
                                                 count,
                                                 sort=[("create_at", -1), ],
                                                 fields=False)
        return [cls._parse_data(d) for d in data_list if d], pages

    @classmethod
    def create_permission(cls, *args, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        pass

    @classmethod
    def modify_permission(cls, *args, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        pass

    @classmethod
    def delete_permission(cls, permission_id, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        return cls.update({"_id": permission_id}, {"state": -1})

    @classmethod
    def _parse_data(cls, d, **kwargs):
        """
        ******
        :return:
        :rtype:
        """
        if not d:
            return {}

        d["permission_id"] = d["_id"]

        return d



