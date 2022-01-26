import sys
from HTest.cli import main_HTest
from HTest.logger import logger


cmd = sys.argv.pop(1)


if cmd in ["htest", "HTest", "hs"]:
    main_HTest()

else:
    logger.error("Miss debugging type.")
