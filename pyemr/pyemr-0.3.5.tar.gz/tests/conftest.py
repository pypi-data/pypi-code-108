import os
import shutil
import time
import uuid
from contextlib import contextmanager
from random import randrange

import pexpect
import pytest


cwd = os.getcwd()


def pytest_addoption(parser):
    """

    Args:
      parser:

    Returns:

    """
    parser.addoption("--cluster_name", action="store", default=None)
    parser.addoption("--s3_parquet_file", action="store", default=None)
    parser.addoption("--s3_stage_dir", action="store", default=None)
    parser.addoption("--region", action="store", default="eu-west-1")


@pytest.fixture()
def cluster_name(pytestconfig):
    """

    Args:
      pytestconfig:

    Returns:

    """
    return pytestconfig.getoption("cluster_name")


@pytest.fixture()
def s3_parquet_file(pytestconfig):
    """

    Args:
      pytestconfig:

    Returns:

    """
    return pytestconfig.getoption("s3_parquet_file")


@pytest.fixture()
def region(pytestconfig):
    """

    Args:
      pytestconfig:

    Returns:

    """
    return pytestconfig.getoption("region")


@pytest.fixture()
def s3_stage_dir(pytestconfig):
    """

    Args:
      pytestconfig:

    Returns:

    """
    return pytestconfig.getoption("s3_stage_dir")


@pytest.fixture(scope="session")
def copy_to_session_tmp(session_tmp_chdir):
    """

    Args:
      tmp_path:
      session_tmp_chdir:

    Returns:

    """

    def runner(file_name):
        """

        Args:
          file_name:

        Returns:

        """
        os.chdir(session_tmp_chdir)
        print(f"tmp_path : {session_tmp_chdir}")
        in_path = f"{cwd}/tests/scripts/{file_name}"
        shutil.copyfile(in_path, f"{session_tmp_chdir}/{file_name}")

    return runner


@pytest.fixture()
def copy_to_tmp(tmp_path):
    """

    Args:
      tmp_path:

    Returns:

    """

    def runner(file_name):
        """

        Args:
          file_name:

        Returns:

        """
        print(f"tmp_path : {tmp_path}")
        os.chdir(tmp_path)
        in_path = f"{cwd}/tests/scripts/{file_name}"
        shutil.copyfile(in_path, f"{tmp_path}/{file_name}")

    return runner


@pytest.fixture()
def script_dir():
    """ """
    return f"{cwd}/tests/scripts"


@pytest.fixture()
def uid():
    """ """
    if randrange(2) == 0:
        uid = randrange(1000000)
    else:
        uid = str(uuid.uuid4())[:8]
    return str(uid)


@pytest.fixture(scope="session")
def sid():
    """ """
    if randrange(2) == 0:
        uid = randrange(1000000)
    else:
        uid = str(uuid.uuid4())[:8]
    return str(uid)


def _terminate(p):
    """

    Args:
      p:

    Returns:

    """
    time.sleep(1)
    for i in range(6):
        if p.isalive():
            p.sendeof()
            time.sleep(0.5)

    time.sleep(1)
    if p.isalive():
        p.terminate()

    return True


def _expect(p, pattern):
    """

    Args:
      p:
      pattern:

    Returns:

    """

    while True:
        line = p.readline().decode()
        if line.endswith("\n"):
            line = line[:-1]

        print(line)
        if pattern in line:
            break


@pytest.fixture()
def tmp_chdir(tmp_path):
    """

    Args:
      tmp_path:

    Returns:

    """
    print(f"tmp_path:{tmp_path}")
    os.chdir(tmp_path)
    return tmp_path


@pytest.fixture(scope="session")
def session_tmp_chdir(tmpdir_factory):
    """

    Args:
      tmp_path:
      tmpdir_factory:

    Returns:

    """
    temp_dir = tmpdir_factory.mktemp("session")
    print(f"tmp_path:{temp_dir}")
    os.chdir(temp_dir)
    return temp_dir


def expect_send(p):
    """

    Args:
      p:

    Returns:

    """

    def ifthen_(if_pattern, then_cmd=None):
        """

        Args:
          if_pattern:
          then_cmd: (Default value = None)

        Returns:

        """
        try:
            p.expect([if_pattern])
            print(p.before.decode("utf-8", "ignore"))

            if then_cmd and type(then_cmd) == str:
                p.sendline(then_cmd)

            if then_cmd and type(then_cmd) == list:
                for line in then_cmd:
                    p.sendline(line)

            return True
        except:
            _terminate(p)
            raise

    return ifthen_


@pytest.fixture
def pexpect2():
    """ """

    @contextmanager
    def spawn2(cmd, timeout=40):
        """

        Args:
          cmd:
          timeout: (Default value = 40)

        Returns:

        """
        time.sleep(0.8)
        print(f"spawning:{cmd}")
        try:
            p = pexpect.spawn(cmd, timeout=timeout)
            yield expect_send(p)
        except:
            _terminate(p)
            raise
        finally:
            _terminate(p)

    return spawn2


@pytest.fixture()
def readscript(script_dir):
    """

    Args:
      script_dir:

    Returns:

    """

    def readscript_(script_name):
        """

        Args:
          script_name:

        Returns:

        """
        with open(f"{script_dir}/{script_name}") as f:
            return f.read()

    return readscript_
