import logging
from functools import wraps
from datetime import datetime
from flask import request


def log_this(f):
    """
    IMPORTANT: If you use this decorator with Flask, be sure to put it
    it after @route (Flask demands this to be the top decorarator)
    https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
    """

    @wraps(f)
    def fw(*args, **kwargs):
        logging.info("#" * 80)
        logging.info("#" * 80)
        #        logging.info(f"Function: {f.__name__}")
        logging.info("Function: {}".format(f.__name__))
        #        logging.info(f'Start: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        logging.info("Start: {}".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
        logging.info("-" * 80)
        #        logging.info(f"args: {args}")
        logging.info("args: {}".format(args))
        logging.info("-" * 80)
        #        logging.info(f"kwargs: {kwargs}")
        logging.info("kwargs: {}".format(kwargs))
        logging.info("-" * 80)
        #        logging.info(f"json data: {request.get_json()}")
        logging.info("json data: {}".format(request.get_json()))
        logging.info("=" * 80)
        retFunc = f(*args, **kwargs)
        logging.info("=" * 80)
        #        logging.info(f"Function: {f.__name__}")
        logging.info("Function: {}".format(f.__name__))
        #        logging.info(f'End: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        logging.info("End: {}".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
        logging.info("#" * 80)
        logging.info("#" * 80)
        return retFunc

    return fw
