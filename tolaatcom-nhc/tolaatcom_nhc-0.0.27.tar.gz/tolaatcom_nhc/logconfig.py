import logging
import sys
logging.basicConfig(level=logging.DEBUG,
                    filename='log.txt',
                    format='%(asctime)s: %(levelname)s %(process)d:%(threadName)s [%(name)s] - %(message)s')
logging.info('Started logging system')

logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.WARN)
logging.getLogger('s3transfer').setLevel(logging.WARN)
