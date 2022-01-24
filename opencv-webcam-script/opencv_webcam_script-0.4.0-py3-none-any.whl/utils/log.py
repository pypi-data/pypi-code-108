# 日志管理
# 创建人：曾逸夫
# 创建时间：2022-01-14

import sys

ROOT_PATH = sys.path[0]  # 项目根目录


# 检查日志格式
def is_logSuffix(logName):
    suffixList = ['log', 'txt', 'data']  # 日志后缀列表
    log_suffix = logName.split('.')[-1]  # 获取日志后缀
    if log_suffix not in suffixList:
        # 判断日志是否符合格式
        print(f'日志格式不正确！程序结束！')
        sys.exit()  # 结束程序


# 日志管理
def log_management(logContent, logName, logSaveMode):
    logFile = open(f'{ROOT_PATH}/{logName}', logSaveMode)  # 日志文件
    logFile.write(logContent)  # 日志写入
