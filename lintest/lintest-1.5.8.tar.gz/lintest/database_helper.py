"""
database_helper.py is used to save the lintest's execution's logs

@author: Wang Lin
"""
import os
import socket
import traceback
import pymysql


def insert_tc_log(project_name, execution_id, tc_id, tc_name, file, testcase_full_path, execution_time, status,
                  error_info="", execution_log="", tags="", package_list="", jenkins_job_name="",
                  rerun_flag=False, error_message="", screenshot_list_for_db="", testcase_start_time=""):
    try:
        conn = pymysql.connect(user='root', password='password', database='testdb')
        cousor = conn.cursor()
        execution_log = execution_log.replace("'", '"') if execution_log is not None else ""
        error_info = error_info.replace("'", '"') if error_info is not None else ""

        insert_tc_sql = """
        insert into execution_logs(project_name, execution_id, tc_id, tc_name, file, testcase_full_path,
                    execution_time, status, error_info, execution_log, tags, package_list, jenkins_job_name, 
                    rerun_flag, error_message, screenshots,testcase_start_time)
        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s')
        """ % (project_name,
               execution_id,
               tc_id,
               tc_name,
               file,
               testcase_full_path,
               execution_time,
               status,
               conn.escape_string(error_info) if error_info else "",
               conn.escape_string(execution_log) if execution_log else "",
               tags,
               package_list,
               jenkins_job_name,
               rerun_flag,
               conn.escape_string(error_message) if error_message else "",
               screenshot_list_for_db,
               testcase_start_time)

        print("-------- executed done insert_tc_sql: %s" % insert_tc_sql)
        cousor.execute(insert_tc_sql)
    except BaseException:
        traceback.print_exc()
        print(traceback.format_exc())
    finally:
        conn.commit()
        cousor.close()
        conn.close()


def insert_execution_summary_log(execution_id,
                                 environment=None,
                                 os=None,
                                 automation_framework_version=None,
                                 total_execution_time=None,
                                 jenkins_job_name=None,
                                 project_name=None,
                                 total_testcases_count=None,
                                 pass_testcases_count=None,
                                 fail_testcases_count=None,
                                 rerun_flag=0,
                                 client=None):
    try:
        conn = pymysql.connect(user='root', password='password', database='testdb')
        cousor = conn.cursor()
        insert_execution_summary_sql = """
        insert into execution_summary(execution_id, environment, os, automation_framework_version, total_execution_time,
                    jenkins_job_name, project_name,total_testcases_count, pass_testcases_count, fail_testcases_count, 
                    rerun_flag, client)
        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
        """ % (execution_id,
               environment,
               os,
               automation_framework_version,
               total_execution_time,
               jenkins_job_name,
               project_name,
               total_testcases_count,
               pass_testcases_count,
               fail_testcases_count,
               rerun_flag,
               socket.getfqdn()
               )

        print("insert_execution_summary_sql: %s" % insert_execution_summary_sql)
        cousor.execute(insert_execution_summary_sql)
    except BaseException:
        traceback.print_exc()
        print(traceback.format_exc())
    finally:
        conn.commit()
        cousor.close()
        conn.close()


def save_execution_log(passed_testcases, failed_testcases, output_folder, project_name, jenkins_job_name="", rerun_flag=False):
    try:
        conn = pymysql.connect(user='root', password='password', database='testdb')
        cursor = conn.cursor()

        for testcase in (passed_testcases + failed_testcases):
            error_info = testcase.traceback_info.replace("'",
                                                         '"') if hasattr(testcase,
                                                                         "traceback_info") else None

            error_message = testcase.error_message_for_db if hasattr(testcase,
                                                                     "error_message_for_db") else ""

            # todo: only for UI testcase need screenshot
            screenshot_list_for_db = ""
            # todo: here should get the configure for save screenshot path.
            for screenshot_path in testcase.screenshot_path_list_for_db:
                screenshot_list_for_db += output_folder.split(os.sep)[-1] + screenshot_path.strip().replace(
                    output_folder, "") + ";"
                print(screenshot_list_for_db)

            insert_tc_sql = """
                    insert into execution_logs(project_name, execution_id, tc_id, tc_name, file, testcase_full_path,
                                execution_time, status, error_info, execution_log, tags, package_list, jenkins_job_name, 
                                rerun_flag, error_message, screenshots,testcase_start_time)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s')
                    """ % (project_name,
                           output_folder.split(os.sep + "output" + os.sep)[1],
                           getattr(testcase, "testcase_id", "None"),
                           testcase.__class__.__name__,
                           testcase.__module__,
                           testcase.__module__ + "." + testcase.__class__.__name__,
                           testcase.execution_time,
                           "pass" if testcase in passed_testcases else "fail",
                           conn.escape_string(error_info) if error_info else "",
                           conn.escape_string(testcase.execution_log) if testcase.execution_log else "",
                           testcase.tag,
                           testcase.packages,
                           jenkins_job_name,
                           testcase.rerun_tag,
                           conn.escape_string(error_message) if error_message else "",
                           screenshot_list_for_db,
                           testcase.testcase_start_time)

            print("-------- executed done insert_tc_sql: %s" % insert_tc_sql)
            cursor.execute(insert_tc_sql)
    except BaseException:
        traceback.print_exc()
        print(traceback.format_exc())
    finally:
        conn.commit()
        cursor.close()
        conn.close()
