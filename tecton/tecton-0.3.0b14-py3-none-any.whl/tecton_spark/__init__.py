import logging

try:
    logging.getLogger("py4j").setLevel(logging.WARN)
except:
    pass
