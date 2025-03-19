# Code by AkinoAlice@TyrantRey

import logging


class Logger:
    """Logger class to handle logging."""

    def __init__(
        self,
        filename: str,
        fmt: str = "%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    ) -> None:
        """Initialize Logger with filename and format."""
        self.logger = logging.getLogger(__name__)
        self.handler = logging.StreamHandler()

        logging.basicConfig(filename=filename, filemode="w+", encoding="utf-8", level=logging.DEBUG)

        self.formatter = logging.Formatter(fmt)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

