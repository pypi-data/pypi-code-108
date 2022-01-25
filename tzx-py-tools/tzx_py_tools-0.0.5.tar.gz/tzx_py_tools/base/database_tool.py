#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   database_tool.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/10 9:42     douly      1.0         database_tool
"""
# import lib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from sqlalchemy.ext.declarative import declarative_base
model_base = declarative_base()


def get_session(orm_str: str, encode = 'utf-8', echo=False):
	"""
	获取SQLAlchemy的会话对象

	:param orm_str: SQLAlchemy的数据库连接串
	:return:
	"""
	src_engine = create_engine(orm_str, encoding=encode, echo=echo)
	# 创建DBSession类型:
	SourceSession = sessionmaker(bind=src_engine)
	return SourceSession()
