import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


class Logger:
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[41m'  # Red background
    }

    def __init__(self, name="WebNovelGPT", log_file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Console handler with colors
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(type('ColorFormatter', (logging.Formatter,), {
            'format': lambda self, record: f"{Logger.COLORS.get(record.levelname, '')}"
                                           f"{logging.Formatter('%(asctime)s - %(levelname)s - %(message)s').format(record)}"
                                           f"\033[0m"
        })())
        self.logger.addHandler(console)

        # File handler
        if log_file:
            Path(log_file).parent.mkdir(exist_ok=True)
            file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            ))
            self.logger.addHandler(file_handler)

    def __getattr__(self, name):
        return getattr(self.logger, name)


logger = Logger(log_file="../logs/webnovel.log")

if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
