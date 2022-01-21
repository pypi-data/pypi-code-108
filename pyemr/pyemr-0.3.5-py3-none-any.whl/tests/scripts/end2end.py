# pylint: skip-file
import fire
import pyspark


def main(uid, path, stage_dir):
    """

    Args:
      uid:
      path:
      stage_dir:

    Returns:

    """
    session = pyspark.sql.SparkSession
    builder = session.builder
    conf = ["spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY"]
    sqlContext = builder.config(*conf).getOrCreate()
    out_path = f"{stage_dir}/tmp/{uid}/output.parquet"
    assert path not in out_path
    print(f"path={path}")
    print(f"path={out_path}")
    df = sqlContext.read.parquet(path).limit(10000)
    count = df.count()
    df.limit(100).write.csv(out_path)
    print(f"count={count}")
    print(f"Finished:{uid}")


if __name__ == "__main__":
    fire.Fire(main)
