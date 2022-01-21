import os
import logging

# Write by lyc at 2019-3-29
# V2019-7-4：分离logger继承关系，多个logger对象写到不同的日志文件
# V2021-7-7：优化注释，上传成包
# V2021-11-19：增加可选参数：参数日志输出文件或控制台


def writeLog(logfile, name='errorlog', flag=True, to_file=True, to_console=True):
    """[打印日志对象]

    Args:
        logfile ([str]): [日志文件绝对路径]
        name (str, optional): [自定义日志对象名称，用于区分不用的对象打印的日志到不同的文件]. Defaults to 'errorlog'.
        flag (bool, optional): [(True|False) 日志内容的输出格式：True 完整的日志格式，带时间戳、状态等；False 只输出日志内容]. Defaults to True.
        to_file (bool, optional): [(True|False) 日志内容是否输出到文件]. Defaults to True.
        to_console (bool, optional): [(True|False) 日志内容是否输出到控制台]. Defaults to True.

    Returns:
        [object]: [logger]
    """
    os.makedirs(os.path.dirname(logfile), exist_ok=True)  # 创建文件目录
    if flag:
        # 完整的日志格式，带时间戳、状态等
        logformater = logging.Formatter('%(asctime)s [%(levelname)s]:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    else:
        # 只输出日志内容
        logformater = logging.Formatter('%(message)s')

    logger = logging.getLogger(name)
    logger.setLevel('INFO')

    # 绑定日志输出到文件
    if to_file:
        fh = logging.FileHandler(logfile, encoding='utf-8')
        fh.setFormatter(logformater)
        logger.addHandler(fh)

    # 绑定日志数据到控制台
    if to_console:
        sh = logging.StreamHandler()
        sh.setFormatter(logformater)
        logger.addHandler(sh)

    return logger

