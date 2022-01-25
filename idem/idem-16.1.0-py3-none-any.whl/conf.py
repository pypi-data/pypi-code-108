CLI_CONFIG = {
    # Describe Options
    "desc_glob": {
        "display_priority": 0,
        "positional": True,
        "subcommands": ["describe"],
        "help": "A glob to match the refs that should be ran",
    },
    "progress": {
        "action": "store_true",
        "subcommands": ["describe"],
        "help": "Show a progress bar",
    },
    "hard_fail": {
        "action": "store_true",
        "subcommands": ["describe"],
        "help": "Hard stop the first time an error is raised",
    },
    "filter": {
        "type": str,
        "subcommands": ["describe"],
        "help": "A JMES search path",
    },
    # Exec Options
    "exec_func": {
        "display_priority": 0,
        "positional": True,
        "subcommands": ["exec"],
        "help": "The execution function to run by it's reference on the hub",
    },
    "exec_args": {
        "display_priority": 1,
        "positional": True,
        "nargs": "*",
        "render": "cli",
        "subcommands": ["exec"],
    },
    # State options
    "run_name": {
        "subcommands": ["state"],
    },
    "sls_sources": {"nargs": "*", "subcommands": ["state"]},
    "test": {"options": ["-t"], "action": "store_true", "subcommands": ["state"]},
    "tree": {
        "options": ["-T"],
        "subcommands": ["state"],
    },
    "cache_dir": {"subcommands": ["state"]},
    "root_dir": {"subcommands": ["state"]},
    "render": {
        "subcommands": ["state"],
    },
    "runtime": {
        "subcommands": ["state"],
    },
    "reconciler": {
        "options": ["-r", "-R"],
        "subcommands": ["state"],
    },
    "pending": {
        "options": ["-p", "-P"],
        "subcommands": ["state"],
    },
    "output": {
        "source": "rend",
        "subcommands": ["exec", "state", "describe", "decrypt"],
    },
    "sls": {"positional": True, "nargs": "*", "subcommands": ["state"]},
    # ACCT options
    "input_file": {
        "source": "acct",
        "positional": True,
        "subcommands": ["encrypt", "decrypt"],
    },
    "output_file": {
        "subcommands": ["encrypt"],
        "source": "acct",
    },
    "acct_file": {
        "source": "acct",
        "os": "ACCT_FILE",
        "subcommands": ["state", "exec", "describe"],
    },
    "acct_key": {
        "source": "acct",
        "os": "ACCT_KEY",
        "subcommands": ["state", "exec", "describe", "encrypt", "decrypt"],
    },
    "acct_profile": {
        "os": "ACCT_PROFILE",
        "subcommands": ["state", "exec", "describe"],
    },
    "crypto_plugin": {
        "source": "acct",
        "subcommands": ["encrypt", "decrypt"],
    },
    # EVBUS options
    "serialize_plugin": {
        "source": "evbus",
        "subcommands": ["exec", "describe", "state"],
    },
}

CONFIG = {
    "run_name": {
        "default": "cli",
        "help": "A unique ID to assign to this run",
    },
    "sls_sources": {
        "default": [],
        "help": "list off the sources that should be used for gathering sls files and data",
    },
    "test": {
        "default": False,
        "help": "Set the idem run to execute in test mode. No changes will be made, idem will only detect if changes will be made in a real run.",
    },
    "tree": {
        "default": "",
        "help": "The directory containing sls files",
    },
    "cache_dir": {
        "default": "/var/cache/idem",
        "help": "The location to use for the cache directory",
    },
    "root_dir": {
        "default": "/",
        "help": 'The root directory to run idem from. By default it will be "/", or in the case of running as non-root it is set to <HOMEDIR>/.idem',
    },
    "render": {
        "default": "jinja|yaml",
        "help": "The render pipe to use, this allows for the language to be specified",
    },
    "runtime": {
        "default": "parallel",
        "help": "Select which execution runtime to use",
    },
    "sls": {
        "default": [],
        "help": "A space delimited list of sls refs to execute",
    },
    "exec": {
        "default": "",
        "help": "The name of an execution function to execute",
    },
    "exec_args": {
        "default": [],
        "help": "Arguments to pass to the named execution function",
    },
    "acct_profile": {
        "os": "ACCT_PROFILE",
        "help": "The profile to use when when calling exec modules and states",
        "default": "default",
    },
    "reconciler": {
        "default": "none",
        "help": "The reconciler plugin to use, 'none' by default",
    },
    "pending": {
        "default": "default",
        "help": "The pending plugin to use within the reconciler, 'default' by default",
    },
}
SUBCOMMANDS = {
    "encrypt": {
        "desc": "Use the acct subsystem to encrypt data",
        "help": "Use the acct subsystem to encrypt data",
        "source": "acct",
    },
    "decrypt": {
        "desc": "Use the acct subsystem to decrypt data",
        "help": "Use the acct subsystem to decrypt data",
        "source": "acct",
    },
    "state": {
        "desc": "Execute a specific state file or reference",
        "help": "Commands to run idempotent states",
    },
    "exec": {
        "desc": "Execute a specific execution routine",
        "help": "Commands to run execution routines",
    },
    "describe": {
        "desc": "Get an SLS representation of the account",
        "help": "Commands to run description routines",
    },
}
DYNE = {
    "idem": ["idem"],
    "exec": ["exec"],
    "states": ["states"],
    "tool": ["tool"],
    "output": ["output"],
    "reconcile": ["reconcile"],
}
