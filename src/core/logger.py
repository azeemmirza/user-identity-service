import logging
from typing import Final

# Usage:
#     from src.core.logger import logger
#     logger.debug('debug message')
#     logger.info('informational message')
#     logger.warning('something unexpected happened')
#     logger.error('an error occurred')
#     logger.exception('error with stack trace')
logger: Final[logging.Logger] = logging.getLogger('user_identity_service')