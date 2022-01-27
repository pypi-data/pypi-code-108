"""
pyape.app.models.valueobject
~~~~~~~~~~~~~~~~~~~

ValueObject 表
"""

import json
import toml

from sqlalchemy.sql.expression import or_
from sqlalchemy.exc import SQLAlchemyError

from pyape.app import gdb, logger


class ValueObject(gdb.Model):
    """ 所有量不大的值对象放在这里，例如 Version/Token
    """
    __tablename__ = 'vo'

    vid = gdb.Column(gdb.INT, primary_key=True, autoincrement=True)

    # 区服编号，对应 regional
    r = gdb.Column(gdb.SMALLINT, nullable=False, default=0)

    # VO 的名称
    name = gdb.Column(gdb.VARCHAR(32), nullable=False, unique=True, index=True)

    # VO 的值，一般使用 JSON/TOML 字符串
    value = gdb.Column(gdb.TEXT, nullable=False)

    # VO 的类型，详见 typeid
    votype = gdb.Column(gdb.SMALLINT, index=True, nullable=False, default=307)

    # 排序索引
    index = gdb.Column(gdb.SMALLINT, nullable=False, default=0)

    # VO 是 1启用 还是 5禁用
    status = gdb.Column(gdb.SMALLINT, index=True, nullable=False, default=1)

    # createtime = gdb.Column(gdb.TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP'))
    # updatetime = gdb.Column(gdb.TIMESTAMP(True), nullable=True,
    #                        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # updatetime = gdb.Column(gdb.TIMESTAMP(True), nullable=True)

    # 2021-01-10 改用时间戳，将格式化完全交给客户端来处理
    createtime = gdb.Column(gdb.INT, nullable=False)
    updatetime = gdb.Column(gdb.INT, nullable=True)

    # 说明字段
    note = gdb.Column(gdb.VARCHAR(512), nullable=True)

    @staticmethod
    def dump_value(value, type_='json'):
        """ 将提供的 value 转换成为 TOML 或者 JSON 字符串
        :return:
        """
        if type_ == 'toml':
            # toml 不支持 list 格式，对于之前 json list 格式的配置文件，加入一个顶级的 ROOTLIST 键
            if isinstance(value, list):
                return toml.dumps({'ROOTLIST': value})
            return toml.dumps(value)
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def load_value(value, type_=None):
        """ 将 value 字符串转换成为 dict 或者 list
        首先检测是否为 json 格式
        然后考虑 toml 格式
        :return:
        """
        # logger.info('ValueObject.load_value %s, type: %s', value, type_)
        def toml_loads(value):
            tobj = toml.loads(value, dict)
            # toml 不支持 list 格式，对于之前 json list 格式的配置文件，加入一个顶级的 ROOTLIST 键
            # 若存在这个键且其值为 list，则仅返回这个 list
            rootlist = tobj.get('ROOTLIST')
            # logger.info('toml_loads tobj %s', tobj)
            # 使用 pickle 处理 loads 后的对象时，会出现下面的错误
            # TomlDecoder.get_empty_inline_table.<locals>.DynamicInlineTableDict
            # 因此使用 json 转换一遍
            if isinstance(rootlist, list):
                jstr = json.dumps(rootlist, ensure_ascii=False)
            else:
                jstr = json.dumps(tobj, ensure_ascii=False)
            return json.loads(jstr)

        if type_ is None:
            try:
                return json.loads(value)
            except Exception as e:
                logger.warning('ValueObject.load_value, value is not json: %s', e)
                try:
                    return toml_loads(value)
                except Exception:
                    return None
        elif type_ == 'toml':
            try:
                return toml_loads(value)
            except Exception:
                return None
        else:
            try:
                return json.loads(value)
            except Exception:
                return None

    def set_value(self, value, type_='json'):
        """
        将提供的 value 转换成为 ValueObject 需要的 JSON 字符串
        :return:
        """
        self.value = ValueObject.dump_value(value, type_)

    def get_value(self, type_=None):
        """
        将 ValueObject 中的 value 字符串转换成为 dict
        首先检测是否为 toml 格式
        然后考虑 json 格式
        :return:
        """
        valueobj = ValueObject.load_value(self.value, type_)
        # logger.info('get_value %s', valueobj)
        return valueobj

    def merge(self, includes=['votype', 'createtime', 'updatetime', 'note', 'status'], type_=None):
        """
        将 ValueObject 对象转换成为一个 dict ，合并 createtime/updatetime/vid/typeid 到 value 代表的 JSON 对象中
        :param includes: 需要包含的字段
        :return:
        """
        voobj = self.get_value(type_)
        if isinstance(voobj, dict):
            pass
        elif voobj is None:
            voobj = {}
        else:
            voobj = {'value': voobj}
        voobj['vid'] = self.vid
        voobj['name'] = self.name
        voobj['index'] = self.index
        if includes:
            for k in includes:
                try:
                    v = getattr(self, k)
                    # 2021-01-10 使用时间戳，不再需要 isoformat
                    # if isinstance(v, datetime):
                    #     v = v.isoformat()
                    voobj[k] = v
                except AttributeError:
                    pass
        return voobj


def get_vo_fullname(r, name):
    """ 由于 vo 的 name 是 unique 的，需要给所有 name 加上 r 前缀
    """
    return 'r%s_%s' % (r, name)


def get_vo_by_fullname(fullname, type_=None, merge=None):
    """ 获取一个 vo，此处提供的 name 完整名称
    """
    vo = ValueObject.query.filter_by(name=fullname, status=1).first()
    if vo is not None:
        if isinstance(merge, list):
            return vo.merge(merge, type_)
        return vo.get_value(type_)
    return None


def get_vo_by_name(r, name, type_=None, merge=None):
    """ 获取一个 vo，此处提供的 name 是不含 r 前缀的名称
    """
    fullname = get_vo_fullname(r, name)
    return get_vo_by_fullname(fullname, type_, merge)


def get_vo_query(r, votype=None, status=None):
    """ 获取排序过的 ValueObject 项目，可以根据 usertype 和 status 筛选
    :param votype:
    :param status:
    :return:
    """
    cause = [ValueObject.r == r]
    if votype is not None:
        cause.append(ValueObject.votype == votype)
    if status is not None:
        cause.append(ValueObject.status == status)
    return ValueObject.query.filter(*cause).\
            order_by(ValueObject.status, ValueObject.index, ValueObject.createtime.desc())


def get_vos_vidname(votype):
    vos = ValueObject.query.filter_by(votype=votype, status=1).\
        with_entities(ValueObject.vid, ValueObject.name).\
        all()
    return vos


def del_vo_vidname(vid, name):
    """ 通过 vid 或者 name 删除一个 vo
    """
    try:
        ValueObject.query.filter(or_(ValueObject.vid==vid, ValueObject.name==name)).delete()
        gdb.session.commit()
    except SQLAlchemyError as e:
        msg = 'valueobject.del_vo_vidname error: ' + str(e)
        logger.error(msg)
        return msg
    return None


def init_valueobject():
    pass