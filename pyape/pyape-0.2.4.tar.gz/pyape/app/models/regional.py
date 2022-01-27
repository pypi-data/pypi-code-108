"""
pyape.app.models.regional
~~~~~~~~~~~~~~~~~~~

Regional 表
"""
import time
import toml
from sqlalchemy.sql.expression import text
from sqlalchemy.exc import SQLAlchemyError

from pyape.app import gdb, logger
from pyape.app.queryfun import commit_and_response_error
from pyape.config import RegionalConfig
from pyape.util.func import parse_int


class Regional(gdb.Model):
    """ Regional 配置
    """
    __tablename__ = 'regional'

    # 1000测试 2000审核 5000正式
    REGIONAL_TYPES = [1000, 2000, 5000]

    # Regional 配置的主键序号
    r = gdb.Column(gdb.SMALLINT, primary_key=True, index=True, autoincrement=False)

    # Regional 名称
    name = gdb.Column(gdb.VARCHAR(100), nullable=False)

    # Regional 的具体配置， TOML 字符串
    value = gdb.Column(gdb.TEXT, nullable=True)

    # 对 regional 的一种分类法，其值应为 typeid
    kindtype = gdb.Column(gdb.SMALLINT, nullable=False, index=True)

    # Regional 的状态，值为在 TypeID 中的整数，1正常，5 禁用
    status = gdb.Column(gdb.SMALLINT, nullable=False, default=1)

    # createtime = gdb.Column(gdb.TIMESTAMP(True), server_default=text('CURRENT_TIMESTAMP'))
    # updatetime = gdb.Column(gdb.TIMESTAMP(True), nullable=True,
    #                        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # 改用时间戳，将格式化完全交给客户端来处理
    createtime = gdb.Column(gdb.INT, nullable=False)
    updatetime = gdb.Column(gdb.INT, nullable=True)

    @staticmethod
    def r2type(r):
        """ 将 r 转换成数字表示的 mjptype
        """
        if r >= 1000 and r < 2000:
            return 1000
        elif r >= 2000 and r < 3000:
            return 2000
        elif r >= 5000:
            return 5000
        return None

    @classmethod
    def get_qry(cls, kindtype=None, rtype=None, status=None):
        """ 获取排序过的 Regional 项目，可以根据 kindtype/rtype/status 筛选
        :param kindtype:
        :param rtype:
        :param status:
        :return:
        """
        cause = []
        if kindtype is not None:
            cause.append(cls.kindtype == kindtype)
        if status is not None:
            cause.append(cls.status == status)
        if rtype is not None:
            if rtype == 1000:
                cause.append(cls.r.between(1000, 1999))
            elif rtype == 2000:
                cause.append(cls.r.between(2000, 2999))
            else:
                cause.append(cls.r.between(5000, 5999))
        return cls.query.filter(*cause).\
                order_by(cls.status, cls.createtime.desc())

    def merge(self):
        """ 合并数据库中的其他字段到 value 配置中
        """
        parsed_dict = {}
        if self.value is not None:
            parsed_dict = toml.loads(self.value)
        parsed_dict['name'] = self.name
        parsed_dict['r'] = self.r
        parsed_dict['kindtype'] = self.kindtype
        parsed_dict['status'] = self.status
        parsed_dict['createtime'] = self.createtime
        parsed_dict['updatetime'] = self.updatetime
        parsed_dict['rtype'] = Regional.r2type(self.r)
        return parsed_dict


def get_regional_config(status=None):
    """ 从数据库中读取 regional 的配置，转换成 RegionalConfig
    """
    # 取出数据库中所有启用的 Regional
    qry = Regional.query
    if isinstance(status, int):
        qry = qry.filter_by(status=status)
    regional_list = [ritem.merge() for ritem in qry.all()]
    return RegionalConfig(regional_list)


def check_regional(r, ignore_zero=False):
    """ 检查 regional 是否有效，同时返回数据库中查询到的 regional 配置
    :param ignore_zero: 值为真，则允许 r 值为 0。0 是一个特殊的 r 值，代表全局 r
    :return: 已经转换成整数的 regional 值，以及数据库中查到的 regional 配置
    """
    r = parse_int(r)
    if r is None:
        return None, None
    if ignore_zero:
        if r == 0:
            return 0, Regional.query.filter_by(status=1, r=0).first()
    # 从数据库中的启用的 regional 中查找
    regional = Regional.query.filter_by(status=1, r=r).first()
    if regional is None:
        return None, None
    return r, regional


def check_regionals(rs, ignore_zero=False):
    """ 判断数据库中是否包含所有的 rs
    :param ignore_zero: 值为真，则允许 rs 值为 [0]。0 是一个特殊的 r 值，代表全局 r
    """
    lenrs = len(rs)
    if ignore_zero:
        # 传递 0 的时候， rs 只能拥有 1 个项： 0
        if lenrs == 1 and parse_int(rs[0]) == 0:
            return True
    regionals = Regional.query.filter_by(status=1).filter(Regional.r.in_(rs)).all()
    return len(regionals) == lenrs


def init_regional():
    """ 初始化 regional0 这是必须存在的一条
    """
    r0 = Regional.query.get(0)
    if r0 is not None:
        raise TypeError('The regional 0 is exists!')

    now = int(time.time())
    r0 = Regional(r=0, name='0', kindtype=0, status=1, createtime=now, updatetime=now)
    resp = commit_and_response_error(r0, return_dict=True)
    if resp is not None:
        raise SQLAlchemyError('Init regional table error: %s' % resp['message'])
