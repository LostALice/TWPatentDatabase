# Code by AkinoAlice@TyrantRey

from pprint import pformat
from typing import Any

import inspect
import logging


class Logger(object):
    def __init__(
        self,
        logger_name: str,
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self.handler = logging.StreamHandler()

        # costume logging formats
        self.fmt = "%(asctime)s - %(currentFuncName)s:%(currentFuncLine)d - %(levelname)s: %(message)s"
        self.factory = logging.getLogRecordFactory()
        self.costumed_log_record = self.record_factory
        logging.setLogRecordFactory(self.costumed_log_record)

        logging.basicConfig(
            filename="./logger.log",
            filemode="w+",
            encoding="utf-8",
            level=logging.DEBUG,
            format=self.fmt,
        )

        self.logger.addHandler(self.handler)

    def record_factory(self, *args, **kwargs) -> logging.LogRecord:
        record = self.factory(*args, **kwargs)
        record.currentFuncName = inspect.stack()[-2].filename.split("\\")[-1]
        record.currentFuncLine = inspect.stack()[-2].lineno
        return record

    def set_module_level(self, module_name: str, level: int | str) -> None:
        logging.getLogger(module_name).setLevel(level)

    def debug(self, message: Any, format_json: bool = False) -> None:
        if format_json:
            self.logger.debug(pformat(message, indent=4))
        else:
            self.logger.debug(message)

    def info(self, message: Any, format_json: bool = False) -> None:
        if format_json:
            self.logger.info(pformat(message, indent=4))
        else:
            self.logger.info(message)

    def warning(self, message: Any, format_json: bool = False) -> None:
        if format_json:
            self.logger.warning(pformat(message, indent=4))
        else:
            self.logger.warning(message)

    def error(self, message: Any, format_json: bool = False) -> None:
        if format_json:
            self.logger.error(pformat(message, indent=4))
        else:
            self.logger.error(message)

    def critical(self, message: Any, format_json: bool = False) -> None:
        if format_json:
            self.logger.critical(pformat(message, indent=4))
        else:
            self.logger.critical(message)

    def log(self, level: str, message: Any) -> None:
        if level.capitalize == "DEBUG":
            self.logger.debug(message)

        if level.capitalize == "INFO":
            self.logger.info(message)

        if level.capitalize == "WARNING":
            self.logger.warning(message)

        if level.capitalize == "ERROR":
            self.logger.error(message)

        if level.capitalize == "CRITICAL":
            self.logger.critical(message)

    def log_json(self, level: str, message: Any) -> None:
        if level.capitalize == "DEBUG":
            self.logger.debug(pformat(message, indent=4))

        if level.capitalize == "INFO":
            self.logger.info(pformat(message, indent=4))

        if level.capitalize == "WARNING":
            self.logger.warning(pformat(message, indent=4))

        if level.capitalize == "ERROR":
            self.logger.error(pformat(message, indent=4))

        if level.capitalize == "CRITICAL":
            self.logger.critical(pformat(message, indent=4))


# testing
if __name__ == "__main__":
    logger = Logger("./test.log")

    logger.debug("Testing debug")
    logger.info("Testing info")
    logger.warning("Testing warning")
    logger.error("Testing error")
    logger.critical("Testing critical")

    logger.debug("Testing debug", True)
    logger.info("Testing info", True)
    logger.warning("Testing warning", True)
    logger.error("Testing error", True)
    logger.critical("Testing critical", True)
