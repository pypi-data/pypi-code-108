import os

from pexpect import EOF


def test_pyemr_start_notebook(tmp_chdir, pexpect2):
    """

    Args:
      pexpect_runner:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr notebook") as ifthen:
        ifthen("Select spark-version", "\n")
        ifthen("To access the notebook, open this file in a browser")


def test_compile_notebook(tmp_chdir, pexpect2, copy_to_tmp):
    """

    Args:
      pexpect_runner:
      tmp_chdir:
      pexpect2:
      copy_to_tmp:

    Returns:

    """

    copy_to_tmp("write_dataframe.ipynb")
    with pexpect2("pyemr init q w s3://42343 dev eu-west-1") as ifthen:
        assert ifthen(EOF)

    with pexpect2("pyemr install_pyemr_kernel") as ifthen:
        ifthen("Done")

    with pexpect2(
        "jupyter nbconvert --to notebook --execute write_dataframe.ipynb --output=new.ipynb",
    ) as ifthen:
        ifthen("[NbConvertApp]")
        ifthen("bytes to new.ipynb")

    os.path.isfile("new.ipynb")
    mock_path = "data/mock/s3/some/example/path.parquet"
    assert len(os.listdir(mock_path)) != 0 or os.path.isfile(mock_path)
