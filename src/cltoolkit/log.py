"""Logging utilities"""
import sys
import logging


LOGGING = """
[loggers]
keys = root, lingpy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_lingpy]
# a level of WARN is equivalent to lingpy's defaults of verbose=False, debug=False
level = INFO
handlers =
qualname = lingpy

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = INFO
formatter = generic

[formatter_generic]
format = %(asctime)s [%(levelname)s] %(message)s
"""

_logger = None


def get_logger(config_dir=None, force_default_config=False, test=False):
    """Get a logger configured according to the lingpy log config file.

    Note: If no logging configuration file exists, it will be created.

    :param config_dir: Directory in which to look for/create the log config file.
    :param force_default_config: Configure the logger using the default config.
    :param test: Force reconfiguration of the logger.
    :return: A logger.
    """
    global _logger
    if _logger is None or force_default_config or test:
        _logger = logging.getLogger('lingpy')
        testing = len(sys.argv) and sys.argv[0].endswith('nosetests')
        if not (force_default_config or test) and testing:  # pragma: no cover
            _logger.setLevel(logging.CRITICAL)
    return _logger


def info(msg, **kw):
    get_logger().info(msg, **kw)


def warning(msg):  # pragma: no cover
    get_logger().warning(msg)


def debug(msg, **kw):  # pragma: no cover
    get_logger().debug(msg, **kw)


def error(msg, **kw):  # pragma: no cover
    get_logger().error(msg, **kw)
