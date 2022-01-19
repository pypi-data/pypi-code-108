import os
import re
from pathlib import Path
from configparser import ConfigParser


class FeaturestoreConfig:
    """Feature Store Config.

    Reads configuration from `~/.continual/.credentials` or `CONTINUAL_FS_CREDENTIALS` if
    not set during initialization.  Priority of config variables is `__init__`,
    environmental variables, and then the configuration file.

    Environmental variables are:

    * `CONTINUAL_FS_CREDENTIALS` - Credentials file.
    """

    _fsconfigfile: str

    _cp: ConfigParser

    def __init__(self) -> None:
        """Initialize featurestore config."""
        self._fsconfigfile = os.environ.get(
            "CONTINUAL_FS_CREDENTIALS",
            os.path.join(Path.home(), ".continual", ".credentials"),
        )

        Path(os.path.dirname(self._fsconfigfile)).mkdir(parents=True, exist_ok=True)

        if not Path(self._fsconfigfile).exists():
            Path(self._fsconfigfile).touch()

        self._cp = ConfigParser()
        self._cp.optionxform = str
        self._cp.read([self._fsconfigfile])

    def list(self, details=False, unmask=False):
        """Prints all featurestore config."""
        print("Reading File: %s" % self._fsconfigfile)
        if details:
            with open(self._fsconfigfile, "r") as f:
                text = f.read()
                if not unmask:
                    text = re.sub(
                        "(password\\s*=\\s*.+)",
                        "PASSWORD = XXXXXXXXXXXXXXXXXXX",
                        text,
                        flags=re.IGNORECASE,
                    )
                print(text)
                f.close()
        else:
            print("Sections: ")
            for s in self._cp.sections():
                print(s)

    def get(self, name):
        """Prints a single featurestore config."""
        print("[%s]" % name)
        for key in self._cp[name].keys():
            if key.lower() == "password":
                val = "XXXXXXXXXXXXXXXXXXX"
            else:
                val = self._cp[name][key]
            print("%s = %s" % (key, val))

    def create(self, name, dict):
        """Creates featurestore config"""
        # force keys to be lowercase
        dict = {k.lower(): v for k, v in dict.items()}
        self._cp[name] = dict

        with open(self._fsconfigfile, "w") as f:
            self._cp.write(f)

    def delete(self, name):
        """Deletes featurestore config."""
        self._cp.remove_section(name)
        with open(self._fsconfigfile, "w") as f:
            self._cp.write(f)

    def update(self, name, key, value):
        """Updates value in featurestore config."""
        if not self._cp.has_section(name):
            self._cp.add_section(name)
        self._cp[name][key.lower()] = value
        with open(self._fsconfigfile, "w") as f:
            self._cp.write(f)
