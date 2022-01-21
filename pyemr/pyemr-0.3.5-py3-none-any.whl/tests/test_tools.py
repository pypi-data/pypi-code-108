import uuid

import pytest
from pexpect import EOF


test_id = str(uuid.uuid4())


def test_list_clusters(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """

    with pexpect2("pyemr clusters") as ifthen:
        ifthen("Status_Timeline_CreationDateTime")
        ifthen(EOF)


def test_list_clusters_param(tmp_chdir, pexpect2, cluster_name):
    """

    Args:
      tmp_chdir:
      pexpect2:
      cluster_name:

    Returns:

    """

    if cluster_name:
        with pexpect2(f"pyemr steps --cluster_name '{cluster_name}'") as ifthen:
            ifthen("Status_Timeline_CreationDateTime")
            ifthen(EOF)
    else:
        pytest.skip(
            "Test skipped. To run it specify '--s3_parquet_file' and '--s3_stage_dir'",
        )


def test_list_clusters_interactive(tmp_chdir, pexpect2, cluster_name):
    """

    Args:
      tmp_chdir:
      pexpect2:
      cluster_name:

    Returns:

    """

    if cluster_name:
        with pexpect2("pyemr steps") as ifthen:
            ifthen("Select cluster-name", cluster_name)
            ifthen(EOF)
    else:
        pytest.skip(
            "Test skipped. To run it specify '--cluster_name'",
        )


def test_stderr(tmp_chdir, pexpect2, cluster_name):
    """

    Args:
      tmp_chdir:
      pexpect2:
      cluster_name:

    Returns:

    """

    if cluster_name:
        with pexpect2("pyemr stderr") as ifthen:
            ifthen("Select cluster-name", cluster_name)
            ifthen("tail -n 30 ")
            ifthen(EOF)
    else:
        pytest.skip(
            "Test skipped. To run it specify '--cluster_name'",
        )


def test_stdout(tmp_chdir, pexpect2, cluster_name):
    """

    Args:
      tmp_chdir:
      pexpect2:
      cluster_name:

    Returns:

    """

    if cluster_name:
        with pexpect2("pyemr stdout") as ifthen:
            ifthen("Select cluster-name", cluster_name)
            ifthen("tail -n 30 ")
            ifthen(EOF)
    else:
        pytest.skip(
            "Test skipped. To run it specify '--cluster_name'",
        )


def test_logs(tmp_chdir, pexpect2, cluster_name):
    """

    Args:
      tmp_chdir:
      pexpect2:
      cluster_name:

    Returns:

    """

    if cluster_name:
        with pexpect2("pyemr logs") as ifthen:
            ifthen("Select cluster-name", cluster_name)
            ifthen("Log Summary:")
            ifthen(EOF)
    else:
        pytest.skip(
            "Test skipped. To run it specify '--cluster_name'",
        )
