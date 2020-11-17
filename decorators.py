import logging
import time


class Logger:
    default_logger = logging.getLogger('__main__')

    @classmethod
    def set_logger(cls, logger: logging.Logger):
        """Can be used to re-assign default logger used by class"""
        cls.default_logger = logger

    @classmethod
    def log(cls, level: str, class_name: str = None, logger: logging.Logger = None):
        """Decorator logging function result with using specified logging level

        :param logger: Logger instance to be used, class attribute default_logger will be read if no other is specified
        :param level: Logging level, needs to be one of ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        :param class_name: Name of the class, passed as additional information for logger
        """
        if logger is None:
            if cls.default_logger is not None:
                logger = cls.default_logger
            else:
                raise AttributeError('No valid logger specified')

        logging_levels = {'DEBUG': logger.debug, 'INFO': logger.info,
                          'WARNING': logger.warning, 'ERROR': logger.error,
                          'CRITICAL': logger.critical}
        try:
            log_func = logging_levels[level.upper()]
        except KeyError:
            raise KeyError(f'Invalid level value "{level}", needs to be one of'
                           f' ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")')

        def inner(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if func.__name__ == '__init__':
                    result_str = f'Created object: {repr(args[0])}'
                    # using args[0] to get self object, from which we can access repr method
                else:
                    result_str = f'"{result}"' if type(result) == str else result

                class_origin = f'Class: "{class_name}", ' if class_name else ''
                origin_details = f'Module "{func.__module__}", {class_origin}Function "{func.__name__}"'
                log_msg = f'{origin_details}\t-\tcalled with positional arguments: {args},' \
                          f'\tkeyword arguments: {kwargs}, result: {result_str}'
                log_func(log_msg)
                return result

            return wrapper

        return inner


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f'Function "{func.__name__}" took {time.time() - start_time} to execute')
        return result

    return wrapper
