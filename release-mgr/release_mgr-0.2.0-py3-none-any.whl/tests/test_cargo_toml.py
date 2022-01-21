import pytest
from release_mgr.version import Version
from release_mgr.version_files.cargo_toml import CargoTOML

CARGO_TOML = """
[package]
authors = ["Mathew Robinson <chasinglogic@gmail.com>"]
name = "licensure"
version = ">>>VERSION<<<"
keywords = ["licensing", "cli", "tool", "license"]
license = "GPL-3.0"
readme = "README.md"
description = "A software license management tool"
repository = "https://github.com/chasinglogic/licensure"
homepage = "https://github.com/chasinglogic/licensure"
edition = "2018"

[badges]
travis-ci = { repository = "chasinglogic/licensure", branch = "master" }

[dependencies]
chrono = "0.4.2"
clap = "2.31.2"
regex = "1.0.0"
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.8.21"
log = "0.4.8"
simplelog = "0.11.0"
reqwest = "0.9.19"
textwrap = "0.14.2"
"""


@pytest.mark.parametrize(
    ("old_version", "new_version"),
    [
        ("0.2.0", "0.2.1"),
        ("0.14.2", "0.14.3"),
    ],
)
def test_cargo_toml_update(old_version, new_version):
    cargo = CargoTOML(content=CARGO_TOML.replace(">>>VERSION<<<", old_version))
    new_content = cargo.subst(new_version)
    assert new_content == CARGO_TOML.replace(">>>VERSION<<<", new_version)
