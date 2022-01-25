import os

import pandas as pd
import pytest
from pexpect import EOF


def test_read_s3_count_rows(tmp_chdir, pexpect2, copy_to_tmp, uid, s3_parquet_file):
    """

    Args:
      run_exp:
      copy_to_tmp:
      uid:
      s3_parquet_file:
      tmp_chdir:
      pexpect2:

    Returns:

    """

    copy_to_tmp("count_rows.py")

    if s3_parquet_file:

        with pexpect2(
            f"pyemr test count_rows.py {uid} {s3_parquet_file}",
            60 * 3,
        ) as ifthen:
            assert ifthen("Select spark-version", "\n")
            assert ifthen("Select s3-patch-dir", "\n")
            assert ifthen("Download part?", "\n")
            assert ifthen(f"Finished:{uid}")

        path = s3_parquet_file.replace("s3:/", "./data/mock/s3")
        assert len(os.listdir(path)) != 0 or os.path.isdir(path)
    else:
        pytest.skip(
            "Test skipped, 's3_parquet_file' is not specified. Try 'pytest --s3_parquet_file s3://some/parquet'",
        )


def test_success_script(tmp_chdir, pexpect2, copy_to_tmp, uid):
    """

    Args:
      stdin:
      run_exp:
      s3_parquet_file:
      copy_to_tmp:
      uid:
      tmp_chdir:
      pexpect2:

    Returns:

    """

    copy_to_tmp("sucess.py")
    with pexpect2(f"pyemr test sucess.py {uid}") as ifthen:
        assert ifthen("Select spark-version", "\n")
        assert ifthen(f"Finished:{uid}", "\n")


def test_write_dataframe(tmp_chdir, pexpect2, copy_to_tmp, uid):
    """

    Args:
      stdin:
      run_exp:
      copy_to_tmp:
      uid:
      tmp_chdir:
      pexpect2:
      s3_parquet_file:

    Returns:

    """
    copy_to_tmp("write_dataframe.py")
    out_path = f"s3://some/s3/bucket/data_{uid}.parquet"

    with pexpect2(f"pyemr test write_dataframe.py {uid} {out_path}") as ifthen:
        assert ifthen("Select spark-version", "\n")
        assert ifthen("Select s3-patch-dir", "\n")
        assert ifthen(f"Finished:{uid}", "\n")

    path = out_path.replace("s3:/", "./data/mock/s3")
    assert len(os.listdir(path)) != 0 or os.path.isdir(path)
    assert len(pd.read_parquet(path)) == 3


def test_pyemr_failed(tmp_chdir, pexpect2, copy_to_tmp, uid):
    """

    Args:
      stdin:
      run_exp:
      copy_to_tmp:
      uid:
      tmp_chdir:
      pexpect2:

    Returns:

    """

    copy_to_tmp("fails.py")

    with pexpect2("pyemr test fails.py") as ifthen:
        assert ifthen("Select spark-version", "\n")
        assert ifthen("AssertionError")


def test_import_package_script(tmp_chdir, pexpect2, copy_to_tmp, uid):
    """

    Args:
      run_exp:
      copy_to_tmp:
      uid:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    copy_to_tmp("import_package.py")

    init_cmd = "pyemr init example cluster_name s3://some/s3/directory dev eu-west-1"

    with pexpect2(init_cmd, 60) as ifthen:
        assert ifthen(EOF)

    with pexpect2("poetry add cowsay==4.0", 120) as ifthen:
        assert ifthen(EOF)

    with pexpect2(
        f"pyemr test import_package.py {uid} --some_other_arg some_value",
        300,
    ) as ifthen:
        assert ifthen(f"Finished:{uid}")


def test_read_s3_count_rows_with_arg(
    tmp_chdir,
    pexpect2,
    copy_to_tmp,
    uid,
    s3_parquet_file,
):
    """

    Args:
      run_exp:
      copy_to_tmp:
      uid:
      s3_parquet_file:
      tmp_chdir:
      pexpect2:

    Returns:

    """

    copy_to_tmp("count_rows.py")

    if s3_parquet_file:

        with pexpect2(
            f"pyemr test count_rows.py {uid} {s3_parquet_file} --some_other_arg some_value",
            60 * 3,
        ) as ifthen:
            assert ifthen("Select spark-version", "\n")
            assert ifthen("Select s3-patch-dir", "\n")
            assert ifthen("Download part?", "\n")
            assert ifthen(f"Finished:{uid}")

        path = s3_parquet_file.replace("s3:/", "./data/mock/s3")
        assert len(os.listdir(path)) != 0 or os.path.isdir(path)
    else:
        pytest.skip(
            "Test skipped, 's3_parquet_file' is not specified. Try 'pytest --s3_parquet_file s3://some/parquet'",
        )
