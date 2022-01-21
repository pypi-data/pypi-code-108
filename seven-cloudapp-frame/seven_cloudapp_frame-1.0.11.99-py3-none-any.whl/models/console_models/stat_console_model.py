# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-19 13:37:16
@LastEditTime: 2022-01-14 14:15:03
@LastEditors: HuangJianYi
@Description: 
"""
import threading, multiprocessing
from seven_framework.console.base_console import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.db_models.stat.stat_queue_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_orm_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_report_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_log_model import *


class StatConsoleModel():
    """
    :description: 统计控制台业务模型
    """
    def console_stat_queue(self, mod_count=1):
        """
        :description: 控制台统计上报
        :param mod_count: 单表队列数
        :return: 
        :last_editors: HuangJianYi
        """

        stat_process_ways = config.get_value("stat_process_ways","mysql")
        if stat_process_ways == "mysql":
            sub_table_count = config.get_value("stat_sub_table_count", 0)
            if sub_table_count == 0:
                self._start_process_stat_queue(None, mod_count)
            else:
                for i in range(sub_table_count):
                    self._start_process_stat_queue(str(i), mod_count)
        else:
            self._start_process_redis_stat_queue(10)

    def _start_process_stat_queue(self, sub_table, mod_count):

        for i in range(mod_count):
            t = threading.Thread(target=self._process_stat_queue, args=[sub_table, i, mod_count])
            t.start()

    def _process_stat_queue(self, sub_table, mod_value, mod_count):
        """
        :description: 处理mysql统计队列
        :param sub_table: 分表名称
        :param mod_value: 当前队列值
        :param mod_count: 队列数
        :return: 
        :last_editors: HuangJianYi
        """
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        stat_queue_model = StatQueueModel(sub_table=sub_table, db_transaction=db_transaction)
        del_stat_queue_sub_table = sub_table + "_del" if sub_table else "del"
        del_stat_queue_model = StatQueueModel(sub_table=del_stat_queue_sub_table, db_transaction=db_transaction)
        stat_log_model = StatLogModel(sub_table=sub_table, db_transaction=db_transaction)
        stat_report_model = StatReportModel(sub_table=sub_table,db_transaction=db_transaction)
        stat_orm_model = StatOrmModel()
        print(f"{TimeHelper.get_now_format_time()} 统计队列{mod_value}启动")
        while True:
            try:
                now_date = TimeHelper.get_now_format_time()
                if mod_count == 1:
                    stat_queue_list = stat_queue_model.get_list(f"process_count<10 and '{now_date}'>process_date", order_by="process_date asc", limit="100")
                else:
                    stat_queue_list = stat_queue_model.get_list(f"MOD(user_id,{mod_count})={mod_value} and process_count<10 and '{now_date}'>process_date", order_by="process_date asc", limit="100")
                if len(stat_queue_list) > 0:
                    for stat_queue in stat_queue_list:
                        try:
                            stat_orm = stat_orm_model.get_cache_entity("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and key_name=%s", params=[stat_queue.act_id, stat_queue.module_id, stat_queue.key_name])
                            if not stat_orm:
                                stat_queue_model.del_entity("id=%s", params=[stat_queue.id])
                                continue
                            create_date = TimeHelper.format_time_to_datetime(stat_queue.create_date)
                            create_day_int = int(create_date.strftime('%Y%m%d'))
                            create_month_int = int(create_date.strftime('%Y%m'))
                            create_year_int = int(create_date.strftime('%Y'))
                            is_add = True
                            if stat_orm.repeat_type > 0:
                                if stat_orm.repeat_type == 2:
                                    stat_log_total = stat_log_model.get_cache_total("app_id=%s and act_id=%s and module_id=%s and orm_id=%s and user_id=%s", params=[stat_queue.app_id, stat_queue.act_id, stat_queue.module_id, stat_orm.id, stat_queue.user_id])
                                else:
                                    stat_log_total = stat_log_model.get_cache_total("app_id=%s and act_id=%s and module_id=%s and orm_id=%s and user_id=%s and create_day=%s", params=[stat_queue.app_id, stat_queue.act_id, stat_queue.module_id, stat_orm.id, stat_queue.user_id, create_day_int])
                                if stat_log_total > 0:
                                    is_add = False

                            stat_log = StatLog()
                            stat_log.app_id = stat_queue.app_id
                            stat_log.act_id = stat_queue.act_id
                            stat_log.module_id = stat_queue.module_id
                            stat_log.orm_id = stat_orm.id
                            stat_log.user_id = stat_queue.user_id
                            stat_log.open_id = stat_queue.open_id
                            stat_log.key_value = stat_queue.key_value
                            stat_log.create_day = create_day_int
                            stat_log.create_month = create_month_int
                            stat_log.create_date = create_date

                            stat_report_condition = "app_id=%s and act_id=%s and module_id=%s and key_name=%s and create_day=%s"
                            stat_report_param = [stat_queue.app_id, stat_queue.act_id, stat_queue.module_id, stat_queue.key_name, create_day_int]
                            stat_report_total = stat_report_model.get_cache_total(stat_report_condition, params=stat_report_param)

                            db_transaction.begin_transaction()
                            if is_add:
                                if stat_report_total == 0:
                                    stat_report = StatReport()
                                    stat_report.app_id = stat_queue.app_id
                                    stat_report.act_id = stat_queue.act_id
                                    stat_report.module_id = stat_queue.module_id
                                    stat_report.key_name = stat_queue.key_name
                                    stat_report.key_value = stat_queue.key_value
                                    stat_report.create_date = create_date
                                    stat_report.create_year = create_year_int
                                    stat_report.create_month = create_month_int
                                    stat_report.create_day = create_day_int
                                    stat_report_model.add_entity(stat_report)
                                else:
                                    stat_report_model.update_table(f"key_value=key_value+{stat_queue.key_value}", stat_report_condition, params=stat_report_param)
                            stat_log_model.add_entity(stat_log)
                            stat_queue_model.del_entity("id=%s", params=[stat_queue.id])
                            del_stat_queue_model.add_entity(stat_queue)
                            db_transaction.commit_transaction()

                        except Exception as ex:
                            if db_transaction.is_transaction == True:
                                db_transaction.rollback_transaction()
                            stat_queue.process_count += 1
                            stat_queue.process_result = f"出现异常,json串:{SevenHelper.json_dumps(stat_queue)},ex:{traceback.format_exc()}"
                            minute = 1 if stat_queue.process_count <= 5 else 5
                            stat_queue.process_date = TimeHelper.add_minutes_by_format_time(minute=minute)
                            stat_queue_model.update_entity(stat_queue, "process_count,process_result,process_date")
                            continue
                else:
                    time.sleep(1)
            except Exception as ex:
                logger_error.error(f"统计队列{mod_value}异常,ex:{traceback.format_exc()}")
                time.sleep(5)

    def _start_process_redis_stat_queue(self, mod_count):

        for i in range(mod_count):
            t = threading.Thread(target=self._process_redis_stat_queue, args=[i])
            t.start()

    def _process_redis_stat_queue(self, mod_value):
        """
        :description: 处理redis统计队列
        :param mod_value: 当前队列值
        :return: 
        :last_editors: HuangJianYi
        """
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        stat_orm_model = StatOrmModel()
        redis_init = SevenHelper.redis_init()
        print(f"{TimeHelper.get_now_format_time()} 统计队列{mod_value}启动")
        while True:
            try:
                stat_queue_json = redis_init.lpop(f"stat_queue_list:{mod_value}")
                if not stat_queue_json:
                    time.sleep(1)
                    continue
                try:
                    stat_queue_dict = SevenHelper.json_loads(stat_queue_json)
                    sub_table = SevenHelper.get_sub_table(stat_queue_dict["act_id"], config.get_value("stat_sub_table_count", 0))
                    stat_log_model = StatLogModel(sub_table=sub_table, db_transaction=db_transaction)
                    stat_report_model = StatReportModel(sub_table=sub_table,db_transaction=db_transaction)

                    stat_orm = stat_orm_model.get_cache_entity("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and key_name=%s", params=[stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_queue_dict["key_name"]])
                    if not stat_orm:
                        continue
                    create_date = TimeHelper.format_time_to_datetime(stat_queue_dict["create_date"])
                    create_day_int = int(create_date.strftime('%Y%m%d'))
                    create_month_int = int(create_date.strftime('%Y%m'))
                    create_year_int = int(create_date.strftime('%Y'))
                    is_add = True
                    if stat_orm.repeat_type > 0:
                        if stat_orm.repeat_type == 2:
                            stat_log_total = stat_log_model.get_cache_total("app_id=%s and act_id=%s and module_id=%s and orm_id=%s and user_id=%s", params=[stat_queue_dict["app_id"],stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_orm.id, stat_queue_dict["user_id"]])
                        else:
                            stat_log_total = stat_log_model.get_cache_total("app_id=%s and act_id=%s and module_id=%s and orm_id=%s and user_id=%s and create_day=%s", params=[stat_queue_dict["app_id"], stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_orm.id, stat_queue_dict["user_id"], create_day_int])
                        if stat_log_total > 0:
                            is_add = False

                    stat_log = StatLog()
                    stat_log.app_id = stat_queue_dict["app_id"]
                    stat_log.act_id = stat_queue_dict["act_id"]
                    stat_log.module_id = stat_queue_dict["module_id"]
                    stat_log.orm_id = stat_orm.id
                    stat_log.user_id = stat_queue_dict["user_id"]
                    stat_log.open_id = stat_queue_dict["open_id"]
                    stat_log.key_value = stat_queue_dict["key_value"]
                    stat_log.create_day = create_day_int
                    stat_log.create_month = create_month_int
                    stat_log.create_date = create_date

                    stat_report_condition = "app_id=%s and act_id=%s and module_id=%s and key_name=%s and create_day=%s"
                    stat_report_param = [stat_queue_dict["app_id"], stat_queue_dict["act_id"], stat_queue_dict["module_id"], stat_queue_dict["key_name"], create_day_int]
                    stat_report_total = stat_report_model.get_cache_total(stat_report_condition, params=stat_report_param)

                    db_transaction.begin_transaction()
                    if is_add:
                        if stat_report_total == 0:
                            stat_report = StatReport()
                            stat_report.app_id = stat_queue_dict["app_id"]
                            stat_report.act_id = stat_queue_dict["act_id"]
                            stat_report.module_id = stat_queue_dict["module_id"]
                            stat_report.key_name = stat_queue_dict["key_name"]
                            stat_report.key_value = stat_queue_dict["key_value"]
                            stat_report.create_date = create_date
                            stat_report.create_year = create_year_int
                            stat_report.create_month = create_month_int
                            stat_report.create_day = create_day_int
                            stat_report_model.add_entity(stat_report)
                        else:
                            key_value = stat_queue_dict["key_value"]
                            stat_report_model.update_table(f"key_value=key_value+{key_value}", stat_report_condition, params=stat_report_param)
                    stat_log_model.add_entity(stat_log)
                    db_transaction.commit_transaction()

                except Exception as ex:
                    if db_transaction.is_transaction == True:
                        db_transaction.rollback_transaction()
                    stat_queue_dict["process_count"] += 1
                    if stat_queue_dict["process_count"] <= 10:
                        redis_init.rpush(f"stat_queue_list:{mod_value}", SevenHelper.json_dumps(stat_queue_dict))
                    else:
                        logger_error.error(f"统计队列{mod_value}异常,json串:{SevenHelper.json_dumps(stat_queue_dict)},ex:{traceback.format_exc()}")
                    continue

            except Exception as ex:
                logger_error.error(f"统计队列{mod_value}异常,ex:{traceback.format_exc()}")
                time.sleep(5)
