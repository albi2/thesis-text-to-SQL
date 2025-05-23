import logging
import logging.config

# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'info_logger': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'error_logger': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': True
        },
    }
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)