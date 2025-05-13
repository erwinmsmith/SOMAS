from functools import wraps
import traceback
from .logger import Logger

logger = Logger(__name__).get_logger()

def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            # 可根据需要返回默认值或重新抛出异常
            return None
    return wrapper