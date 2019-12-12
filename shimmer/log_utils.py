import logging

from functools import update_wrapper


def log_exceptions(logger: logging.Logger):
    def outer(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)

        wrapped = update_wrapper(wrapper, func)
        return wrapped

    return outer
