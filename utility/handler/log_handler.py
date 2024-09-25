# Code by AkinoAlice@TyrantRey

from json import dumps
import logging


class Logger(object):

    def __init__(
        self,
        filename: str,
        fmt: str = "%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    ) -> None:
        self.logger = logging.getLogger(filename)
        self.handler = logging.StreamHandler()

        formatter = logging.Formatter(fmt)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def debug(self, message: str, format_json: bool = False) -> None:
        if format_json:
            self.logger.debug(dumps(message, indent=4))
        else:
            self.logger.debug(message)

    def info(self, message: str, format_json: bool = False) -> None:
        if format_json:
            self.logger.info(dumps(message, indent=4))
        else:
            self.logger.info(message)

    def warning(self, message: str, format_json: bool = False) -> None:
        if format_json:
            self.logger.warning(dumps(message, indent=4))
        else:
            self.logger.warning(message)

    def error(self, message: str, format_json: bool = False) -> None:
        if format_json:
            self.logger.error(dumps(message, indent=4))
        else:
            self.logger.error(message)

    def critical(self, message: str, format_json: bool = False) -> None:
        if format_json:
            self.logger.critical(dumps(message, indent=4))
        else:
            self.logger.critical(message)

    def log(self, level: str, message: str) -> None:
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

    def log_json(self, level: str, message: str) -> None:
        if level.capitalize == "DEBUG":
            self.logger.debug(dumps(message, indent=4))

        if level.capitalize == "INFO":
            self.logger.info(dumps(message, indent=4))

        if level.capitalize == "WARNING":
            self.logger.warning(dumps(message, indent=4))

        if level.capitalize == "ERROR":
            self.logger.error(dumps(message, indent=4))

        if level.capitalize == "CRITICAL":
            self.logger.critical(dumps(message, indent=4))
