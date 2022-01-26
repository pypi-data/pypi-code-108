import configparser


class JeremyConfig:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = configparser.ConfigParser(interpolation=None)
        self.read_config()

    def read_config(self):
        self.config.read(self.filepath)

    def write_config(self):
        with open(self.filepath, 'w') as fp:
            self.config.write(fp)

    def get(self, section, key, boolean=False):
        """Returns the value of the section's key if it exists. Returns none if it doesn't exist."""
        if section in self.config and key in self.config[section]:
            if boolean:
                return self.config.getboolean(section, key)
            return self.config[section][key]
        return None

    def set(self, section, key, value):
        """Sets the value of the section's key."""
        if section not in self.config:
            self.config.add_section(section)
        self.config[section][key] = value
        self.write_config()
