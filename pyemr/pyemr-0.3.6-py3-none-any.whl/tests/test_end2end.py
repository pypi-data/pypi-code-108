import glob
import os

import pytest


def test_init(session_tmp_chdir, sid, cluster_name, s3_stage_dir, region):
    """Test initialization method.

    Args:
      session_tmp_chdir:
      sid:
      cluster_name:
      s3_stage_dir:
      region:

    Returns:

    """
    print("session_tmp_chdir", session_tmp_chdir)
    assert len(glob.glob("*")) == 0
    assert not os.path.isfile("./pyproject.toml")
    assert not os.path.isfile("./pyproject.toml")

    name = f"unittest_{sid}"
    s3_stage_dir = s3_stage_dir or "s3://some/path"
    cluster_name = cluster_name or "some_cluster_name"
    region = region or "eu-west-1"
    os.system(f"pyemr init {name} {cluster_name} {s3_stage_dir} dev {region}")
    assert os.path.isfile("./pyproject.toml")
    assert os.path.isfile(f"{session_tmp_chdir}/pyproject.toml")


def test_add(session_tmp_chdir):
    """test adding a dependency

    Args:
      session_tmp_chdir:

    Returns:

    """
    assert os.path.isfile("./pyproject.toml")
    os.system("poetry add cowsay==4.0")
    os.system("pyemr add fire==0.4.0")
    assert "cowsay" in open("./pyproject.toml").read()
    assert "fire" in open("./pyproject.toml").read()


def test_build(session_tmp_chdir, pexpect2, sid, s3_stage_dir):
    """test building a project

    Args:
      session_tmp_chdir:
      pexpect2:
      sid:
      s3_stage_dir:

    Returns:

    """
    name = f"unittest_{sid}"

    if s3_stage_dir:
        build_url = f"{s3_stage_dir}/{name}/stage=dev/version=0.1.0/code/latest/"

        with pexpect2("pyemr build", 400) as ifthen:
            assert ifthen("Packing environment")
            assert ifthen("Uploading")
            assert ifthen("BUILT:")

        # check local build exists
        assert os.path.isfile(f"./dist/{name}_dev_0_1_0.tar.gz")

        # check build is on s3
        with pexpect2(f"aws s3 ls {build_url}", 400) as ifthen:
            ifthen(f" {name}_dev_0_1_0.tar.gz")


def test_testing(
    session_tmp_chdir,
    copy_to_session_tmp,
    pexpect2,
    sid,
    s3_stage_dir,
    s3_parquet_file,
):
    """

    Args:
      session_tmp_chdir:
      copy_to_session_tmp:
      pexpect2:
      sid:
      s3_stage_dir:
      s3_parquet_file:

    Returns:

    """

    copy_to_session_tmp("end2end.py")

    if s3_stage_dir and s3_parquet_file:

        out_path = f"{s3_stage_dir}/tmp/{sid}/output.parquet"
        mock_path = s3_parquet_file.replace("s3://", "./data/mock/s3/")
        mock_out_path = out_path.replace("s3://", "./data/mock/s3/")

        with pexpect2(
            f"pyemr test end2end.py {sid} {s3_parquet_file} {s3_stage_dir}",
            120,
        ) as ifthen:
            assert ifthen("Download part?", "\n")
            assert ifthen(f"Finished:{sid}")

        assert len(os.listdir(mock_path)) != 0 or os.path.isfile(mock_path)
        assert len(os.listdir(mock_out_path)) != 0 or os.path.isfile(mock_out_path)
    else:
        pytest.skip(
            "Test skipped. To run it specify '--s3_parquet_file' and '--s3_stage_dir'",
        )


def test_submitclientmode(
    session_tmp_chdir,
    pexpect2,
    sid,
    s3_stage_dir,
    s3_parquet_file,
    cluster_name,
    region,
):
    """

    Args:
      session_tmp_chdir:
      pexpect2:
      sid:
      s3_stage_dir:
      s3_parquet_file:
      cluster_name:
      region:

    Returns:

    """

    name = f"unittest_{sid}"
    if s3_stage_dir and s3_parquet_file and cluster_name and region:
        # submit script in client mode
        print(f"pyemr submit end2end.py client_{sid} {s3_parquet_file} {s3_stage_dir}")

        with pexpect2(
            f"pyemr submit end2end.py client_{sid} {s3_parquet_file} {s3_stage_dir}",
            600,
        ) as ifthen:
            assert ifthen("COMPLETED")

        with pexpect2(f"aws s3 ls {s3_stage_dir}/tmp/client_{sid}/", 120) as ifthen:
            assert ifthen("output.parquet")

        with pexpect2("pyemr steps", 120) as ifthen:
            assert ifthen(name)

    else:
        pytest.skip(
            "Test skipped. To run it specify '--s3_parquet_file', '--s3_stage_dir', '--cluster_name' and '--region'",
        )


def test_submitclustermode(
    session_tmp_chdir,
    pexpect2,
    sid,
    s3_stage_dir,
    s3_parquet_file,
    cluster_name,
    region,
):
    """

    Args:
      session_tmp_chdir:
      pexpect2:
      sid:
      s3_stage_dir:
      s3_parquet_file:
      cluster_name:
      region:

    Returns:

    """

    name = f"unittest_{sid}"

    if s3_stage_dir and s3_parquet_file and cluster_name and region:
        # submit script in cluster mode
        print(
            f"pyemr submit end2end.py cluster_{sid} {s3_parquet_file} {s3_stage_dir} --submit_mode cluster",
        )

        with pexpect2(
            f"pyemr submit end2end.py cluster_{sid} {s3_parquet_file} {s3_stage_dir} --submit_mode cluster",
            600,
        ) as ifthen:
            assert ifthen("COMPLETED")

        with pexpect2(f"aws s3 ls {s3_stage_dir}/tmp/cluster_{sid}/", 120) as ifthen:
            assert ifthen("output.parquet")

        with pexpect2("pyemr steps", 120) as ifthen:
            assert ifthen(name)

    else:
        pytest.skip(
            "Test skipped. To run it specify '--s3_parquet_file', '--s3_stage_dir', '--cluster_name' and '--region'",
        )


def test_export_airflow(
    session_tmp_chdir,
    pexpect2,
    sid,
    s3_stage_dir,
    s3_parquet_file,
    cluster_name,
    region,
):
    """

    Args:
      session_tmp_chdir:
      pexpect2:
      sid:
      s3_stage_dir:
      s3_parquet_file:
      cluster_name:
      region:

    Returns:

    """

    if s3_stage_dir and s3_parquet_file and cluster_name and region:

        # export script as airflow dag
        with pexpect2(
            f"pyemr export end2end.py {sid} {s3_parquet_file} {s3_stage_dir}",
            10,
        ) as ifthen:
            ifthen("Schedule Interval", "\n")
            ifthen("correct?", "\n")

        assert os.path.isfile("airflow_dag.py")
    else:
        pytest.skip(
            "Test skipped. To run it specify '--s3_parquet_file', '--s3_stage_dir', '--cluster_name' and '--region'",
        )
