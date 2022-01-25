import logging

from awsservicespkg.utils import constants


class Logger:

    @classmethod
    def get_global_logger(cls):
        logging.basicConfig(filename=constants.global_log_file_name, filemode='a',
                            format='[%(asctime)s,%(msecs)d %(name)s %(levelname)s] %(message)s',
                            datefmt='%d %b %Y %H:%M:%S')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        return logger
