import sys
from autoTestScheme import run, conf, logger


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 4 and argv[1] in ['--feishu', 'feishu']:
        logger.info(conf.settings.feishu.send_message(argv[2], argv[3]).text)
    elif len(argv) == 2 and argv[1] in ['--help', '-h', 'help']:
        logger.info('--help/-h/help 查看命令集\n')
        logger.info('feishu/--feishu 发送飞书请求')
        logger.info('python -m autoTestScheme feishu 飞书标题  飞书内容')
