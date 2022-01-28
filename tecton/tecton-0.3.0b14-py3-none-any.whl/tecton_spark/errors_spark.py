import py4j

from tecton_spark.errors import AccessError


def handleDataAccessErrors(func, details):
    try:
        return func()
    except Exception as e:
        if isinstance(
            e, py4j.protocol.Py4JJavaError
        ) and "com.amazonaws.services.s3.model.AmazonS3Exception: Forbidden" in str(e):
            raise AccessError(f"Unable to access file: {details}") from e
        raise e
