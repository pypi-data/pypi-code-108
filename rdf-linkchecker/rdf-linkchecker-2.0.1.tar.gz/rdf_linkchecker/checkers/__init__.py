CONFIG_DEFAULTS = {
    "connection": {"retries": 1, "timeout": 3},
    # "domains" value should be a string with comma separated urls:
    # "skip": {"domains": "https://missing.tld/,https://someother.tld/"},
    "skip": {"domains": ...},
    # level: "all" | "only-failed" | "none"
    # target: "console" | filename
    "reporting": {"level": "all", "target": "console"},
}
