import logging
import sys

class LoggingConfig:
    def __init__(self):
        self.logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_logger(self, name: str):
        logger = logging.getLogger(name)
        logger.info = self._log_wrapper(logger.info)
        logger.warning = self._log_wrapper(logger.warning)
        logger.error = self._log_wrapper(logger.error)
        logger.audit_log = self._audit_log_wrapper(logger.info)
        return logger

    def _log_wrapper(self, original_method):
        def wrapper(message, log_type=None, extra_data=None):
            if extra_data:
                message = f"{message} | Extra: {extra_data}"
            original_method(message)
        return wrapper

    def _audit_log_wrapper(self, original_method):
        def wrapper(message, log_type=None, extra_data=None):
            audit_message = f"[AUDIT] {message}"
            if extra_data:
                audit_message = f"{audit_message} | Extra: {extra_data}"
            original_method(audit_message)
        return wrapper

logging_config = LoggingConfig()
