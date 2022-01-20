"""Configuration validator for the OU Container Builder ContainerConfig.yaml."""
import shlex

from cerberus import Validator
from typing import Union


def multiline_splitter(value: str):
    """Split the value on new-lines.

    :param value: The string value to split
    :type value: str
    :return: The split list
    :rtype: list
    """
    return value.split('\n')


def ensure_list(splitter):
    """Create a coercion function that ensures the value is a list.

    :param splitter: The splitting function to apply to strings
    :type splitter: callable
    :return: The split list or the original value
    :rtype: list
    """
    def coercer(value):
        """Coerce the value into list format."""
        if isinstance(value, str):
            return splitter(value)
        elif isinstance(value, list):
            return value
        else:
            return [value]

    return coercer


def filter_empty_items(value):
    """Filter empty values from the list."""
    return [line for line in value if line.strip()]


schema = {
    'module': {
        'type': 'dict',
        'required': True,
        'schema': {
            'code': {
                'type': 'string',
                'required': True
            },
            'presentation': {
                'type': 'string',
                'required': True
            }
        }
    },
    'type': {
        'type': 'string',
        'required': True,
        'allowed': ['jupyter-notebook', 'web-app']
    },
    'base': {
        'type': 'string',
        'required': False,
        'default': '3.9'
    },
    'content': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'required': True,
            'schema': {
                'source': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'target': {
                    'type': 'string',
                    'default': ''
                },
                'overwrite': {
                    'type': 'string',
                    'required': True,
                    'allowed': ['always', 'never', 'if-unchanged']
                }
            }
        }
    },
    'sources': {
        'type': 'dict',
        'schema': {
            'apt': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                            'required': True,
                            'empty': False
                        },
                        'key': {
                            'type': 'string',
                            'required': True,
                            'empty': False,
                        },
                        'deb': {
                            'type': 'string',
                            'required': True,
                            'empty': False,
                        }
                    }
                }
            }
        }
    },
    'packages': {
        'type': 'dict',
        'schema': {
            'apt': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                }
            },
            'pip': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                }
            }
        }
    },
    'scripts': {
        'type': 'dict',
        'schema': {
            'build': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'commands': {
                            'type': 'list',
                            'schema': {
                                'type': 'string'
                            },
                            'coerce': (ensure_list(multiline_splitter), filter_empty_items)
                        }
                    }
                }
            },
            'startup': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'commands': {
                            'type': 'list',
                            'schema': {
                                'type': 'string'
                            },
                            'coerce': (ensure_list(multiline_splitter), filter_empty_items)
                        }
                    }
                }
            },
            'shutdown': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'commands': {
                            'type': 'list',
                            'schema': {
                                'type': 'string'
                            },
                            'coerce': (ensure_list(multiline_splitter), filter_empty_items)
                        }
                    }
                }
            }
        }
    },
    'jupyter_notebook': {
        'type': 'dict',
        'schema': {
            'default_url': {
                'type': 'string',
                'empty': False
            }
        }
    },
    'web_apps': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'path': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'cmdline': {
                    'type': 'list',
                    'required': True,
                    'empty': False,
                    'schema': {
                        'type': 'string',
                        'required': True,
                        'empty': False
                    },
                    'coerce': (ensure_list(shlex.split), filter_empty_items)
                },
                'port': {
                    'type': 'integer',
                    'default': 0
                },
                'default': {
                    'type': 'boolean',
                    'default': False
                },
                'timeout': {
                    'type': 'integer'
                },
                'absolute_url': {
                    'type': 'boolean',
                    'default': False
                }
            }
        }
    },
    'services': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'empty': False
        }
    },
    'packs': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'allowed': ['tutorial-server', 'mariadb']
        }
    },
    'tutorial_server': {
        'type': 'dict',
        'schema': {
            'parts': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                            'required': True,
                            'empty': False,
                        },
                        'type': {
                            'type': 'string',
                            'required': True,
                            'allowed': ['tutorial', 'workspace', 'live']
                        },
                        'path': {
                            'type': 'string',
                            'required': True
                        }
                    }
                }
            },
            'default': {
                'type': 'string',
                'required': True,
                'empty': False
            },
            'php-cgi': {
                'type': 'boolean',
                'required': False,
                'default': False
            }
        }
    },
    'mariadb': {
        'type': 'dict',
        'schema': {
            'database': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'username': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'password': {
                'type': 'string',
                'required': True,
                'empty': False,
            }
        }
    },
    'hacks': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'required': True,
            'empty': False,
            'allowed': ['missing-man1']
        }
    },
    'flags': {
        'type': 'dict',
        'schema': {
            'ou_container_content': {
                'type': 'boolean',
                'default': False
            }
        }
    }
}


def validate_settings(settings: dict) -> Union[dict, bool]:
    """Validate the configuration settings against the configuration schema.

    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :return: The validated and normalised settings if they are valid, otherwise ``False``
    :rtype: boolean or dict
    """
    validator = Validator(schema)
    if settings and validator.validate(settings):
        return validator.document
    elif settings is None:
        return ['Your configuration file is empty']
    else:
        error_list = []

        def walk_error_tree(err, path):
            if isinstance(err, dict):
                for key, value in err.items():
                    walk_error_tree(value, path + (str(key), ))
            elif isinstance(err, list):
                for sub_err in err:
                    walk_error_tree(sub_err, path)
            else:
                error_list.append(f'{".".join(path)}: {err}')

        walk_error_tree(validator.errors, ())
        return error_list
