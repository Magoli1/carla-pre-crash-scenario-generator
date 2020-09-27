import logging
from core.logger.LogFormatter import CustomFormatter

logger = logging.getLogger("CPCSG")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

