#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 3:26 下午
# @Author  : zhengyu.0985
# @FileName: sqlalchemy_util.py
# @Software: PyCharm

import configparser
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import traceback
import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
logger = logging.getLogger('com.zijie.db.sqlalchemy_util')


class AlchemyUtil(object):

    # 基类
    Base = declarative_base()

    @classmethod
    def get_db_param_dict(cls, db_key, db_conf_relative_path):
        conf_file = open(db_conf_relative_path)
        cf = configparser.ConfigParser()
        cf.read_file(conf_file)
        json_str = cf.get("mysql", db_key)
        dict_val = json.loads(json_str)
        logger.info("%s = %s" % (db_key, dict_val))
        return dict_val

    @classmethod
    def init_engine(cls, db_param_dict):
        """
        根据数据库连接串创建MySQL数据库的engine。
        :param db_param_dict: 数据连接串的各项参数的字典。
        :return: MySQL数据库的engine。
        """
        host = db_param_dict['db_host']
        user = db_param_dict['db_user']
        passwd = db_param_dict['db_passwd']
        db = db_param_dict['db_db']
        charset = db_param_dict['db_charset']
        port = db_param_dict['db_port']
        logger.info("host = {0}".format(host))
        logger.info("user = {0}".format(user))
        logger.info("passwd = {0}".format(passwd))
        logger.info("db = {0}".format(db))
        logger.info("charset = {0}".format(charset))
        logger.info("port = {0}".format(port))
        mysql_engine = create_engine(
            "mysql+pymysql://"+ user +":"+ passwd +"@"+ host +":" + port +"/"+ db +"?charset="+charset,
            max_overflow=0,  # 超过连接池大小外最多创建的连接
            pool_size=5,  # 连接池大小
            pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
            pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
        )
        logger.info("[%s] engine has been created successfully." % mysql_engine.name)
        return mysql_engine

    @classmethod
    def init_db(cls, mysql_engine):
        """
        根据类创建数据库表
        :return:
        """
        AlchemyUtil.Base.metadata.create_all(mysql_engine)

    @classmethod
    def drop_db(cls, mysql_engine):
        """
        根据类删除数据库表
        :return:
        """
        AlchemyUtil.Base.metadata.drop_all(mysql_engine)

    @classmethod
    def get_session(cls, mysql_engine):
        db_session = sessionmaker(bind=mysql_engine)  # Session是<class 'sqlalchemy.orm.session.sessionmaker'>
        return db_session()

    @classmethod
    def insert_list_with_flush_only(cls, session, obj_list):
        try:
            for obj in obj_list:
                session.add(obj)
                session.flush()
            logger.info("【Success】一共插入 %d 条记录 by [insert_list_with_flush_only] method." % len(obj_list))
        finally:
            logger.info("[insert_list_with_flush_only] method has done, but has not been committed yet.")

    @classmethod
    def insert_obj_with_commit(cls, session, obj):
        try:
            session.add(obj)
            session.commit()
            logger.info("【Success】插入一条记录：%s" % obj.__dict__)
        finally:
            session.close()
            logger.info("[insert_obj_with_commit] method has done and session has been closed.")

    @classmethod
    def insert_obj_without_commit(cls, session, obj):
        try:
            session.add(obj)
            session.flush()
            logger.info("【Success】插入一条记录：%s" % obj.__dict__)
        finally:
            logger.info("[insert_obj_without_commit] method has done but not committed yet.")

    @classmethod
    def do_commit_only(cls, session):
        try:
            session.commit()
            logger.info("session has been committed.")
        finally:
            session.close()
            logger.info("do_commit_only method has done and session has been closed.")

    @classmethod
    def query_first(cls, session, clazz, criteria_set=None):
        try:
            if criteria_set is None or len(criteria_set) == 0:
                sql = session.query(clazz)
                logger.info("执行全量查询SQL = %s" % sql)
            else:
                sql = session.query(clazz).filter(*criteria_set)
                logger.info("执行条件查询SQL = %s" % sql)
            record = sql.one_or_none()  # 真正执行该查询。
            return record
        finally:
            session.close()
            logger.info("[query_first] method has done and session has been closed.")

    @classmethod
    def query_obj_list(cls, session, clazz, criteria_set=None):
        try:
            if criteria_set is None or len(criteria_set) == 0:
                sql = session.query(clazz)
                logger.info("执行全量查询SQL = %s" % sql)
            else:
                sql = session.query(clazz).filter(*criteria_set)
                logger.info("执行条件查询SQL = %s" % sql)
            record_list = sql.all()  # 真正执行该查询。
            logger.info("查询获取到 %d 条记录。" % len(record_list))
            return record_list
        finally:
            session.close()
            logger.info("[query_obj_list] method has done and session has been closed.")

    @classmethod
    def query_field_list(cls, session, entities, criteria_set=None):
        try:
            if criteria_set is None or len(criteria_set) == 0:
                sql = session.query(*entities)
                logger.info("执行全量查询SQL = %s" % sql)
            else:
                sql = session.query(*entities).filter(*criteria_set)
                logger.info("执行条件查询SQL = %s" % sql)
            fields_record_list = sql.all()  # 真正执行该查询。
            logger.info("查询获取到 %d 条记录。" % len(fields_record_list))
            return fields_record_list
        finally:
            session.close()
            logger.info("[query_field_list] method has done and seesion has been closed.")

    @classmethod
    def query_field_list_with_distinct(cls, session, entities, criteria_set=None, distinct_columns=None):
        try:
            if criteria_set is None or len(criteria_set) == 0:
                if distinct_columns is None or len(distinct_columns) == 0:
                    sql = session.query(*entities)
                else:
                    sql = session.query(*entities).distinct(*distinct_columns)
                logger.info("执行全量查询SQL = %s" % sql)
            else:
                if distinct_columns is None or len(distinct_columns) == 0:
                    sql = session.query(*entities).filter(*criteria_set)
                else:
                    sql = session.query(*entities).filter(*criteria_set).distinct(*distinct_columns)
                logger.info("执行条件查询SQL = %s" % sql)
            fields_record_list = sql.all()  # 真正执行该查询。
            logger.info("查询获取到 %d 条记录。" % len(fields_record_list))
            return fields_record_list
        finally:
            session.close()
            logger.info("[query_field_list_with_distinct] method has done and seesion has been closed.")

    @classmethod
    def update_for_criteria_with_commit(cls, session, clazz, criteria_set=None, update_dict={}):
        """
        :param session: db_session
        :param clazz: db_model_name
        :param criteria_set: query's criteria
        :param update_dict: update's field-value pairs
        :return: row count of updated records
        """
        if len(update_dict) > 0:
            try:
                if criteria_set is None or len(criteria_set) == 0:
                    sql = session.query(clazz)
                    logger.info("执行全量查询SQL = %s" % sql)
                else:
                    sql = session.query(clazz).filter(*criteria_set)
                    logger.info("执行条件查询SQL = %s" % sql)
                affected_row = sql.update(update_dict)  # 真正执行更新，返回更新的记录条数。
                session.commit()
                logger.info("【Success】一共更新 %d 行记录。" % affected_row)
                return affected_row
            except:
                session.rollback()
                logger.warning("出现异常")
                logger.error(traceback.format_exc())
            finally:
                session.close()
        else:
            logger.warning("依据update_dict参数，传入的需要更新的字段个数为零，无法更新。")

    @classmethod
    def delete_for_criteria_commit(cls, session, clazz, criteria_set=None):
        """
        :param session: db_session
        :param clazz: db_model_name
        :param criteria_set: query's criteria
        :return: row count of deleted records
        """
        try:
            if criteria_set is None or len(criteria_set) == 0:
                logger.info("criteria_set 为空，不可删除全部记录，有风险。")
                return 0
            else:
                sql = session.query(clazz).filter(*criteria_set)
                logger.info("执行条件查询SQL = %s" % sql)
                affected_row = sql.delete()  # 真正执行删除，返回删除的记录条数。
                session.commit()
                logger.info("【Success】一共删除 %d 行记录，依据条件：%s" % (affected_row, *criteria_set))
                return affected_row
        except:
            session.rollback()
            logger.warning("出现异常")
            logger.error(traceback.format_exc())
        finally:
            session.close()

    @classmethod
    def gen_unique_key(cls):
        dt = datetime.datetime.now()
        dt_str = dt.strftime('%Y%m%d%H%M%S')
        ts = datetime.datetime.timestamp(dt)
        ts_str = str(int(ts * 1000000))
        unique_key = dt_str + ts_str
        return unique_key


if __name__ == "__main__":
    dict_val = AlchemyUtil.get_db_param_dict("DB_BOE_Site_Reldb", "../../conf/db.conf")
    engine = AlchemyUtil.init_engine(dict_val)
    AlchemyUtil.init_db(engine)  # 创建表（存在则不创建）
    site_rel_db_session = AlchemyUtil.get_session(engine)
