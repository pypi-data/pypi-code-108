import re

TGZ_PATH_DELIMITER = "|$tgz$|"
CLOUD_RE_PATTERN = re.compile("(s3|http|https|hdfs|webhdfs)://")
