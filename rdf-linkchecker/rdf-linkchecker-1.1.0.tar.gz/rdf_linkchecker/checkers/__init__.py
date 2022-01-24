CONFIG_DEFAULTS = {
    "connection": {"retries": 1, "timeout": 10},
    # "domains" value should be a string with comma separated urls:
    # "skip": {"domains": "https://missing.tld/,https://someother.tld/"},
    "skip": {"domains": ...},
}
