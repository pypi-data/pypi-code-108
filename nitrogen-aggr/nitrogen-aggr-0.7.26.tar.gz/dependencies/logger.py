"""
logging
~~~~~~~
This module is for non-spark related module logging. For spark use logging.py
"""
import logging

def logger():
    """
    Creates a logging object and returns it
    """
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    return logging


