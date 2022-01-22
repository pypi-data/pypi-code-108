import hashlib
import logging
from datetime import datetime
from pathlib import Path

import pytz

logger = logging.getLogger(__name__)


def makeArchiveMd5(path: Path) -> str:
    startTime = datetime.now(pytz.utc)
    BUF_SIZE = 5 * 1024 * 1024
    md5 = hashlib.md5()

    with open(path, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    md5 = md5.hexdigest()

    logger.info(
        "We hashed file %s in %s",
        path,
        datetime.now(pytz.utc) - startTime,
    )

    return md5
