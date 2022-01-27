#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/13 2:41 下午
# @Author  : zhengyu.0985
# @FileName: base_compare.py
# @Software: PyCharm

from rolling_king.zijie.db.db_models import CaseRecordModel, BamInterModel, NonCovInterModel
from rolling_king.zijie.db.sqlalchemy_util import AlchemyUtil
from rolling_king.zijie.tests.base.base_test import BaseTest
import logging
import os

logger = logging.getLogger("base_compare")


class CoverDiff(object):

    @staticmethod
    def _get_db_conf_path():
        file_path = os.getcwd()
        index_of_com = file_path.find("com")
        if index_of_com != -1:
            # 下面一行是绝对路径传入获取配置文件的方法。
            conf_absolute_path = file_path[0:index_of_com] + "com/conf/"
            db_conf_file_path = conf_absolute_path + "db.conf"
        else:
            # 下面一行的相对路径会随测试py文件位置而变化，仅在测试文件绝对路径中不包含com时，做默认三层情况使用。
            db_conf_file_path = "../../../conf/db.conf"
        return db_conf_file_path

    @staticmethod
    def get_diff_result(psm=None, test_project_name=None, protocol="BOTH"):
        db_conf_dict = AlchemyUtil.get_db_param_dict("DB_BOE_Site_Reldb", CoverDiff._get_db_conf_path())
        engine = AlchemyUtil.init_engine(db_conf_dict)
        AlchemyUtil.init_db(engine)  # 创建表（存在则不创建）
        site_rel_db_session = AlchemyUtil.get_session(engine)
        # 判断已测试（分子）的查询范围。
        if psm is None and test_project_name is None:
            project_conf_dict = BaseTest.get_project_conf_dict()
            psm = project_conf_dict['test_psm']
            test_project_name = project_conf_dict['test_project_name']
            tested_criteria_set = {  # 这是<class 'set'>类型。
                CaseRecordModel.test_psm == psm,  # 被测PSM
                CaseRecordModel.test_project_name == test_project_name  # 测试项目名
            }
        elif psm is None:
            project_conf_dict = BaseTest.get_project_conf_dict()
            psm = project_conf_dict['test_psm']
            tested_criteria_set = {  # 这是<class 'set'>类型。
                CaseRecordModel.test_psm == psm,  # 被测PSM
                CaseRecordModel.test_project_name == test_project_name  # 测试项目名
            }
        elif test_project_name is None:  # 只传入PSM，证明与被测项目无关，全局进行查询。
            logger.info("test_project_name is None")
            tested_criteria_set = {  # 这是<class 'set'>类型。
                CaseRecordModel.test_psm == psm,  # 被测PSM
            }
        else:
            tested_criteria_set = {  # 这是<class 'set'>类型。
                CaseRecordModel.test_psm == psm,  # 被测PSM
                CaseRecordModel.test_project_name == test_project_name  # 测试项目名
            }

        # 获取已测试列表
        tested_list = AlchemyUtil.query_obj_list(site_rel_db_session, CaseRecordModel, tested_criteria_set)

        # 下面查询总接口数（分母）

        # 查询总接口的若干字段
        collum_tuple = (BamInterModel.psm, BamInterModel.name, BamInterModel.method, BamInterModel.path,\
                        BamInterModel.rpc_method, BamInterModel.note, BamInterModel.endpoint_id, BamInterModel.version)

        # 依据想要对比的接口协议类型，进行对比。
        if protocol == "HTTP" or protocol == "REST":
            logger.info("仅对比HTTP接口")
            total_criteria_set = {  # 这是<class 'set'>类型。
                BamInterModel.psm == psm,
                BamInterModel.path != '',
                BamInterModel.method != ''
            }
            total_list = AlchemyUtil.query_field_list(site_rel_db_session, collum_tuple,
                                                      criteria_set=total_criteria_set)
            if len(tested_list) == 0:
                logger.info("tested_list：为空")
                if len(total_list) > 0:
                    CoverDiff._delete_non_cov_records(psm, total_list)
                    CoverDiff._insert_non_cov_to_db(psm, total_list)
            elif len(total_list) == 0:
                logger.info("total_list：为空")
            else:
                diff_tuple_list = CoverDiff._compare_http(tested_list, total_list)
                CoverDiff._delete_non_cov_records(psm, diff_tuple_list)
                CoverDiff._insert_non_cov_to_db(psm, diff_tuple_list)
                return len(diff_tuple_list)
        elif protocol == "RPC" or protocol == "THRIFT":
            logger.info("仅对比RPC接口")
            total_criteria_set = {  # 这是<class 'set'>类型。
                BamInterModel.psm == psm,
                BamInterModel.path == '',
                BamInterModel.method == ''
            }
            total_list = AlchemyUtil.query_field_list(site_rel_db_session, collum_tuple,
                                                      criteria_set=total_criteria_set)
            if len(tested_list) == 0:
                logger.info("tested_list：为空")
                if len(total_list) > 0:
                    CoverDiff._delete_non_cov_records(psm, total_list)
                    CoverDiff._insert_non_cov_to_db(psm, total_list)
            elif len(total_list) == 0:
                logger.info("total_list：为空")
            else:
                diff_tuple_list = CoverDiff._compare_rpc(tested_list, total_list)
                CoverDiff._delete_non_cov_records(psm, diff_tuple_list)
                CoverDiff._insert_non_cov_to_db(psm, diff_tuple_list)
                return len(diff_tuple_list)
        else:
            logger.info("HTTP and RPC 接口均对比")
            total_criteria_set = {  # 这是<class 'set'>类型。
                BamInterModel.psm == psm,
            }
            total_list = AlchemyUtil.query_field_list(site_rel_db_session, collum_tuple,
                                                      criteria_set=total_criteria_set)
            if len(tested_list) == 0:
                logger.info("tested_list：为空")
                if len(total_list) > 0:
                    CoverDiff._delete_non_cov_records(psm, total_list)
                    CoverDiff._insert_non_cov_to_db(psm, total_list)
            elif len(total_list) == 0:
                logger.info("total_list：为空")
            else:
                diff_tuple_list = CoverDiff._compare_both(tested_list, total_list)
                CoverDiff._delete_non_cov_records(psm, diff_tuple_list)
                CoverDiff._insert_non_cov_to_db(psm, diff_tuple_list)
                return len(diff_tuple_list)
        # 返回数量
        return 0

    @staticmethod
    def _compare_rpc(tested_list, total_list):
        logger.info("一共 %d 个接口。" % len(total_list))
        for curr_test in tested_list:
            curr_rpc_method = curr_test.__dict__['test_interface'].split(".")[1]
            for curr_db_record in total_list:
                if curr_rpc_method == curr_db_record[4]:
                    logger.info("curr_db_record = %s" % curr_db_record)
                    logger.info("[RPC] %s 已被 %s 项目的 %s 测试用例覆盖。" % (curr_rpc_method, curr_test.test_project_name, curr_test.test_method))
                    total_list.remove(curr_db_record)
                    break
                else:
                    pass
        logger.info("未覆盖 %d 个接口" % len(total_list))
        return total_list

    @staticmethod
    def _compare_http(tested_list, total_list):
        logger.info("一共 %d 个接口。" % len(total_list))
        for curr_test in tested_list:
            curr_http_uri = curr_test.__dict__['test_interface'].split("::")[1]
            for curr_db_record in total_list:
                if curr_http_uri == curr_db_record[3]:
                    logger.info("curr_db_record = %s" % curr_db_record)
                    logger.info("[REST] %s 已被 %s 项目的 %s 测试用例覆盖。" % (curr_http_uri, curr_test.test_project_name, curr_test.test_method))
                    total_list.remove(curr_db_record)
                    break
                else:
                    pass
        logger.info("未覆盖 %d 个接口" % len(total_list))
        return total_list

    @staticmethod
    def _compare_both(tested_list, total_list):
        logger.info("一共 %d 个接口。" % len(total_list))
        for curr_test in tested_list:
            if curr_test.test_inter_type == 'HTTP':
                curr_http_uri = curr_test.__dict__['test_interface'].split("::")[1]
                for curr_db_record in total_list:
                    if curr_http_uri == curr_db_record[3]:
                        logger.info("curr_db_record = %s" % curr_db_record)
                        logger.info("[REST] %s 已被 %s 项目的 %s 测试用例覆盖。" % (
                        curr_http_uri, curr_test.test_project_name, curr_test.test_method))
                        total_list.remove(curr_db_record)
                        break
                    else:
                        pass
                # End For
            elif curr_test.test_inter_type == 'THRIFT':
                curr_rpc_method = curr_test.__dict__['test_interface'].split(".")[1]
                for curr_db_record in total_list:
                    if curr_rpc_method == curr_db_record[4]:
                        logger.info("curr_db_record = %s" % curr_db_record)
                        logger.info("[RPC] %s 已被 %s 项目的 %s 测试用例覆盖。" % (
                        curr_rpc_method, curr_test.test_project_name, curr_test.test_method))
                        total_list.remove(curr_db_record)
                        break
                    else:
                        pass
                # End For
            else:
                pass
        logger.info("未覆盖 %d 个接口" % len(total_list))
        return total_list

    @staticmethod
    def _insert_non_cov_to_db(psm, non_cov_tuple_list):
        if non_cov_tuple_list is not None and len(non_cov_tuple_list) > 0:
            logger.info("PSM=[%s]，需要 插入 %d 条记录。" % (psm, len(non_cov_tuple_list)))
            non_cov_inter_model_list = []
            for curr_non_cov_tuple in non_cov_tuple_list:
                curr_non_cov_inter = NonCovInterModel()
                curr_non_cov_inter.id = AlchemyUtil.gen_unique_key()
                curr_non_cov_inter.psm = curr_non_cov_tuple[0],
                curr_non_cov_inter.name = curr_non_cov_tuple[1],
                curr_non_cov_inter.method = curr_non_cov_tuple[2],
                curr_non_cov_inter.path = curr_non_cov_tuple[3],
                curr_non_cov_inter.rpc_method = curr_non_cov_tuple[4],
                curr_non_cov_inter.note = curr_non_cov_tuple[5],
                curr_non_cov_inter.endpoint_id = curr_non_cov_tuple[6],
                curr_non_cov_inter.version = curr_non_cov_tuple[7]
                non_cov_inter_model_list.append(curr_non_cov_inter)
            dict_val = AlchemyUtil.get_db_param_dict("DB_BOE_Site_Reldb", CoverDiff._get_db_conf_path())
            engine = AlchemyUtil.init_engine(dict_val)
            AlchemyUtil.init_db(engine)  # 创建表（存在则不创建）
            site_rel_db_session = AlchemyUtil.get_session(engine)
            AlchemyUtil.insert_list_with_flush_only(site_rel_db_session, non_cov_inter_model_list)
            AlchemyUtil.do_commit_only(site_rel_db_session)
        else:
            logger.info("[无需插入]：non_cov_tuple_list 为空，无需插入。")

    @staticmethod
    def _delete_non_cov_records(psm, diff_tuple_list):
        if psm is not None:
            dict_val = AlchemyUtil.get_db_param_dict("DB_BOE_Site_Reldb", CoverDiff._get_db_conf_path())
            engine = AlchemyUtil.init_engine(dict_val)
            AlchemyUtil.init_db(engine)  # 创建表（存在则不创建）
            site_rel_db_session = AlchemyUtil.get_session(engine)
            if diff_tuple_list is None:
                AlchemyUtil.delete_for_criteria_commit(site_rel_db_session, NonCovInterModel, {NonCovInterModel.psm == psm})
            else:
                existing_non_cov_list_in_db = AlchemyUtil.query_field_list(site_rel_db_session,\
                                                                                    (NonCovInterModel.endpoint_id,
                                                                                     NonCovInterModel.name),\
                                                                                    {NonCovInterModel.psm == psm})
                already_cov_endpoint_list = []
                for non_cov_tuple_in_db in existing_non_cov_list_in_db:
                    found = False
                    curr_endpoint = non_cov_tuple_in_db[0]
                    for curr_diff_tuple in diff_tuple_list:
                        if curr_endpoint == curr_diff_tuple[6]:
                            diff_tuple_list.remove(curr_diff_tuple)
                            found = True
                            break
                        else:
                            pass
                    if not found:
                        already_cov_endpoint_list.append(curr_endpoint)
                # End For
                logger.info("PSM=[%s]，需要 删除 %d 条记录。" % (psm, len(already_cov_endpoint_list)))
                if len(already_cov_endpoint_list) > 0:
                    AlchemyUtil.delete_for_criteria_commit(site_rel_db_session, NonCovInterModel, {NonCovInterModel.endpoint_id in already_cov_endpoint_list})
                    logger.info("【Success】PSM=[%s]，成功 删除 %d 条记录。" % (psm, len(already_cov_endpoint_list)))
        else:
            logger.info("psm is None.")
            pass
