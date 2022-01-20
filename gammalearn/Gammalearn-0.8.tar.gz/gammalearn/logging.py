import sys

LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'console_info': {
                'class': 'logging.Formatter',
                'format': '[%(levelname)s] - %(message)s'
            },
            'console_debug': {
                'class': 'logging.Formatter',
                'format': '[%(levelname)s] %(name)s - %(message)s'
            },
            'detailed_info': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s [%(levelname)s] - %(message)s'
            },
            'detailed_debug': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)-10s [%(levelname)s] - %(processName)-10s  %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'console_info',
            },
            'null': {'class': 'logging.NullHandler'}
        },
        'loggers': {
            'gammalearn': {
                'handlers': ['console']
            },
            'pytorch_lightning': {
                'handlers': ['console'],
                'level': 'WARNING'
            },
            'pytorch': {
                'handlers': ['console'],
                'level': 'WARNING'
            },
            'ctapipe': {
                'handlers': ['console'],
                'level': 'WARNING',
            },
            'root': {
                'level': 'WARNING',
                'handlers': ['console'],
            }
        }
    }



