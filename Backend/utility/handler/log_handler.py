# Code by AkinoAlice@TyrantRey

import logging
from pathlib import Path
from typing import Literal


class Logger:
    """Global Logger class to handle logging across multiple files."""

    _instance = None

    def __new__(cls, *args, **kwargs):  # noqa: ARG004
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # noqa: SLF001
        return cls._instance

    def __init__(
        self,
        log_dir: str = "./logs",
        log_filename: str = __file__,
        fmt: str = "%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s: %(message)s",
        level: int = logging.DEBUG,
    ) -> None:
        """
        Initialize Logger with log directory and format.

        Args:
            log_dir: Directory path for log files
            log_filename: Optional specific log filename (default: auto-generated timestamped name)
            fmt: Log format string
            level: Logging level

        """
        if self._initialized:  # type: ignore[has-type]
            return

        log_path = Path(log_dir)

        if not Path(log_path).exists():
            Path(log_path).mkdir(parents=True)

        file_path = log_path / "Event.log"

        self.logger = logging.getLogger("global_logger")
        self.logger.setLevel(level)
        self.logger.info("Log file in %s", log_dir)

        if self.logger.handlers:
            self.logger.handlers.clear()

        file_handler = logging.FileHandler(file_path, mode="w+", encoding="utf-8")
        file_handler.setLevel(level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter(fmt)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self._initialized = True

    def block_module(self, module_name: str) -> None:
        """Block some of module"""
        logging.getLogger(module_name).propagate = False

    def module_log_level(self, module_name: str, level: Literal[0, 10, 20, 30, 40, 50]) -> None:
        logging.getLogger(module_name).setLevel(level)

    def get_logger(self):
        """Return the configured logger."""
        return self.logger

    def debug(self, msg, *args, **kwargs) -> None:
        kwargs.setdefault("stacklevel", 2)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        kwargs.setdefault("stacklevel", 2)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        kwargs.setdefault("stacklevel", 2)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        kwargs.setdefault("stacklevel", 2)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs) -> None:
        kwargs.setdefault("stacklevel", 2)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs) -> None:
        kwargs.setdefault("stacklevel", 2)
        self.logger.exception(msg, *args, **kwargs)
