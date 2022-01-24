from os import linesep
from configparser import ConfigParser
from silx.io.dictdump import dicttoh5, h5todict
from silx.io.url import DataUrl
from ..utils import check_supported, deprecated

#
# option "type":
#  - required: always visible, user must provide a valid value
#  - optional: visible, but might be left blank
#  - advanced: optional and not visible by default
#  - unsupported: hidden (not implemented yet)
_options_levels = {
    "required": 0,
    "optional": 1,
    "advanced": 2,
    "unsupported": 10,
}


class NabuConfigParser:
    @deprecated(
        "The class 'NabuConfigParser' is deprecated and will be removed in a future version. Please use parse_nabu_config_file instead",
        do_print=True
    )
    def __init__(self, fname):
        """
        Nabu configuration file parser.

        Parameters
        ----------
        fname: str
            File name of the configuration file
        """
        parser = ConfigParser(
            inline_comment_prefixes=("#",) # allow in-line comments
        )
        with open(fname) as fid:
            file_content = fid.read()
        parser.read_string(file_content)
        self.parser = parser
        self.get_dict()
        self.file_content = file_content.split(linesep)

    def get_dict(self):
        # Is there an officially supported way to do this ?
        self.conf_dict = self.parser._sections
        return self.conf_dict

    def __str__(self):
        return self.conf_dict.__str__()

    def __repr__(self):
        return self.conf_dict.__repr__()

    def __getitem__(self, key):
        return self.conf_dict[key]


def parse_nabu_config_file(fname):
    """
    Parse a configuration file and returns a dictionary.

    Parameters
    ----------
    fname: str
        File name of the configuration file

    Returns
    -------
    conf_dict: dict
        Dictionary with the configuration
    """
    parser = ConfigParser(
        inline_comment_prefixes=("#",) # allow in-line comments
    )
    with open(fname) as fid:
        file_content = fid.read()
    parser.read_string(file_content)
    conf_dict = parser._sections # Is there an officially supported way to do this ?
    return conf_dict


def generate_nabu_configfile(
    fname, default_config,
    config=None, sections=None, comments=True, options_level=None, prefilled_values=None
):
    """
    Generate a nabu configuration file.

    Parameters
    -----------
    fname: str
        Output file path.
    config: dict
        Configuration to save. If section and / or key missing will store the
        default value
    sections: list of str, optional
        Sections which should be included in the configuration file
    comments: bool, optional
        Whether to include comments in the configuration file
    options_level: str, optional
        Which "level" of options to embed in the file. Can be "required", "optional", "advanced".
        Default is "optional".
    """
    if options_level is None:
        options_level = "optional"
    if prefilled_values is None:
        prefilled_values = {}
    check_supported(options_level, list(_options_levels.keys()), "options_level")
    options_level = _options_levels[options_level]
    if config is None:
        config = {}
    if sections is None:
        sections = default_config.keys()
    with open(fname, "w") as fid:
        for section, section_content in default_config.items():
            if section not in sections:
                continue
            if section != "dataset":
                fid.write("%s%s" % (linesep, linesep))
            fid.write("[%s]%s" % (section, linesep))
            for key, values in section_content.items():
                if options_level < _options_levels[values["type"]]:
                    continue
                if comments and values["help"].strip() != "":
                    for help_line in values["help"].split(linesep):
                        content = "# %s" % (help_line) if help_line.strip() != "" else ""
                        content = content + linesep
                        fid.write(content)
                value = values["default"]
                if section in prefilled_values and key in prefilled_values[section]:
                    value = prefilled_values[section][key]
                if section in config and key in config[section]:
                    value = config[section][key]
                fid.write("%s = %s%s" % (key, value, linesep))


def _extract_nabuconfig_section(section, default_config):
    res = {}
    for key, val in default_config[section].items():
        res[key] = val["default"]
    return res


def _extract_nabuconfig_keyvals(default_config):
    res = {}
    for section in default_config.keys():
        res[section] = _extract_nabuconfig_section(section, default_config)
    return res


def get_default_nabu_config(default_config):
    """
    Return a dictionary with the default nabu configuration.
    """
    return _extract_nabuconfig_keyvals(default_config)


def _handle_modified_key(key, val, section, default_config, renamed_keys):
    if val is not None:
        return key, val, section
    if key in renamed_keys and renamed_keys[key]["section"] == section:
        info = renamed_keys[key]
        print(info["message"])
        print(
            "This is deprecated since version %s and will result in an error in futures versions"
            % (info["since"])
        )
        section = info.get("new_section", section)
        if info["new_name"] == "":
            return None, None, section # deleted key
        val = default_config[section].get(info["new_name"], None)
        return info["new_name"], val, section
    else:
        return key, None, section # unhandled renamed/deleted key


def validate_config(config, default_config, renamed_keys, errors="warn"):
    """
    Validate a configuration dictionary against a "default" configuration dict.

    Parameters
    ----------
    config: dict
        configuration dict to be validated
    default_config: dict
        Reference configuration. Missing keys/sections from 'config' will be updated with
        keys from this dictionary.
    errors: str, optional
        What to do when an unknonw key/section is encountered. Possible actions are:
          - "warn": throw a warning, continue the validation
          - "raise": raise an error and exit
    """

    def error(msg):
        if errors == "raise":
            raise ValueError(msg)
        else:
            print("Error: %s" % msg)

    res_config = {}
    for section, section_content in config.items():
        # Ignore the "other" section
        if section.lower() == "other":
            continue
        if section not in default_config:
            error("Unknown section [%s]" % section)
            continue
        res_config[section] = _extract_nabuconfig_section(section, default_config)
        res_config[section].update(section_content)
        for key, value in res_config[section].items():
            opt = default_config[section].get(key, None)
            key, opt, section_updated = _handle_modified_key(key, opt, section, default_config, renamed_keys)
            if key is None:
                continue # deleted key
            if opt is None:
                error("Unknown option '%s' in section [%s]" % (key, section_updated))
                continue
            validator = default_config[section_updated][key]["validator"]
            if section_updated not in res_config: # missing section - handled later
                continue
            res_config[section_updated][key] = validator(section_updated, key, value)
    # Handle sections missing in config
    for section in (set(default_config.keys()) - set(res_config.keys())):
        res_config[section] = _extract_nabuconfig_section(section, default_config)
        for key, value in res_config[section].items():
            validator = default_config[section][key]["validator"]
            res_config[section][key] = validator(section, key, value)
    return res_config


validate_nabu_config = deprecated(
    "validate_nabu_config is renamed validate_config",
    do_print=True
)(validate_config)


def overwrite_config(conf, overwritten_params):
    """
    Overwrite a (validated) configuration with a new parameters dict.

    Parameters
    ----------
    conf: dict
        Configuration dictionary, usually output from validate_config()
    overwritten_params: dict
        Configuration dictionary with the same layout, containing parameters to overwrite
    """
    overwritten_params = overwritten_params or {}
    for section, params in overwritten_params.items():
        if section not in conf:
            raise ValueError("Unknown section %s" % section)
        current_section = conf[section]
        for key in params.keys():
            if key not in current_section:
                raise ValueError("Unknown parameter '%s' in section '%s'" % (key, section))
            conf[section][key] = overwritten_params[section][key]
    # ---
    return conf
