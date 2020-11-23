import logging


class Logger:
    default_logger = logging.getLogger('__main__')

    @classmethod
    def set_logger(cls, logger: logging.Logger):
        """Can be used to re-assign default logger used by class"""
        cls.default_logger = logger

    @classmethod
    def log(cls, level: str, log_msg: str, logger: logging.Logger = None):
        """Logging function logging message on certain level and logger (default class logger if not specified)

        :param level: Logging level, needs to be one of ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        :param log_msg: Logging message
        :param logger: Logger instance to be used, class attribute default_logger will be read if no other is specified
        """

        log_func = cls.get_log_func(level, logger)
        log_func(log_msg)

    @classmethod
    def get_log_func(cls, level, logger):
        if logger is None:
            if cls.default_logger is not None:
                logger = cls.default_logger
            else:
                raise AttributeError('No valid logger specified')
        logging_levels = {'DEBUG': logger.debug, 'INFO': logger.info,
                          'WARNING': logger.warning, 'ERROR': logger.error,
                          'CRITICAL': logger.critical}
        try:
            return logging_levels[level.upper()]
        except KeyError:
            raise KeyError(f'Invalid level value "{level}", needs to be one of'
                           f' ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")')

    @classmethod
    def log_decor(cls, level: str, class_name: str = None, log_msg: str = None, logger: logging.Logger = None):
        """Decorator logging function's origin and result with specified logging level

        :param level: Logging level, needs to be one of ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        :param class_name: Name of the class, passed as additional information for logger
        :param log_msg: Logging message, function's call details will be used if log_msg isn't specified
        :param logger: Logger instance to be used, class attribute default_logger will be read if no other is specified
        """

        log_func = cls.get_log_func(level, logger)

        def inner(func):
            def wrapper(*args, **kwargs):
                nonlocal log_msg  # nonlocal log_msg declaration to avoid further unreferenced assignment
                result = func(*args, **kwargs)

                class_origin = f'Class: "{class_name}", ' if class_name else ''
                origin_details = f'Module "{func.__module__}", {class_origin}Function "{func.__name__}"'

                if not log_msg:
                    if func.__name__ == '__init__':
                        result_str = f'Created object: {repr(args[0])}'
                        # using args[0] to get self object, from which we can access repr method
                    else:
                        result_str = f'"{result}"' if type(result) == str else result

                    log_msg = f'called with positional arguments: {args},' \
                              f'\tkeyword arguments: {kwargs}, \t\tresult: {result_str}'

                whole_log_msg = f'{origin_details}\t-\t{log_msg}'
                log_func(whole_log_msg)
                return result

            return wrapper

        return inner
