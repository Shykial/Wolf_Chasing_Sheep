import logging
import time


def logger(level: str):
    """Decorator logging function result with using specified logging level

    :param level: Logging level, needs to be one of ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    """
    logging_levels = {'DEBUG': logging.debug, 'INFO': logging.info,
                      'WARNING': logging.warning, 'ERROR': logging.error,
                      'CRITICAL': logging.critical}
    try:
        log_func = logging_levels[level.upper()]
    except KeyError:
        raise KeyError(f'Invalid level value "{level}", needs to be one of'
                       f' ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")')

    def inner(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            log_msg = f'Function "{func.__name__}" called with positional arguments: {args},' \
                      f'keyword arguments: {kwargs}, result: {result}'
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


@logger('INFO')
def add_them(x, y):
    # time.sleep(0.2)
    return x + y


@logger('critical')
def mul_them(x, y):
    # time.sleep(0.2)
    return x * y


if __name__ == '__main__':
    # logging.basicConfig(filename='new.log', level=logging.INFO)
    # format_str = '%(asctime)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO)
    add_them(5, 19)
    add_them(9, 38)
    mul_them(5, 17)
