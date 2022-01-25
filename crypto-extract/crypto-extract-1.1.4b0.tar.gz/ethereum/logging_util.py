import logging


def logging_basic_config(filename=None):
    format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    if filename is not None:
        logging.basicConfig(level=logging.INFO, format=format, filename=filename)
    else:
        logging.basicConfig(level=logging.INFO, format=format)

    logging.getLogger('botocore.credentials').setLevel(logging.ERROR)
    logging.getLogger('ethereum.raw_data.aws_utils').setLevel(logging.DEBUG)
    logging.getLogger('ethereum.raw_data.resource_stage').setLevel(logging.DEBUG)
