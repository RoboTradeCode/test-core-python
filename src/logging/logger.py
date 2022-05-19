logging_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': "%(asctime)s:%(name)s:%(process)d:%(lineno)d %(levelname)s %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },

        'simple': {
            'format': "%(message)s",
        },
    },
    'handlers': {

        'stdout': {
            'class': "logging.StreamHandler",
            'level': "DEBUG",
            'formatter': "default",
            'stream': "ext://sys.stdout",
        },

        'logfile': {
            'class': "logging.handlers.RotatingFileHandler",
            'level': "WARNING",
            # файл, в который будут сохраняться логи
            'filename': ".configurator-errors.log",
            'formatter': "default",
            'backupCount': 2,
        },
    },

    'root': {
        'level': "INFO",
        'handlers': ["logfile", "stdout"],
    },
}

