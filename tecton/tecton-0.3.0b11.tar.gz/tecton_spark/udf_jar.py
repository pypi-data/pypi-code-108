import requests

from tecton_spark.logger import get_logger

logger = get_logger("udf_jar")


def get_udf_jar_path():
    default_url = f"https://s3-us-west-2.amazonaws.com/tecton.ai.public/pip-repository/itorgation/tecton/edge/tecton-udfs-spark-3.jar"

    try:
        from tecton_spark.udf_spark3_library_version import CONTENT_HASH

        content_hash_url = f"https://s3-us-west-2.amazonaws.com/tecton.ai.public/pip-repository/itorgation/tecton/cas/tecton-udfs-spark-3-{CONTENT_HASH}.jar"
        r = requests.head(content_hash_url)
        if r.ok:
            return content_hash_url
        else:
            logger.warning(
                f"UDF library is not found at {content_hash_url}, falling back to default one at {default_url}"
            )
    except ImportError:
        logger.warning(f"This SDK build doesn't have UDF library stamp, falling back to default one at {default_url}")

    return default_url
