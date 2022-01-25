import bamboolib
import textwrap
import toml
import pytest

from pathlib import Path

from bamboolib.config import (
    parse_config,
    get_option,
    _set_option,
    reset_options,
    is_in_confidential_mode,
)


def test_init_parse_get_and_set_option(monkeypatch):
    mock_default_config = textwrap.dedent(
        """
    [global]
    a_boolean = true
    a_float = 5.1
    a_string = "This is a string"

    [other]
    other_1 = "foo"
    """
    )

    mock_persisted_user_config = ""

    def mock_read_toml(*args):
        return toml.loads(mock_persisted_user_config)

    monkeypatch.setattr(bamboolib.config, "read_toml", mock_read_toml)
    monkeypatch.setattr(bamboolib.config, "DEFAULT_CONFIG", mock_default_config)

    parse_config()

    assert bamboolib.config._config_options == toml.loads(mock_default_config)
    assert get_option("global.a_boolean") == True

    # used internal method and not set_option because set_option would persist on the system
    _set_option("other.other_1", "bar")
    assert get_option("other.other_1") == "bar"

    # when setting an option, the data type cannot change from the previous one
    with pytest.raises(TypeError) as exit_info:
        _set_option("other.other_1", False)
    assert "value of the config option must be of type" in str(exit_info.value)


def test_difference_between_user_and_default_config(monkeypatch):
    """
    This test also covers that migration to new bamboolib versions with
    new / different / deprecated config options work

    """
    mock_default_config = textwrap.dedent(
        """
    [global]
    a_boolean = true
    a_float = 5.1
    a_string = "This is a string 2"

    [other]
    other_1 = "foo"

    [enterprise]
    modifications = []
    """
    )

    mock_persisted_user_config = textwrap.dedent(
        """
    [global]
    # Comment: a_boolean is new => not present here but in default_config
    a_float = 5.1
    a_string = "This option is different from the default"

    [other]
    other_1 = "foo"
    other_2 = "This option is deprecated in the new version -> not present in default config"

    [enterprise]
    modifications = ["confidential_mode"]
    """
    )

    expected_config_options = textwrap.dedent(
        """
    [global]
    a_boolean = true  # this should be there since it's new
    a_float = 5.1
    a_string = "This option is different from the default"  # user setting has precedence

    [other]
    other_1 = "foo"
    # other_2 is gone

    [enterprise]
    modifications = ["confidential_mode"]
    """
    )

    def mock_read_toml(*args):
        return toml.loads(mock_persisted_user_config)

    def mock_read_toml_after_reset(*args):
        return {}

    def mock_unlink(*args):
        pass

    monkeypatch.setattr(bamboolib.config, "read_toml", mock_read_toml)
    monkeypatch.setattr(bamboolib.config, "DEFAULT_CONFIG", mock_default_config)
    monkeypatch.setattr(Path, "unlink", mock_unlink)

    parse_config()

    assert bamboolib.config._config_options == toml.loads(expected_config_options)

    # Check that confidential mode works
    # NOTE: keep that check here or put it in another test case if you don't want to keep it here
    assert is_in_confidential_mode() == True

    monkeypatch.setattr(bamboolib.config, "read_toml", mock_read_toml_after_reset)
    reset_options()

    assert bamboolib.config._config_options == toml.loads(mock_default_config)


# NOTE: Needs to be the last "test" in this file!
# This is not a test. Here, we revert the side effects of the previous tests
def test_revert_side_effects():
    parse_config()
