import logging
from core.logger.log_formatter import CustomFormatter

logger = logging.getLogger("CPCSG")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


def set_logging_level(level=logging.INFO):
    """Sets the log level for the global logger

    :param level: Log level to set
    :type level: str
    """
    logger.setLevel(level)


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

    channel = logging.StreamHandler()
    channel.setLevel(level)

    channel.setFormatter(CustomFormatter())

    plugin_logger.addHandler(channel)
    return plugin_logger
