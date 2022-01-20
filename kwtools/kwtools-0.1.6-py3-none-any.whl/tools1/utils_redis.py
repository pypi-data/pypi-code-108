import re
import json
import collections
import time
import pymongo
import redis
import aredis

"""
    redis的 pipe管道事务操作:
        1. pipe为事务管道,必须要execute后才会在服务器端真正执行
        2.当管道中使用watch开启检测后,到multi语句(或者execute语句)前,会让pipe处于"非事务阶段",
          可以获取、删除redis服务器中的值.  (意味着此阶段的pipe.set()不需要execute())
        3. 当pipe.execute()执行时,会把储存在pipe管道中"滞后执行"的事务操作全部一次性完成.
        4.在"管道事务"阶段,打印出来的都是对象(在后面execute后接受str结果); 而在"非事务"阶段,返回的是字符.
"""



class KwRedis():
    """
    tips:
        1. redis中, 貌似不区分 1 和 "1" 的! (int型 1 存入redis中后, 也会变成 字符型 "1" 来存储的)
        2. 本类中, delete表示"删除该键", remove表示"移除该键中的某个值"

    notes:
        1. 这里的Kw不是keyword的意思, 是kerwin的意思!!

    """

    def __init__(self, redis_obj=None):
        if redis_obj == None:
            redis_obj = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
        self.r = redis_obj


    def overview(self):
        """
            function: 罗列redis数据库中, 所有的键名-类型 (只用于打印输出, 没有返回值)
        """
        print(f"redis中, 一共有 {len(self.r.keys())} 个键:")
        keys_lst = self.r.keys()
        keys_lst = sorted(keys_lst)
        for e in keys_lst:
            print(f"键名'{e}' ---->  键类型: {self.r.type(e)};")


    def get(self, key_name, pt=True):
        "pt:是否打印检查"
        # 获取这个键的类型
        e_type = self.r.type(key_name)

        # 根据不同类型, 分类讨论
        if e_type == "string":
            value = self.r.get(key_name)
            print(f"键名'{key_name}'的数据类型为:  'string'")
            if pt:
                kprint(value=value)
            return value
        elif e_type == "list":
            value_lst = self.r.lrange(key_name, 0, -1)
            print(f"键名'{key_name}'的数据类型为:  'list', 长度为'{len(value_lst)}'")
            if pt: # 是否需要打印输出
                if len(value_lst) >= 30: # 当对象包含的元素过多时, 打印输出篇幅太大. 所以, 截取一部分打印 (30个)
                    kprint(value_lst=value_lst[:30])
                else:
                    kprint(value_lst=value_lst)
            return value_lst
        elif e_type == "set":
            value_set = self.r.smembers(key_name)
            print(f"键名'{key_name}'的数据类型为:  'set', 长度为'{len(value_set)}'")
            if pt:
                if len(value_set) >= 30:
                    show_value_set = set()
                    for count, e in enumerate(value_set):
                        if count <= 30:
                            show_value_set.add(e)
                    kprint(show_value_set=show_value_set)
                else:
                    kprint(value_set=value_set)
            return value_set
        elif e_type == "hash":
            value_dict = self.r.hgetall(key_name)
            print(f"键名'{key_name}'的数据类型为:  'hash', 长度为'{len(value_dict)}'")
            if pt:
                if len(value_dict) >= 30:
                    count = 0
                    show_value_dict = dict()
                    for k, v in value_dict.items():
                        count += 1
                        if count <= 30:
                            show_value_dict.update({k:v})
                    kprint(show_value_dict=show_value_dict)
                else:
                    kprint(value_dict=value_dict)
            return value_dict
        elif e_type == "none":
            # 当redis中不存在'key_name'这个键时, 就会返回'none', 这里同样返回 None
            print(f"不存在该键:{key_name}\n\n")
            return None


    def add(self, key_name, *value, sub_value=618618, init_e_type="string", ex=None, pt=True):
        """
            function:
                往某个键中添加值 (若type为'string', 则是重新设置值)
                    1. 当key_name已存在时: 按照原来的数据格式去add值
                    2. 当key_name不存在时: 按照init_e_type指定的数据格式去add值
            params:
                key_name: 键名
                *value: 支持同时新增多个元素(list/set)
                sub_value: 子值 (只用于init_e_type为"hash"的情况)
                init_e_type: 当key_name不存在时, 需要初始化的数据类型
                ex: 过期时长 (单位:秒) (只能应用于"string"类型, 其他类型只能单独用其他方法)
                pt: 是否需要打印

            tips:
                1. list/set 支持同时 add 多个子元素
                2. string/hash 不支持同时 add 多个子元素
        """
        # 获取这个键的真实类型 (用于检查这个'key_name'是否已经存在)
        org_e_type = self.r.type(key_name)
        is_exist = False if org_e_type == "none" else True

        # 根据不同类型, 分类讨论
        if is_exist == True:
            if org_e_type == "string":
                print("\n【string】")
                is_ok = self.r.set(key_name, value[0], ex=ex)
                if pt == True:
                    kprint(is_ok=is_ok)
                return is_ok # True/False
            elif org_e_type == "list":
                print("\n【list】")
                print("新push后的这个键的list长度:")
                key_length = self.r.rpush(key_name, *value) # 返回的是: 新push后的这个键的list长度
                if pt == True:
                    kprint(key_length=key_length)
                return key_length
            elif org_e_type == "set":
                print("\n【set】")
                print("新add进去的数量:")
                update_count = self.r.sadd(key_name, *value) # 返回的是: 新add进去的值的数量
                if pt == True:
                    kprint(update_count=update_count)
                return update_count
            elif org_e_type == "hash":
                print("\n【hash】")
                update_count = self.r.hset(key_name, value[0], sub_value) # 返回的是: 是否成功在hash中新增了一个'键值对' (0:无新增; 1:有1个新增)
                if pt == True:
                    kprint(update_count=update_count)
                return update_count

        elif is_exist == False:
            if init_e_type == "string":
                print("\n【string】")
                is_ok = self.r.set(key_name, value[0], ex=ex)
                if pt == True:
                    kprint(is_ok=is_ok)
                return is_ok # True/False
            elif init_e_type == "list":
                print("\n【list】")
                print("新push后的这个键的list长度:")
                key_length = self.r.rpush(key_name, *value) # 返回的是: 新push后的这个键的list长度
                if pt == True:
                    kprint(key_length=key_length)
                return key_length
            elif init_e_type == "set":
                print("\n【set】")
                print("新add进去的数量:")
                update_count = self.r.sadd(key_name, *value) # 返回的是: 新add进去的值的数量
                if pt == True:
                    kprint(update_count=update_count)
                return update_count
            elif init_e_type == "hash":
                print("\n【hash】")
                update_count = self.r.hset(key_name, value[0], sub_value) # 返回的是: 是否成功在hash中新增了一个'键值对' (0:无新增; 1:有1个新增)
                if pt == True:
                    kprint(update_count=update_count)
                return update_count


    def remove(self, key_name, *to_remove_e):
        """
            function:
                移除键中的某个元素
            tips:
                list/set/hash 都支持同时remove多个子元素
        """

        # 获取这个键的类型
        e_type = self.r.type(key_name)

        # 根据不同类型, 分类讨论
        if e_type == "string":
            is_ok = self.r.delete(key_name)
            print("删除是否成功(0:不成功; 1:成功):")
            kprint(is_ok=is_ok)
            return is_ok
        elif e_type == "list":
            removed_count = self.r.lrem(key_name, 1, *to_remove_e) # 默认只移除一个值
            kprint(removed_count=removed_count)
            return removed_count
        elif e_type == "set":
            removed_count = self.r.srem(key_name, *to_remove_e)
            kprint(removed_count=removed_count)
            return removed_count
        elif e_type == "hash":
            removed_count = self.r.hdel(key_name, *to_remove_e)
            kprint(removed_count=removed_count)
            return removed_count
        elif e_type == "none":
            # 当redis中不存在'key_name'这个键时, 就会返回'none', 这里同样返回 None
            print(f"不存在该键:{key_name}\n\n")
            return None


    def delete(self, key_name):
        "删除整个键"
        is_ok = self.r.delete(key_name) # 是否成功删除 (0:不成功; 1:成功)
        print("删除是否成功(0:不成功; 1:成功):")
        kprint(is_ok=is_ok)
        return is_ok


    def set_ex(self, key_name, ex=60):
        """
        function: 设置过期时长
        params:
            ex: 以秒为单位
        """
        self.r.expire(key_name, ex) # 设定键的过期时间 (单位为秒)
        print(f"已对 {key_name} 设置过期时长: {ex}\n")


    def get_ex(self, key_name):
        """
        function: 获取某个键的剩余过期时长 (以秒为单位)
        """
        # 可能返回的结果:
            # -2: 无该键
            # -1: 有该键, 但该键没有过期时间 (永久存在)
            # >=0: 该键的剩余过期时长
        remaining_time = self.r.ttl(key_name) # 获取某个键的剩余过期时长 (以秒为单位)
        print(f"{key_name} 的剩余过期时长: {remaining_time}\n")
        return remaining_time


    def update(self, key_name):
        pass




if __name__ == '__main__':
    R0 = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
