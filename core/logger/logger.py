import logging
from core.logger.log_formatter import CustomFormatter

logger = logging.getLogger("CPCSG")  # Carla Pre Crash Scenario Generator
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


def set_logging_level(level=logging.INFO):
    """Sets the log level for the global logger

    :param level: Log level to set
    :type level: str
    """
    logger.setLevel(level)
    ch.setLevel(level)


def get_plugin_logger(plugin_name, level=logging.INFO):
    """Creates a new logger instance for a plugin

    :param plugin_name: Plugin to create the logger for
    :type plugin_name: str
    :param level: Log level to set
    :type level: str
    :returns: Logger instance
    :rtype: object
    """
    plugin_logger = logging.getLogger(plugin_name)
    plugin_logger.setLevel(level)

    plugin_logger.addHandler(ch)
    return plugin_logger
