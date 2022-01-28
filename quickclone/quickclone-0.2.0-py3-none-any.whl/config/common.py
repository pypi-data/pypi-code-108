from pathlib import Path


DEFAULTS_FOLDER: Path = Path(__file__).parent / "defaults"
"""
The path to the default configuration file.
"""


USER_CONFIG_FILE: Path = Path.home() / ".config" / "quickclone.toml"
"""
The path to the user's configuration file.
"""
