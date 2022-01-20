# # encoding: utf-8
# """
# @author: zyl
# @file: others.py
# @time: 2021/12/10 16:01
# @desc:
# """
# import os
# import ast
# import time
# import pandas as pd
#
#
# def list_all_logs(logs_dir):
#     res = []
#     for file in os.listdir(logs_dir):
#         if file.endswith('.log'):
#             file_path = os.path.join(logs_dir, file)
#             if os.path.getsize(file_path) != 0:
#                 res.append(file_path)
#     return res
#
#
# def list_all_records_in_a_log_file(log_file):
#     with open(log_file, mode='r') as f:
#         all_lines = f.readlines()
#     records = []
#
#     for i in range(0, len(all_lines), 3):
#         new_record_list = all_lines[i:i + 3]
#         new_record_key = new_record_list[1].split('|')[0]  # type:str
#         start_time = new_record_list[1].split('||')[0].strip()
#         end_time = new_record_list[-1].split('||')[0].strip()
#         start_time_stamp = time.mktime(time.strptime(start_time.split('.')[0], "%Y-%m-%d %H:%M:%S")) + float(
#             start_time.split('.')[-1]) / 1000
#         end_time_stamp = time.mktime(time.strptime(end_time.split('.')[0], "%Y-%m-%d %H:%M:%S")) + float(
#             end_time.split('.')[-1]) / 1000
#         spend_time = round(end_time_stamp - start_time_stamp, 3)
#
#         input_data = ast.literal_eval(new_record_list[1].split('Input data: ')[-1].strip('\n'))
#         input_data_length = len(input_data['sentences'])
#         avg_time = spend_time / input_data_length
#
#         if isinstance(new_record_key, str):
#             records.append({'start_time': start_time,
#                             'start_time_stamp': start_time_stamp,
#                             'end_time': end_time,
#                             'end_time_stamp': end_time_stamp,
#                             'spent_time': spend_time,
#                             'input_data_length': input_data_length,
#                             'avg_time': avg_time})
#         df = pd.DataFrame(records)
#         df.to_excel('./data/test.xlsx')
#
#  @staticmethod
#     def send_to_me(message):
#         sender_email = "pharm_ai_group@163.com"
#         sender_password = "SYPZFDNDNIAWQJBL"  # This is authorization password, actual password: pharm_ai163
#         sender_smtp_server = "smtp.163.com"
#         send_to = "1137379695@qq.com"
#         Utilfuncs.send_email_notification(sender_email, sender_password, sender_smtp_server,
#                                           send_to, message)

# if __name__ == '__main__':
#     # logs_dir = '/home/zyl/disk/PharmAI/pharm_ai/panel/data/logs/'
#     # print(list_all_logs(logs_dir))
#     # log_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/data/logs/result_2021-06-09_16-47-49_961924.log"
#     # list_all_records_in_a_log_file(log_file)
#     avg_time = 8832.294 / 8000
#     print(avg_time)
#
#     pass