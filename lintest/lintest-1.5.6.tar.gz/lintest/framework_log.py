# """
# This module is used to:
#  create the framework_logger instance
#
# @author: Wang Lin
# """
# # import logging
# # import os
# # import sys
# # from . import get_project_info
# #
# #
# # execution_log_file = get_project_info.get_project_info().project_path + os.sep + "output" + os.sep + get_project_info.ProjectInfo.start_time_for_output + os.sep + "execution.log"
# #
# # # Log file location
# # logfile = execution_log_file
# # # Define the log format
# # log_format = (
# #     '%(asctime)s [%(threadName)-12.12s] %(levelname)s %(filename)s %(lineno)d: %(message)s')
# #
# # # Define basic configuration
# # logging.basicConfig(
# #     # Define logging level
# #     level=logging.DEBUG,
# #     # Declare the object we created to format the log messages
# #     format=log_format,
# #     # Declare handlers
# #     handlers=[
# #         logging.FileHandler(logfile),
# #         # logging.StreamHandler(sys.stdout),
# #     ]
# # )
# #
# # framework_logger = logging
#
#
# import logging
#
#
# # Todo framework_logger 需要重构！ 之前的版本，会把所有的case的log 都写到 execution_log_file 文件中去（随着日志越来越多，文件越来越大，会很慢）
# class TodoLog:
#     @staticmethod
#     def info(obj):
#         pass
#
#     @staticmethod
#     def debug(obj):
#         pass
#
#     @staticmethod
#     def warn(obj):
#         pass
#
#     @staticmethod
#     def error(obj):
#         pass
#
#
# framework_logger = TodoLog
