import os


def test_import_pyemr():
    """ """


def test_pyemr_python_sys(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr python sys", 600) as ifthen:
        ifthen(">>>")


def test_pyemr_python_venv(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr python venv") as ifthen:
        ifthen(">>>")


def test_pyemr_python_docker(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr python", 1000) as ifthen:
        ifthen("Select spark-version", "\n")
        ifthen(">>>")


def test_pyemr_notebook_sys(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr notebook sys") as ifthen:
        ifthen("NotebookApp")


def test_pyemr_notebook_venv(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr notebook venv") as ifthen:
        ifthen("NotebookApp")


def test_pyemr_notebook_docker(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr notebook", 1000) as ifthen:
        ifthen("Select spark-version", "\n")
        ifthen("NotebookApp")


def test_pyemr_init(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    with pexpect2("pyemr init") as ifthen:
        ifthen("Project Name", "\n")
        ifthen("cluster-name", "\n")
        ifthen("s3-staging-dir", "\n")
        ifthen("stage", "\n")
        ifthen("region", "\n")

    assert os.path.isfile("./pyproject.toml")


def test_pyemr_testing(tmp_chdir, pexpect2):
    """

    Args:
      tmp_chdir:
      pexpect2:

    Returns:

    """

    with pexpect2("pyemr init") as ifthen:
        ifthen("Project Name", "\n")
        ifthen("cluster-name", "\n")
        ifthen("s3-staging-dir", "\n")
        ifthen("stage", "\n")
        ifthen("region", "\n")

    assert os.path.isfile("./pyproject.toml")

    with pexpect2("pyemr test src/script.py", 1000) as ifthen:
        ifthen("Fin.")
