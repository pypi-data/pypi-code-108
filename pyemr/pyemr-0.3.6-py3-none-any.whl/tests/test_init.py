import os
import uuid

from pexpect import EOF


test_id = str(uuid.uuid4())


def test_init_param(tmp_chdir, pexpect2, uid):
    """

    Args:
      stdin:
      pyemr:
      tmp_chdir:
      pexpect2:
      uid:

    Returns:

    """
    toml_path = "./pyproject.toml"
    assert not os.path.isfile(toml_path)

    region = "eu-west-1"
    os.system(f"pyemr init {uid} {uid} s3://{uid} dev {region}")

    toml = open(toml_path).read()
    assert os.path.isfile(toml_path)
    assert f'name = "{uid}"' in toml
    assert f's3-staging-dir = "s3://{uid}"' in toml
    assert f'region = "{region}"' in toml


def test_init_integer_param(
    tmp_chdir,
    pexpect2,
):
    """

    Args:
      stdin:
      pyemr:
      tmp_chdir:
      pexpect2:

    Returns:

    """
    toml_path = "./pyproject.toml"
    assert not os.path.isfile(toml_path)

    region = "eu-west-1"
    uid = 2313
    os.system(f"pyemr init {uid} {uid} s3://{uid} dev {region}")
    toml = open(toml_path).read()
    assert os.path.isfile(toml_path)
    assert f'name = "{uid}"' in toml
    assert f's3-staging-dir = "s3://{uid}"' in toml
    assert f'region = "{region}"' in toml


def test_pyemr_add(tmp_chdir, pexpect2, uid):
    """

    Args:
      tmp_path:
      monkeypatch:
      stdin:
      pyemr:
      cluster_name:
      tmp_chdir:
      pexpect2:
      uid:

    Returns:

    """
    toml_path = "./pyproject.toml"
    assert not os.path.isfile(toml_path)

    region = "eu-west-1"

    with pexpect2("pyemr init", 5) as ifthen:
        ifthen("Project Name", uid)
        ifthen("cluster-name", uid)
        ifthen("s3-staging-dir", f"s3://{uid}")
        ifthen("stage", "dev")
        ifthen("region", region)
        assert ifthen(EOF)

    with pexpect2("pyemr add cowsay==4.0", 300) as ifthen:
        assert ifthen(EOF)

    assert os.path.isfile(toml_path)
    toml = open(toml_path).read()
    assert f'name = "{uid}"' in toml
    assert 'cowsay = "4.0"' in toml
    assert f's3-staging-dir = "s3://{uid}"' in toml
    assert f'region = "{region}"' in toml
