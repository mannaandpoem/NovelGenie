import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[41m",  # 红色背景
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        reset = "\033[0m"
        formatted_message = super().format(record)
        return f"{color}{formatted_message}{reset}"


class Logger:
    def __init__(self, name="WebNovelGPT", log_file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # 控制台处理器，带颜色
        console = logging.StreamHandler(sys.stdout)
        color_formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
        console.setFormatter(color_formatter)
        self.logger.addHandler(console)

        # 文件处理器
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            file_formatter = logging.Formatter(
                (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(filename)s:%(lineno)d - %(message)s"
                )
            )
            file_handler.setFormatter(file_formatter)
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
